"""
Progress monitoring utilities for CLI and other clients.
"""

import asyncio
from typing import Optional, Any
import aiohttp
from aiohttp import ClientTimeout
import websockets
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.console import Console
from rich.table import Table
import json

from acolyte.core.logging import logger


class ProgressMonitor:
    """
    Unified progress monitoring with WebSocket + HTTP fallback.
    Provides a clean interface for CLI and other clients.
    """

    def __init__(self, backend_port: int, console: Optional[Console] = None):
        self.backend_port = backend_port
        self.console = console or Console()
        self.websocket_retries = 3
        self.websocket_timeout = 10  # Volver al valor original
        self.polling_interval = 2

    async def monitor_task(self, task_id: str, total_files: int = 0, verbose: bool = False) -> dict:
        """
        Monitor a task with automatic WebSocket/HTTP fallback.
        Returns final statistics.
        """
        # Try to get initial status
        initial_status = await self._get_initial_status(task_id)
        if initial_status:
            total_files = initial_status.get('total', total_files)
            self.console.print(
                f"[green]✓[/green] Task found: {initial_status.get('message', 'Starting...')}"
            )

        # Set up progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("{task.fields[status]}"),
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:

            task = progress.add_task(
                "[cyan]Connecting to progress monitor...",
                total=total_files or 100,
                status="Starting...",
            )

            # Try WebSocket first
            final_stats = await self._try_websocket_monitoring(task_id, progress, task, verbose)

            # If WebSocket failed, use HTTP polling
            if not final_stats:
                progress.update(
                    task, description="[yellow]⚠ WebSocket unavailable, using HTTP polling[/yellow]"
                )
                final_stats = await self._http_polling_fallback(task_id, progress, task, verbose)

            return final_stats or {}

    async def _get_initial_status(self, task_id: str) -> Optional[dict]:
        """Get initial task status via HTTP."""
        url = f"http://localhost:{self.backend_port}/api/index/project/status/{task_id}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=ClientTimeout(total=2)) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            logger.debug("Failed to get initial status", task_id=task_id, error=str(e))

        return None

    async def _try_websocket_monitoring(
        self, task_id: str, progress: Progress, task: Any, verbose: bool
    ) -> Optional[dict]:
        """Try to monitor via WebSocket with retries."""
        ws_url = f"ws://localhost:{self.backend_port}/api/ws/progress/{task_id}"

        for attempt in range(self.websocket_retries):
            try:
                websocket = await asyncio.wait_for(
                    websockets.connect(ws_url), timeout=self.websocket_timeout
                )

                progress.update(task, description="[green]Connected! Receiving updates...[/green]")

                # Handle WebSocket messages
                return await self._handle_websocket_messages(websocket, progress, task, verbose)

            except (
                asyncio.TimeoutError,
                websockets.ConnectionClosedError,
                websockets.WebSocketException,
            ) as e:
                if attempt < self.websocket_retries - 1:
                    progress.update(
                        task,
                        description=f"[yellow]Connection failed, retrying... (attempt {attempt + 2}/{self.websocket_retries})[/yellow]",
                    )
                    # Exponential backoff con jitter para evitar thundering herd
                    backoff_delay = min(2**attempt + (attempt * 0.1), 10)
                    await asyncio.sleep(backoff_delay)
                else:
                    logger.debug(
                        "WebSocket connection failed", attempts=self.websocket_retries, error=str(e)
                    )
                    # Mostrar mensaje más claro sobre el fallback
                    progress.update(
                        task,
                        description="[yellow]⚠ Connection failed, switching to HTTP polling[/yellow]",
                    )

        return None

    async def _handle_websocket_messages(
        self, websocket, progress: Progress, task: Any, verbose: bool
    ) -> dict:
        """Handle incoming WebSocket messages."""
        stats = {"chunks_created": 0, "embeddings_generated": 0, "files_skipped": 0, "errors": 0}

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)

                    if data.get('type') == 'progress':
                        # Update progress bar
                        current = data.get('current', 0)
                        total = data.get('total', 100)
                        current_file = data.get('current_file', data.get('message', ''))
                        phase = data.get('phase', 'indexing')
                        stats_data = data.get('stats', {})

                        # Update stats
                        if 'stats' in data:
                            stats['chunks_created'] = stats_data.get('chunks_created', 0)
                            stats['embeddings_generated'] = stats_data.get(
                                'embeddings_generated', 0
                            )
                            stats['files_skipped'] = stats_data.get('files_skipped', 0)
                            stats['errors'] = stats_data.get('errors', 0)

                        # Build status message based on phase
                        if phase == 'discovering':
                            # During discovery phase
                            metadata = data.get('metadata', {})
                            files_found = metadata.get('files_found', 0)
                            folders_scanned = metadata.get('folders_scanned', 0)
                            total_folders = metadata.get('total_folders', '?')
                            status_message = f"🔍 Scanning folders ({folders_scanned}/{total_folders}) - {files_found} files found"
                        elif phase == 'discovery_complete':
                            status_message = f"✅ Discovery complete - {total} files ready"
                        else:
                            # During indexing phase - show file info
                            if current_file and '/' in current_file:
                                filename = current_file.split('/')[-1]
                            elif current_file and '\\' in current_file:
                                filename = current_file.split('\\')[-1]
                            else:
                                filename = current_file

                            # Show as "File X/Y: filename"
                            if current > 0 and total > 0:
                                status_message = f"File {current}/{total}: {filename}"
                            else:
                                status_message = (
                                    filename[:50] + "..." if len(filename) > 50 else filename
                                )

                        # Detect batch information in the metadata
                        batch_info = ""
                        metadata = data.get('metadata', {})
                        if 'batch_num' in metadata:
                            batch_num = metadata.get('batch_num')
                            total_batches = metadata.get('total_batches', '?')
                            batch_status = metadata.get('batch_status', '')

                            if batch_num:
                                batch_info = f" [Batch {batch_num}/{total_batches}]"
                                if batch_status == "paused":
                                    batch_info += " ⏸️ PAUSADO"
                                elif batch_status == "completed":
                                    batch_info += " ✅"

                        # Add ETA if available
                        eta_info = ""
                        if 'estimated_remaining_seconds' in metadata:
                            eta_seconds = metadata.get('estimated_remaining_seconds', 0)
                            if eta_seconds and eta_seconds > 0:
                                eta_minutes = round(eta_seconds / 60, 1)
                                eta_info = f" (ETA: {eta_minutes}min)"

                        # Combine all information for display
                        enhanced_status = f"{status_message}{batch_info}{eta_info}"

                        # Update progress with phase-aware description
                        if phase == 'discovering':
                            description = "[cyan]🔍 Discovering files...[/cyan]"
                        elif phase == 'discovery_complete':
                            description = "[green]✅ Starting indexing...[/green]"
                        else:
                            description = "[cyan]📊 Indexing files...[/cyan]"

                        # Update progress
                        progress.update(
                            task,
                            completed=current,
                            total=total,
                            description=description,
                            status=enhanced_status,
                        )

                        # Enhanced verbose output for Phase 3
                        if verbose and current % 10 == 0:
                            batch_summary = ""
                            if batch_info:
                                batch_summary = f" | {batch_info.strip()}"

                            self.console.print(
                                f"[dim]Chunks: {stats['chunks_created']} | "
                                f"Embeddings: {stats['embeddings_generated']} | "
                                f"Skipped: {stats['files_skipped']} | "
                                f"Errors: {stats['errors']}{batch_summary}[/dim]"
                            )

                        # Check if complete
                        if current >= total:
                            progress.update(task, completed=total)
                            break

                    elif data.get('type') == 'complete':
                        # Final stats from server
                        final_stats = data.get('final_stats', {})
                        stats.update(final_stats)
                        progress.update(task, completed=task.total)
                        break

                    elif data.get('type') == 'error':
                        self.console.print(
                            f"[red]Error: {data.get('message', 'Unknown error')}[/red]"
                        )

                except json.JSONDecodeError:
                    pass  # Ignore non-JSON messages (ping/pong)
                except Exception as e:
                    # THREADING FIX: Manejar errores de manera thread-safe
                    if verbose:
                        try:
                            self.console.print(f"[yellow]Warning: {e}[/yellow]")
                        except Exception:
                            # Si la consola falla, solo loggear
                            logger.debug("Console print failed", error=str(e))
                    # Continuar procesando otros mensajes
                    continue

        finally:
            # THREADING FIX: Cierre graceful del WebSocket
            try:
                await websocket.close()
            except Exception as e:
                logger.debug("Error closing WebSocket", error=str(e))
                # No fallar si el cierre falla

        return stats

    async def _http_polling_fallback(
        self, task_id: str, progress: Progress, task: Any, verbose: bool
    ) -> dict:
        """Fallback to HTTP polling if WebSocket fails."""
        url = f"http://localhost:{self.backend_port}/api/index/project/status/{task_id}"
        stats = {}

        # Mostrar que estamos usando HTTP polling
        progress.update(
            task,
            description="[cyan]📡 Using HTTP polling for progress updates[/cyan]",
        )

        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.get(url, timeout=ClientTimeout(total=2)) as resp:
                        if resp.status == 200:
                            data = await resp.json()

                            # Update progress
                            current = data.get('current', 0)
                            total = data.get('total', 100)
                            message = data.get('message', 'Processing...')

                            # Update progress
                            progress.update(
                                task,
                                completed=current,
                                total=total,
                                description="[cyan]Indexing files...[/cyan]",
                                status=message[:50] + "..." if len(message) > 50 else message,
                            )

                            # Update stats
                            if 'stats' in data:
                                stats = data['stats']

                            # Check if complete
                            status = data.get('status', '')
                            if status in ['completed', 'failed', 'cancelled']:
                                if status == 'completed':
                                    progress.update(task, completed=total)
                                break

                        elif resp.status == 404:
                            progress.update(
                                task,
                                description="[red]❌ Task not found - indexing may have completed[/red]",
                            )
                            break

                except Exception as e:
                    if verbose:
                        try:
                            self.console.print(f"[yellow]Polling error: {e}[/yellow]")
                        except Exception:
                            logger.debug("Console print failed during polling", error=str(e))

                    # Continuar polling incluso si hay errores temporales
                    await asyncio.sleep(self.polling_interval)

        # Mostrar mensaje de finalización
        progress.update(
            task,
            description="[green]✅ Indexing completed (HTTP polling)[/green]",
        )

        return stats

    def display_final_stats(self, stats: dict, elapsed_time: float):
        """Display final statistics in a nice table."""
        if not stats:
            return

        self.console.print("\n[bold green]✓ Indexing completed![/bold green]")

        table = Table(title="Indexing Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        # Add rows
        if 'files_processed' in stats:
            table.add_row("Files Processed", str(stats.get('files_processed', 0)))
        if 'files_skipped' in stats:
            table.add_row("Files Skipped", str(stats['files_skipped']))
        if 'chunks_created' in stats:
            table.add_row("Chunks Created", str(stats['chunks_created']))
        if 'embeddings_generated' in stats:
            table.add_row("Embeddings Generated", str(stats['embeddings_generated']))

        # Time metrics
        table.add_row("Total Time", f"{elapsed_time:.1f}s")

        if stats.get('files_processed', 0) > 0:
            files_per_sec = stats['files_processed'] / elapsed_time
            table.add_row("Files/Second", f"{files_per_sec:.1f}")

        # Errors
        if stats.get('errors', 0) > 0:
            table.add_row("Errors", f"[red]{stats['errors']}[/red]")

        self.console.print(table)

        if stats.get('errors', 0) > 0:
            self.console.print(
                "\n[yellow]⚠ Some files had errors. Check logs for details.[/yellow]"
            )
