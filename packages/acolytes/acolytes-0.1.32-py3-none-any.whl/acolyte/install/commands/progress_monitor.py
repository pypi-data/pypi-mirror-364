"""Progress monitoring for indexing."""

import asyncio
import os

from rich.console import Console
from rich.table import Table

from acolyte.core.progress import ProgressMonitor


async def monitor_indexing_progress(
    backend_port: int, websocket_path: str, task_id: str, total_files: int, verbose: bool = False
):
    """Monitor indexing progress via WebSocket with Rich progress bar."""
    console = Console()

    try:
        # Usar el monitor unificado directamente sin layouts ni Live adicionales
        monitor = ProgressMonitor(backend_port, console)

        # Dar tiempo al backend para que empiece a publicar eventos
        await asyncio.sleep(0.5)

        # Monitorear la tarea
        final_stats = await monitor.monitor_task(
            task_id=task_id, total_files=total_files, verbose=verbose
        )

        # Mostrar estadísticas finales si las hay
        if final_stats:
            console.print("\n[bold green]✓ Indexing completed successfully![/bold green]")

            # Mostrar tabla de estadísticas
            if final_stats.get('files_processed', 0) > 0 or verbose:
                # La tabla ya está importada arriba, reutilizarla
                table = Table(title="Indexing Statistics")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")

                table.add_row("Files Processed", str(final_stats.get('files_processed', 0)))
                table.add_row("Chunks Created", str(final_stats.get('chunks_created', 0)))
                table.add_row(
                    "Embeddings Generated", str(final_stats.get('embeddings_generated', 0))
                )
                table.add_row("Files Skipped", str(final_stats.get('files_skipped', 0)))

                if final_stats.get('errors', 0) > 0:
                    table.add_row("Errors", f"[red]{final_stats['errors']}[/red]")

                console.print(table)

                if final_stats.get('errors', 0) > 0:
                    console.print(
                        "\n[yellow]⚠ Some files had errors. Check logs for details.[/yellow]"
                    )
        else:
            console.print("[red]✗[/red] Progress monitoring failed")
            console.print("[yellow]⚠[/yellow] Indexing continues in background")
            console.print("Check logs with: [bold]acolyte logs[/bold]")

    except KeyboardInterrupt:
        console.print(
            "\n[yellow]Progress monitoring cancelled. Indexing continues in background.[/yellow]"
        )
    except Exception as e:
        console.print(f"[red]Error monitoring progress: {e}[/red]")
        if os.environ.get('ACOLYTE_DEBUG'):
            import traceback

            traceback.print_exc()


