"""Index command for ACOLYTE CLI."""

import asyncio
import click
import requests
from pathlib import Path
from typing import Optional

# ProjectManager will be passed as parameter
from acolyte.install.commands import validators
from acolyte.install.commands.progress_monitor import monitor_indexing_progress


def index_impl(
    path: str,
    partial: bool,
    progress: bool,
    verbose: bool,
    resume: Optional[str],
    dir: Optional[str],
    manager,
):
    """Implementation of index command."""
    project_path = Path(path)

    # 🔧 CRITICAL FIX: Invertir la lógica - full por defecto, partial como opción
    full = not partial  # Si no es parcial, es completo

    # Validate project is initialized
    validators.validate_project_initialized(project_path, manager)

    # Load project info and config
    project_info = validators.validate_project_info(project_path, manager)
    project_id = project_info['project_id']
    project_dir = manager.get_project_dir(project_id)

    # Validate project is configured
    config = validators.validate_project_configured(project_dir)

    # Check if backend is ready
    validators.validate_backend_ready(config)

    # Check version compatibility
    validators.validate_version_compatibility(project_path, project_id, manager.global_dir)

    # Start indexing
    click.echo(click.style("📚 Starting project indexing...", fg="cyan"))
    click.echo(f"Project path: {project_path.resolve()}")
    click.echo(f"Full index: {full}")

    # Mostrar si se especificó un directorio específico
    if dir:
        click.echo(click.style(f"📁 Indexando solo el directorio: {dir}", fg="cyan"))

    try:
        backend_port = config['ports']['backend']

        # 🔧 FIX: Verify services are healthy before indexing
        click.echo("Verifying backend services...")
        health_url = f"http://localhost:{backend_port}/api/health"
        try:
            health_response = requests.get(health_url, timeout=30)
            health_data = health_response.json()

            if health_response.status_code == 200:
                click.echo(click.style("✓ All services ready", fg="green"))
            elif health_response.status_code == 503:
                click.echo(click.style("✗ Critical services unhealthy", fg="red"))
                click.echo(f"Details: {health_data.get('services', {})}")
                raise SystemExit(1)
        except requests.RequestException as e:
            click.echo(click.style(f"⚠ Could not verify services: {e}", fg="yellow"))

        url = f"http://localhost:{backend_port}/api/index/project"

        # Prepare request data
        request_data = {
            "patterns": [
                "*.py",
                "*.js",
                "*.ts",
                "*.tsx",
                "*.jsx",
                "*.java",
                "*.go",
                "*.rs",
                "*.cpp",
                "*.c",
                "*.h",
                "*.hpp",
                "*.cs",
                "*.rb",
                "*.php",
                "*.swift",
                "*.kt",
                "*.scala",
                "*.r",
                "*.m",
                "*.mm",
                "*.sql",
                "*.sh",
                "*.yaml",
                "*.yml",
                "*.json",
                "*.xml",
                "*.toml",
                "*.ini",
                "*.cfg",
                "*.conf",
                "*.md",
                "*.rst",
                "*.txt",
            ],
            "exclude_patterns": [
                "**/node_modules/**",
                "**/__pycache__/**",
                "**/dist/**",
                "**/.git/**",
                "**/venv/**",
                "**/.venv/**",
                "**/build/**",
                "**/target/**",
            ],
            "respect_gitignore": True,
            "respect_acolyteignore": True,
            "force_reindex": full,
            "resume_task_id": resume,  # Add resume task ID if provided
            "project_path": str(
                project_path.resolve()
            ),  # 🔧 CRITICAL FIX: Send absolute project path
        }

        # Añadir directorio específico si se proporcionó
        if dir:
            request_data["specific_directory"] = dir

        # Show progress while waiting for initial response
        click.echo(click.style("\n⏳ Estimating project size...", fg="yellow"))
        click.echo("This may take a moment for large projects...")

        # Use a spinner while waiting
        with click.progressbar(length=1, label='Sending indexing request') as bar:
            response = requests.post(url, json=request_data, timeout=300)  # 5 minutes timeout
            bar.update(1)

        if response.status_code == 200:
            result = response.json()
            click.echo(click.style("✓ Indexing started successfully!", fg="green"))
            click.echo(f"Task ID: {result.get('task_id', 'N/A')}")
            click.echo(f"Estimated files: {result.get('estimated_files', 'N/A')}")

            # Show summary if present
            if 'report' in result:
                click.echo("\nIndexing summary:")
                for k, v in result['report'].items():
                    if k == 'Errors' and v:
                        click.echo(click.style(f"{k}:", fg="red"))
                        for err in v:
                            click.echo(
                                f"  - File: {err['file']} | Stage: {err['stage']} | Error: {err['error']}"
                            )
                    elif k == 'Warnings' and v:
                        click.echo(click.style(f"{k}:", fg="yellow"))
                        for warn in v:
                            click.echo(f"  - {warn}")
                    else:
                        click.echo(f"{k}: {v}")

            # Show initial file collection info if available
            if result.get('patterns'):
                click.echo(f"Patterns: {len(result['patterns'])} file types")

            # Warn if very few files
            if result.get('estimated_files', 1000) < 10:
                click.echo(
                    click.style(
                        "\n⚠ Only a few files found to index. Check your project structure.",
                        fg="yellow",
                    )
                )

            # Connect to WebSocket for live progress if requested
            if progress and result.get('websocket_url'):
                click.echo("\nConnecting to progress monitor...")
                # Run async progress monitoring
                asyncio.run(
                    monitor_indexing_progress(
                        backend_port=backend_port,
                        websocket_path=result['websocket_url'],
                        task_id=result.get('task_id'),
                        total_files=result.get('estimated_files', 0),
                        verbose=verbose,
                    )
                )
            else:
                click.echo(f"\nWebSocket URL: {result.get('websocket_url', 'N/A')}")
                click.echo("Use WebSocket to monitor progress or check logs with 'acolyte logs'.")
        else:
            error_text = response.text
            try:
                error_json = response.json()
                if 'detail' in error_json:
                    error_text = error_json['detail']
            except ValueError:
                pass
            click.echo(click.style(f"✗ Indexing failed: {error_text}", fg="red"))
            raise SystemExit(1)

    except requests.RequestException as e:
        click.echo(click.style(f"✗ Failed to connect to backend: {e}", fg="red"))
        click.echo(click.style("Is the backend running? Try:", fg="yellow"))
        click.echo("  acolyte status")
        click.echo("  acolyte restart")
        click.echo("  acolyte doctor")
        raise SystemExit(1)
    except Exception as e:
        click.echo(click.style(f"✗ Indexing error: {e}", fg="red"))
        click.echo(click.style("If the problem persists, try:", fg="yellow"))
        click.echo("  acolyte doctor")
        raise SystemExit(1)
