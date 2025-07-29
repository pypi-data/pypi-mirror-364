"""Command-line interface for LLM cache."""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .core.cache import LLMCache
from .integrations.http_proxy import LLMCacheProxy
from .utils.config import get_config

app = typer.Typer(help="LLM Cache - A drop-in cache for Large Language Model API calls")
console = Console()


@app.command()
def stats(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed statistics"),
):
    """Show cache statistics."""
    try:
        cache = LLMCache()
        stats = cache.get_stats()
        
        # Basic stats
        console.print(f"[bold blue]Cache Statistics[/bold blue]")
        console.print(f"Total entries: {stats.total_entries}")
        console.print(f"Hit rate: {stats.hit_rate:.2%}")
        console.print(f"Cost saved: ${stats.total_cost_saved_usd:.4f}")
        
        if stats.oldest_entry:
            console.print(f"Oldest entry: {stats.oldest_entry.strftime('%Y-%m-%d %H:%M:%S')}")
        if stats.newest_entry:
            console.print(f"Newest entry: {stats.newest_entry.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if verbose:
            # Provider breakdown
            if stats.provider_stats:
                console.print("\n[bold]Provider Breakdown:[/bold]")
                provider_table = Table(show_header=True, header_style="bold magenta")
                provider_table.add_column("Provider")
                provider_table.add_column("Entries")
                provider_table.add_column("Total Cost")
                provider_table.add_column("Total Tokens")
                
                for provider, data in stats.provider_stats.items():
                    provider_table.add_row(
                        provider,
                        str(data["count"]),
                        f"${data['total_cost']:.4f}",
                        str(data["total_tokens"]),
                    )
                
                console.print(provider_table)
            
            # Model breakdown
            if stats.model_stats:
                console.print("\n[bold]Model Breakdown:[/bold]")
                model_table = Table(show_header=True, header_style="bold magenta")
                model_table.add_column("Model")
                model_table.add_column("Entries")
                model_table.add_column("Total Cost")
                model_table.add_column("Total Tokens")
                
                for model, data in stats.model_stats.items():
                    model_table.add_row(
                        model,
                        str(data["count"]),
                        f"${data['total_cost']:.4f}",
                        str(data["total_tokens"]),
                    )
                
                console.print(model_table)
        
        cache.close()
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def list(
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum number of entries to show"),
    offset: int = typer.Option(0, "--offset", "-o", help="Number of entries to skip"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Filter by provider"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Filter by model"),
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Search query"),
):
    """List cache entries."""
    try:
        cache = LLMCache()
        entries = cache.list_entries(limit=limit, offset=offset, provider=provider, model=model, query=query)
        
        if not entries:
            console.print("[yellow]No cache entries found.[/yellow]")
            return
        
        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Key")
        table.add_column("Provider")
        table.add_column("Model")
        table.add_column("Created")
        table.add_column("Cost")
        table.add_column("Tokens")
        table.add_column("Hits")
        
        for entry in entries:
            # Truncate key for display
            key_display = entry.key[:12] + "..." if len(entry.key) > 15 else entry.key
            
            # Format cost
            cost_display = f"${entry.cost_usd:.4f}" if entry.cost_usd else "N/A"
            
            # Format tokens
            tokens_display = str(entry.output_tokens) if entry.output_tokens else "N/A"
            
            table.add_row(
                key_display,
                entry.provider,
                entry.model,
                entry.created_at.strftime("%Y-%m-%d %H:%M"),
                cost_display,
                tokens_display,
                str(entry.access_count),
            )
        
        console.print(table)
        console.print(f"\nShowing {len(entries)} entries")
        
        cache.close()
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def show(
    key: str = typer.Argument(..., help="Cache entry key"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Show details of a cache entry."""
    try:
        cache = LLMCache()
        entry = cache.get(key)
        
        if not entry:
            console.print(f"[red]Cache entry not found: {key}[/red]")
            sys.exit(1)
        
        # Display entry details
        console.print(f"[bold blue]Cache Entry: {key}[/bold blue]")
        console.print(f"Provider: {entry.provider}")
        console.print(f"Model: {entry.model}")
        console.print(f"Endpoint: {entry.endpoint}")
        console.print(f"Created: {entry.created_at}")
        console.print(f"Last accessed: {entry.accessed_at}")
        console.print(f"Access count: {entry.access_count}")
        
        if entry.cost_usd:
            console.print(f"Cost: ${entry.cost_usd:.4f}")
        if entry.input_tokens:
            console.print(f"Input tokens: {entry.input_tokens}")
        if entry.output_tokens:
            console.print(f"Output tokens: {entry.output_tokens}")
        if entry.latency_ms:
            console.print(f"Latency: {entry.latency_ms:.2f}ms")
        
        # Show request
        console.print(f"\n[bold]Request:[/bold]")
        console.print(json.dumps(entry.request_data, indent=2))
        
        # Show response
        console.print(f"\n[bold]Response:[/bold]")
        if entry.is_streaming and entry.stream_chunks:
            console.print(f"[yellow]Streaming response with {len(entry.stream_chunks)} chunks[/yellow]")
            console.print(f"Final text: {entry.response_text[:200]}...")
        else:
            console.print(json.dumps(entry.response_data, indent=2))
        
        # Save to file if requested
        if output:
            data = {
                "key": entry.key,
                "provider": entry.provider,
                "model": entry.model,
                "endpoint": entry.endpoint,
                "request_data": entry.request_data,
                "response_data": entry.response_data,
                "response_text": entry.response_text,
                "metadata": {
                    "created_at": entry.created_at.isoformat(),
                    "accessed_at": entry.accessed_at.isoformat(),
                    "access_count": entry.access_count,
                    "cost_usd": entry.cost_usd,
                    "input_tokens": entry.input_tokens,
                    "output_tokens": entry.output_tokens,
                    "latency_ms": entry.latency_ms,
                }
            }
            
            with open(output, "w") as f:
                json.dump(data, f, indent=2)
            
            console.print(f"\n[green]Entry saved to {output}[/green]")
        
        cache.close()
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def purge(
    key: Optional[str] = typer.Option(None, "--key", "-k", help="Delete specific entry by key"),
    older: Optional[str] = typer.Option(None, "--older", "-o", help="Delete entries older than N days"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Delete entries for specific model"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Delete entries for specific provider"),
    expired: bool = typer.Option(False, "--expired", "-e", help="Delete expired entries"),
    all: bool = typer.Option(False, "--all", "-a", help="Delete all entries"),
    confirm: bool = typer.Option(False, "--confirm", "-y", help="Skip confirmation prompt"),
):
    """Purge cache entries."""
    try:
        cache = LLMCache()
        
        if all:
            if not confirm:
                if not typer.confirm("Are you sure you want to delete ALL cache entries?"):
                    console.print("[yellow]Operation cancelled.[/yellow]")
                    return
            
            # Get all entries and delete them
            entries = cache.list_entries(limit=1000000)  # Large limit to get all
            deleted_count = 0
            for entry in entries:
                if cache.delete(entry.key):
                    deleted_count += 1
            
            console.print(f"[green]Deleted {deleted_count} entries.[/green]")
            
        elif key:
            if cache.delete(key):
                console.print(f"[green]Deleted entry: {key}[/green]")
            else:
                console.print(f"[red]Entry not found: {key}[/red]")
                sys.exit(1)
                
        elif older:
            try:
                days = int(older)
                deleted_count = cache.purge_older_than(days)
                console.print(f"[green]Deleted {deleted_count} entries older than {days} days.[/green]")
            except ValueError:
                console.print("[red]Invalid number of days.[/red]")
                sys.exit(1)
                
        elif expired:
            deleted_count = cache.purge_expired()
            console.print(f"[green]Deleted {deleted_count} expired entries.[/green]")
            
        elif model or provider:
            # Get entries matching criteria
            entries = cache.list_entries(limit=1000000, model=model, provider=provider)
            deleted_count = 0
            
            if not confirm:
                filter_desc = []
                if model:
                    filter_desc.append(f"model={model}")
                if provider:
                    filter_desc.append(f"provider={provider}")
                
                if not typer.confirm(f"Delete {len(entries)} entries matching {' and '.join(filter_desc)}?"):
                    console.print("[yellow]Operation cancelled.[/yellow]")
                    return
            
            for entry in entries:
                if cache.delete(entry.key):
                    deleted_count += 1
            
            console.print(f"[green]Deleted {deleted_count} entries.[/green]")
            
        else:
            console.print("[red]Please specify what to purge. Use --help for options.[/red]")
            sys.exit(1)
        
        cache.close()
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def export(
    output: Path = typer.Argument(..., help="Output file path"),
    format: str = typer.Option("jsonl", "--format", "-f", help="Output format (jsonl, json)"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Maximum number of entries to export"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Filter by provider"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Filter by model"),
):
    """Export cache entries to file."""
    try:
        cache = LLMCache()
        entries = cache.list_entries(limit=limit, provider=provider, model=model)
        
        if not entries:
            console.print("[yellow]No entries to export.[/yellow]")
            return
        
        def serialize_entry(entry):
            """Serialize entry with proper UUID and datetime handling."""
            data = entry.dict()
            # Convert UUID to string
            if 'id' in data and data['id']:
                data['id'] = str(data['id'])
            # Convert datetime objects to ISO format strings
            for key, value in data.items():
                if hasattr(value, 'isoformat'):
                    data[key] = value.isoformat()
            return data
        
        if format == "jsonl":
            with open(output, "w") as f:
                for entry in entries:
                    json.dump(serialize_entry(entry), f)
                    f.write("\n")
        elif format == "json":
            data = [serialize_entry(entry) for entry in entries]
            with open(output, "w") as f:
                json.dump(data, f, indent=2)
        else:
            console.print(f"[red]Unsupported format: {format}[/red]")
            sys.exit(1)
        
        console.print(f"[green]Exported {len(entries)} entries to {output}[/green]")
        cache.close()
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8100, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
):
    """Start HTTP proxy server."""
    try:
        import uvicorn
        
        # Create proxy
        proxy = LLMCacheProxy()
        
        console.print(f"[bold blue]Starting LLM Cache Proxy[/bold blue]")
        console.print(f"Host: {host}")
        console.print(f"Port: {port}")
        console.print(f"Metrics: http://{host}:{port}/metrics")
        console.print(f"Health: http://{host}:{port}/health")
        console.print(f"Proxy: http://{host}:{port}/v1/chat/completions")
        
        # Start server
        uvicorn.run(
            proxy.app,
            host=host,
            port=port,
            reload=reload,
            log_level="info",
        )
        
    except ImportError:
        console.print("[red]uvicorn not installed. Install with: pip install uvicorn[standard][/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def doctor():
    """Check system health and configuration."""
    try:
        console.print("[bold blue]LLM Cache Health Check[/bold blue]")
        
        # Check cache directory
        cache_dir = Path.home() / ".cache" / "llm-cache"
        if cache_dir.exists():
            console.print(f"[green]✓ Cache directory exists: {cache_dir}[/green]")
        else:
            console.print(f"[yellow]⚠ Cache directory does not exist: {cache_dir}[/yellow]")
        
        # Check database
        try:
            cache = LLMCache()
            stats = cache.get_stats()
            console.print(f"[green]✓ Database accessible: {stats.total_entries} entries[/green]")
            cache.close()
        except Exception as e:
            console.print(f"[red]✗ Database error: {e}[/red]")
        
        # Check config
        try:
            config = get_config()
            console.print(f"[green]✓ Configuration loaded[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠ Configuration error: {e}[/yellow]")
        
        # Check dependencies
        try:
            import sqlmodel
            console.print("[green]✓ SQLModel available[/green]")
        except ImportError:
            console.print("[red]✗ SQLModel not available[/red]")
        
        try:
            import zstandard
            console.print("[green]✓ zstandard available[/green]")
        except ImportError:
            console.print("[red]✗ zstandard not available[/red]")
        
        try:
            import cryptography
            console.print("[green]✓ cryptography available[/green]")
        except ImportError:
            console.print("[red]✗ cryptography not available[/red]")
        
        console.print("\n[bold]Health check complete.[/bold]")
        
    except Exception as e:
        console.print(f"[red]Error during health check: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    app() 