async def monitor_indexing_progress_legacy(
    backend_port: int, websocket_path: str, task_id: str, total_files: int, verbose: bool = False
):
    """Legacy monitor - kept for reference."""
    # Lazy imports
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.console import Console
    import websockets
    import json

    console = Console()

    # WebSocket URL - using urllib.parse for safe URL construction
    from urllib.parse import urlunparse

    ws_url = urlunparse(('ws', f"localhost:{backend_port}", websocket_path, '', '', ''))

    try:
        # First try WebSocket
        import asyncio

        websocket = await asyncio.wait_for(websockets.connect(ws_url), timeout=5)
        try:
            console.print("[green]✓[/green] Connected to progress monitor")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TextColumn("•"),
                TextColumn("{task.fields[current_file]}"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:

                main_task = progress.add_task(
                    "[cyan]Indexing files...", total=total_files or 100, current_file="Starting..."
                )

                # Statistics tracking
                stats = {
                    "chunks_created": 0,
                    "embeddings_generated": 0,
                    "files_skipped": 0,
                    "errors": 0,
                }

                async for message in websocket:
                    try:
                        data = json.loads(message)

                        # Handle different message types
                        if data.get('type') == 'progress':
                            # Update progress bar
                            current = data.get('current', 0)
                            total = data.get('total', total_files)
                            current_file = data.get('current_file', data.get('message', ''))

                            # Update statistics if available
                            if 'chunks_created' in data:
                                stats['chunks_created'] = data['chunks_created']
                            if 'embeddings_generated' in data:
                                stats['embeddings_generated'] = data['embeddings_generated']
                            if 'files_skipped' in data:
                                stats['files_skipped'] = data['files_skipped']
                            if 'errors' in data:
                                stats['errors'] = data['errors']

                            progress.update(
                                main_task, completed=current, total=total, current_file=current_file
                            )

                            # Show detailed stats if verbose
                            if verbose:
                                # Extract phase from data
                                phase = data.get('phase', 'indexing')
                                metadata = data.get('metadata', {})

                                # Show phase-specific info
                                if phase == 'discovering' and metadata:
                                    folders_scanned = metadata.get('folders_scanned', 0)
                                    total_folders = metadata.get('total_folders', '?')
                                    files_found = metadata.get('files_found', 0)
                                    console.print(
                                        f"[dim]🔍 Discovering: Folders {folders_scanned}/{total_folders} | "
                                        f"Files found: {files_found}[/dim]"
                                    )
                                elif current % 10 == 0:  # Every 10 files during indexing
                                    console.print(
                                        f"[dim]Chunks: {stats['chunks_created']} | "
                                        f"Embeddings: {stats['embeddings_generated']} | "
                                        f"Skipped: {stats['files_skipped']} | "
                                        f"Errors: {stats['errors']}[/dim]"
                                    )

                            # Check if complete
                            if current >= total:
                                progress.update(main_task, completed=total)
                                break

                        elif data.get('type') == 'error':
                            console.print(
                                f"[red]Error: {data.get('message', 'Unknown error')}[/red]"
                            )

                        elif data.get('type') == 'complete':
                            progress.update(main_task, completed=total_files)
                            break

                    except json.JSONDecodeError:
                        # Handle non-JSON messages (like ping/pong)
                        pass
                    except Exception as e:
                        if verbose:
                            console.print(f"[yellow]Warning: {e}[/yellow]")

            # Final statistics
            console.print("\n[bold green]✓ Indexing completed![/bold green]")

            # Show final stats table
            if stats['chunks_created'] > 0 or verbose:
                # Reutilizar import superior de Table para evitar duplicados
                table = Table(title="Indexing Statistics")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")

                table.add_row("Files Processed", str(total_files - stats['files_skipped']))
                table.add_row("Files Skipped", str(stats['files_skipped']))
                table.add_row("Chunks Created", str(stats['chunks_created']))
                table.add_row("Embeddings Generated", str(stats['embeddings_generated']))

                if stats['errors'] > 0:
                    table.add_row("Errors", f"[red]{stats['errors']}[/red]")

                console.print(table)

                if stats['errors'] > 0:
                    console.print(
                        "\n[yellow]⚠ Some files had errors. Check logs for details.[/yellow]"
                    )

        finally:
            await websocket.close()

    except (websockets.ConnectionClosedError, asyncio.TimeoutError):
        # WebSocket failed, fallback to polling
        console.print("[yellow]⚠[/yellow] WebSocket connection failed, using HTTP polling")
        await monitor_via_polling(backend_port, task_id, total_files, console)

    except KeyboardInterrupt:
        console.print(
            "\n[yellow]Progress monitoring cancelled. Indexing continues in background.[/yellow]"
        )

    except Exception as e:
        console.print(f"[red]Error monitoring progress: {e}[/red]")
        if os.environ.get('ACOLYTE_DEBUG'):
            import traceback

            traceback.print_exc()


async def monitor_via_polling(backend_port: int, task_id: str, total_files: int, console):
    """Fallback monitoring via HTTP polling."""
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    import aiohttp
    import asyncio

    console.print("[dim]Using HTTP polling for progress updates...[/dim]")
    url = f"http://localhost:{backend_port}/api/index/task/{task_id}/status"

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Indexing files...", total=total_files or 100)
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            current = data.get('processed_files', 0)
                            total = data.get('total_files', total_files)
                            status = data.get('status', 'running')
                            progress.update(task, completed=current, total=total)
                            if status in ['completed', 'failed', 'cancelled']:
                                break
                        else:
                            console.print(
                                f"[yellow]Polling error: status {response.status}[/yellow]"
                            )
                except Exception as e:
                    console.print(f"[yellow]Polling error: {e}[/yellow]")
                await asyncio.sleep(2)
    console.print("\n[bold green]✓ Indexed completed (polling HTTP)[/bold green]")
