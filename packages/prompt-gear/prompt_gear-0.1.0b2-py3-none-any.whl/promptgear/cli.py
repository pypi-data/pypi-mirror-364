"""
Command-line interface for Prompt Gear.
"""
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from . import PromptManager, PromptNotFoundError, PromptAlreadyExistsError
from .schema import PromptTemplate


def _serialize_datetime(obj):
    """JSON serializer for datetime objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def _safe_json_dumps(data, indent=2):
    """Safe JSON dumps that handles datetime objects."""
    return json.dumps(data, indent=indent, default=_serialize_datetime)


def _read_file_content(file_path: str, content_type: str = "text") -> str:
    """
    Safely read content from a file.
    
    Args:
        file_path: Path to the file to read
        content_type: Type of content ("text", "json", "yaml")
    
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If no permission to read file
        ValueError: If file content is invalid for the specified type
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        # Read file content
        content = path.read_text(encoding='utf-8')
        
        # Validate content based on type
        if content_type == "json":
            try:
                json.loads(content)  # Validate JSON format
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in file {file_path}: {e}")
        elif content_type == "yaml":
            try:
                from .yaml_utils import load_yaml
                load_yaml(content)  # Validate YAML format
            except Exception as e:
                raise ValueError(f"Invalid YAML in file {file_path}: {e}")
        
        return content.strip()
        
    except PermissionError:
        raise PermissionError(f"Permission denied reading file: {file_path}")
    except Exception as e:
        raise ValueError(f"Error reading file {file_path}: {e}")

app = typer.Typer(
    name="promptgear",
    help="YAML-powered prompt manager with multi-backend support",
    rich_markup_mode="rich"
)
console = Console()


@app.command()
def create(
    name: str = typer.Argument(..., help="Prompt name"),
    version: str = typer.Option("v1", "--version", "-v", help="Prompt version"),
    system: Optional[str] = typer.Option(None, "--system", "-s", help="System prompt"),
    user: Optional[str] = typer.Option(None, "--user", "-u", help="User prompt"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config as JSON string"),
    system_file: Optional[str] = typer.Option(None, "--system-file", "-S", help="Path to file containing system prompt"),
    user_file: Optional[str] = typer.Option(None, "--user-file", "-U", help="Path to file containing user prompt"),
    config_file: Optional[str] = typer.Option(None, "--config-file", "-C", help="Path to JSON/YAML file containing config"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing prompt"),
):
    """Create a new prompt template."""
    try:
        pm = PromptManager()
        
        # Validate conflicting options
        if system and system_file:
            console.print("[red]Error:[/red] Cannot specify both --system and --system-file")
            sys.exit(1)
        
        if user and user_file:
            console.print("[red]Error:[/red] Cannot specify both --user and --user-file")
            sys.exit(1)
        
        if config and config_file:
            console.print("[red]Error:[/red] Cannot specify both --config and --config-file")
            sys.exit(1)
        
        # Read content from files if specified
        try:
            if system_file:
                system = _read_file_content(system_file, "text")
                console.print(f"[cyan]Info:[/cyan] Read system prompt from file: [green]{system_file}[/green]")
            
            if user_file:
                user = _read_file_content(user_file, "text")
                console.print(f"[cyan]Info:[/cyan] Read user prompt from file: [green]{user_file}[/green]")
            
            if config_file:
                config_content = _read_file_content(config_file, "text")
                # Determine file type by extension
                config_path = Path(config_file)
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    # Load YAML config
                    from .yaml_utils import load_yaml
                    config_dict = load_yaml(config_content)
                    config = _safe_json_dumps(config_dict)  # Convert to JSON string for consistency
                else:
                    # Assume JSON
                    _read_file_content(config_file, "json")  # Validate JSON
                    config = config_content
                console.print(f"[cyan]Info:[/cyan] Read config from file: [green]{config_file}[/green]")
        
        except (FileNotFoundError, PermissionError, ValueError) as e:
            console.print(f"[red]File Error:[/red] {e}")
            sys.exit(1)
        
        if interactive:
            # Interactive mode
            name = name or Prompt.ask("Prompt name")
            version = version or Prompt.ask("Version", default="v1")
            system = system or Prompt.ask("System prompt")
            user = user or Prompt.ask("User prompt")
            
            config_str = Prompt.ask("Config (JSON, optional)", default="")
            if config_str.strip():
                try:
                    config_dict = json.loads(config_str)
                except json.JSONDecodeError:
                    console.print("[red]Invalid JSON format for config[/red]")
                    sys.exit(1)
            else:
                config_dict = {}
        else:
            # Non-interactive mode
            if not system and not system_file:
                console.print("[red]Error:[/red] System prompt is required (use --system or --system-file)")
                sys.exit(1)
            if not user and not user_file:
                console.print("[red]Error:[/red] User prompt is required (use --user or --user-file)")
                sys.exit(1)
            
            config_dict = {}
            if config:
                try:
                    config_dict = json.loads(config)
                except json.JSONDecodeError:
                    console.print("[red]Invalid JSON format for config[/red]")
                    sys.exit(1)
        
        # Create prompt
        prompt = pm.create_prompt(
            name=name,
            version=version,
            system_prompt=system,
            user_prompt=user,
            config=config_dict,
            overwrite=overwrite
        )
        
        console.print(f"[green]✓[/green] Created prompt [bold]{name}:{version}[/bold]")
        _display_prompt(prompt)
        
    except PromptAlreadyExistsError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("Use --overwrite to overwrite existing prompt")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def get(
    name: str = typer.Argument(..., help="Prompt name"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Prompt version (if not specified, gets latest version)"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format (rich, json, yaml)")
):
    """Get a prompt template."""
    try:
        pm = PromptManager()
        prompt = pm.get_prompt(name, version)
        
        if format == "json":
            console.print(_safe_json_dumps(prompt.model_dump()))
        elif format == "yaml":
            from .yaml_utils import dump_yaml
            console.print(dump_yaml(prompt.model_dump()))
        else:
            _display_prompt(prompt)
            
    except PromptNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def list(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Filter by prompt name"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table, json)")
):
    """List prompt templates."""
    try:
        pm = PromptManager()
        prompts = pm.list_prompts(name)
        
        if not prompts:
            console.print("[yellow]No prompts found[/yellow]")
            return
        
        if format == "json":
            console.print(_safe_json_dumps([p.model_dump() for p in prompts]))
        else:
            table = Table(title="Prompt Templates")
            table.add_column("Name", style="cyan")
            table.add_column("Version", style="magenta")
            table.add_column("System Prompt", style="green", max_width=40)
            table.add_column("User Prompt", style="blue", max_width=40)
            table.add_column("Config", style="yellow")
            
            for prompt in prompts:
                config_str = _safe_json_dumps(prompt.config) if prompt.config else "{}"
                table.add_row(
                    prompt.name,
                    prompt.version,
                    prompt.system_prompt[:100] + "..." if len(prompt.system_prompt) > 100 else prompt.system_prompt,
                    prompt.user_prompt[:100] + "..." if len(prompt.user_prompt) > 100 else prompt.user_prompt,
                    config_str
                )
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def delete(
    name: str = typer.Argument(..., help="Prompt name"),
    version: str = typer.Option("v1", "--version", "-v", help="Prompt version"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Delete a prompt template."""
    try:
        pm = PromptManager()
        
        if not pm.prompt_exists(name, version):
            console.print(f"[red]Error:[/red] Prompt {name}:{version} not found")
            sys.exit(1)
        
        if not yes:
            if not Confirm.ask(f"Delete prompt {name}:{version}?"):
                console.print("Cancelled")
                return
        
        pm.delete_prompt(name, version)
        console.print(f"[green]✓[/green] Deleted prompt [bold]{name}:{version}[/bold]")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def versions(
    name: str = typer.Argument(..., help="Prompt name")
):
    """List versions of a prompt."""
    try:
        pm = PromptManager()
        versions = pm.list_versions(name)
        
        if not versions:
            console.print(f"[yellow]No versions found for prompt '{name}'[/yellow]")
            return
        
        console.print(f"[bold]Versions for '{name}':[/bold]")
        for version in versions:
            console.print(f"  • {version}")
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def init(
    backend: str = typer.Option("filesystem", "--backend", "-b", help="Backend type (filesystem, sqlite, postgres)"),
    prompt_dir: Optional[str] = typer.Option(None, "--prompt-dir", "-d", help="Prompt storage directory (filesystem backend only, default: ./prompts)"),
    force: bool = typer.Option(False, "--force", help="Force initialization")
):
    """Initialize Prompt Gear in current directory."""
    try:
        # Validate prompt_dir usage
        if prompt_dir is not None and backend != "filesystem":
            console.print(f"[red]Error:[/red] --prompt-dir option is only supported with filesystem backend")
            console.print(f"[yellow]Hint:[/yellow] Remove --prompt-dir option or use --backend filesystem")
            sys.exit(1)
        
        # Set default prompt directory
        if backend == "filesystem":
            prompt_storage_dir = prompt_dir or "./prompts"
            # Show info about prompt directory when using filesystem
            if prompt_dir:
                console.print(f"[cyan]Info:[/cyan] Using custom prompt directory: [green]{prompt_storage_dir}[/green]")
            else:
                console.print(f"[cyan]Info:[/cyan] Using default prompt directory: [green]{prompt_storage_dir}[/green]")
        else:
            prompt_storage_dir = "./prompts"  # Default for .env file even though not used
        
        env_path = Path(".env")
        
        # Prompt Gear environment variables
        promptgear_env_vars = {
            'PROMPT_GEAR_BACKEND': backend,
            'PROMPT_GEAR_PROMPT_DIR': prompt_storage_dir,
            'PROMPT_GEAR_DB_URL': 'sqlite:///prompts.db',
            'PROMPT_GEAR_DEBUG': 'false'
        }
        
        if env_path.exists() and not force:
            console.print("[yellow]Info:[/yellow] .env file already exists")
            
            # Read existing .env file
            existing_content = env_path.read_text(encoding='utf-8')
            existing_lines = existing_content.splitlines()
            
            # Check which Prompt Gear variables are already configured
            existing_vars = {}
            for line in existing_lines:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_vars[key.strip()] = value.strip()
            
            # Determine the backend to use (existing or command line)
            current_backend = existing_vars.get('PROMPT_GEAR_BACKEND', backend)
            
            # Adjust default DB URL based on backend
            if current_backend == 'postgres':
                promptgear_env_vars['PROMPT_GEAR_DB_URL'] = 'postgresql://user:pass@localhost/prompts'
            elif current_backend == 'sqlite':
                promptgear_env_vars['PROMPT_GEAR_DB_URL'] = 'sqlite:///prompts.db'
            
            # Update backend in defaults if it exists in env
            if 'PROMPT_GEAR_BACKEND' in existing_vars:
                promptgear_env_vars['PROMPT_GEAR_BACKEND'] = existing_vars['PROMPT_GEAR_BACKEND']
            
            # Find missing Prompt Gear variables
            missing_vars = {}
            for key, default_value in promptgear_env_vars.items():
                if key not in existing_vars:
                    missing_vars[key] = default_value
            
            if not missing_vars:
                console.print("[green]✓[/green] Prompt Gear configuration already exists in .env file")
            else:
                console.print(f"[yellow]Missing Prompt Gear configuration variables:[/yellow]")
                for key, value in missing_vars.items():
                    console.print(f"  • {key}={value}")
                
                if Confirm.ask("Add missing Prompt Gear configuration to existing .env file?"):
                    # Append missing variables to existing file
                    with open(env_path, 'a', encoding='utf-8') as f:
                        f.write("\n# Prompt Gear Configuration\n")
                        for key, value in missing_vars.items():
                            f.write(f"{key}={value}\n")
                        
                        # Add commented examples for database URLs
                        if 'PROMPT_GEAR_DB_URL' in missing_vars:
                            f.write("# PROMPT_GEAR_DB_URL=postgresql://user:pass@localhost/prompts\n")
                    
                    console.print("[green]✓[/green] Added Prompt Gear configuration to existing .env file")
                else:
                    console.print("[yellow]Skipped adding configuration to .env file[/yellow]")
                    console.print("[yellow]You can manually add these variables to your .env file later[/yellow]")
        else:
            # Create new .env file
            # Set appropriate DB URL based on backend
            if backend == 'postgres':
                db_url = 'postgresql://user:pass@localhost/prompts'
                commented_url = '# PROMPT_GEAR_DB_URL=sqlite:///prompts.db'
            else:
                db_url = 'sqlite:///prompts.db'
                commented_url = '# PROMPT_GEAR_DB_URL=postgresql://user:pass@localhost/prompts'
            
            env_content = f"""# Prompt Gear Configuration
PROMPT_GEAR_BACKEND={backend}
PROMPT_GEAR_PROMPT_DIR={prompt_storage_dir}
PROMPT_GEAR_DB_URL={db_url}
{commented_url}

# Development settings
PROMPT_GEAR_DEBUG=false
"""
            
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            console.print(f"[green]✓[/green] Created .env configuration file")
        
        # Initialize backend
        pm = PromptManager()
        pm.backend.initialize()
        
        console.print(f"[green]✓[/green] Initialized Prompt Gear with {backend} backend")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def status():
    """Show Prompt Gear status and backend information."""
    try:
        pm = PromptManager()
        
        # Get basic info
        backend_type = pm.config.backend
        console.print(f"[bold]Prompt Gear Status[/bold]")
        console.print(f"Backend: [cyan]{backend_type}[/cyan]")
        
        # Get backend-specific info
        if backend_type == "filesystem":
            console.print(f"Prompts directory: [green]{pm.config.prompt_dir}[/green]")
            prompts = pm.list_prompts()
            console.print(f"Total prompts: [yellow]{len(prompts)}[/yellow]")
            
            # Count unique names
            unique_names = len(set(p.name for p in prompts))
            console.print(f"Unique prompt names: [yellow]{unique_names}[/yellow]")
        
        elif backend_type == "sqlite":
            # Try to get stats if backend supports it
            try:
                if hasattr(pm.backend, 'get_stats'):
                    stats = pm.backend.get_stats()
                    console.print(f"Database: [green]{stats['database_path']}[/green]")
                    console.print(f"Total prompts: [yellow]{stats['total_prompts']}[/yellow]")
                    console.print(f"Unique prompt names: [yellow]{stats['unique_names']}[/yellow]")
                else:
                    console.print(f"Database URL: [green]{pm.config.db_url}[/green]")
                    prompts = pm.list_prompts()
                    console.print(f"Total prompts: [yellow]{len(prompts)}[/yellow]")
            except Exception as e:
                console.print(f"[red]Error getting stats:[/red] {e}")
        
        elif backend_type == "postgres":
            # Try to get stats if backend supports it
            try:
                if hasattr(pm.backend, 'get_stats'):
                    stats = pm.backend.get_stats()
                    console.print(f"Database URL: [green]{stats['database_url']}[/green]")
                    console.print(f"Database version: [green]{stats['database_version']}[/green]")
                    console.print(f"Total prompts: [yellow]{stats['total_prompts']}[/yellow]")
                    console.print(f"Unique prompt names: [yellow]{stats['unique_names']}[/yellow]")
                    console.print(f"Connection pool size: [blue]{stats['pool_size']}[/blue]")
                    console.print(f"Max connections: [blue]{stats['max_connections']}[/blue]")
                    
                    # Show config usage statistics
                    if stats.get('config_stats'):
                        console.print(f"\n[bold]Config usage:[/bold]")
                        for config_stat in stats['config_stats'][:5]:
                            console.print(f"  • {config_stat['key']}: {config_stat['count']} prompts")
                else:
                    console.print(f"Database URL: [green]{pm.config.db_url}[/green]")
                    prompts = pm.list_prompts()
                    console.print(f"Total prompts: [yellow]{len(prompts)}[/yellow]")
            except Exception as e:
                console.print(f"[red]Error getting stats:[/red] {e}")
        
        else:
            console.print(f"Database URL: [green]{pm.config.db_url}[/green]")
            prompts = pm.list_prompts()
            console.print(f"Total prompts: [yellow]{len(prompts)}[/yellow]")
        
        # Show recent prompts
        prompts = pm.list_prompts()
        if prompts:
            console.print(f"\n[bold]Recent prompts:[/bold]")
            for prompt in prompts[:5]:  # Show first 5
                console.print(f"  • {prompt.name}:{prompt.version}")
            
            if len(prompts) > 5:
                console.print(f"  ... and {len(prompts) - 5} more")
        else:
            console.print(f"\n[yellow]No prompts found[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    field: str = typer.Option("all", "--field", "-f", help="Search field (all, name, system_prompt, user_prompt)"),
    format: str = typer.Option("table", "--format", help="Output format (table, json)")
):
    """Search prompt templates."""
    try:
        pm = PromptManager()
        
        # Check if backend supports search
        if not hasattr(pm.backend, 'search_prompts'):
            console.print("[red]Search is not supported by the current backend[/red]")
            sys.exit(1)
        
        prompts = pm.backend.search_prompts(query, field)
        
        if not prompts:
            console.print(f"[yellow]No prompts found for query '{query}'[/yellow]")
            return
        
        if format == "json":
            console.print(_safe_json_dumps([p.model_dump() for p in prompts]))
        else:
            table = Table(title=f"Search Results for '{query}'")
            table.add_column("Name", style="cyan")
            table.add_column("Version", style="magenta")
            table.add_column("System Prompt", style="green", max_width=40)
            table.add_column("User Prompt", style="blue", max_width=40)
            
            for prompt in prompts:
                table.add_row(
                    prompt.name,
                    prompt.version,
                    prompt.system_prompt[:100] + "..." if len(prompt.system_prompt) > 100 else prompt.system_prompt,
                    prompt.user_prompt[:100] + "..." if len(prompt.user_prompt) > 100 else prompt.user_prompt
                )
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def find_by_config(
    config_json: str = typer.Argument(..., help="JSON config to search for"),
    format: str = typer.Option("table", "--format", help="Output format (table, json)")
):
    """Find prompts by configuration parameters."""
    try:
        pm = PromptManager()
        
        # Check if backend supports config queries
        if not hasattr(pm.backend, 'get_prompts_by_config'):
            console.print("[red]Config queries are not supported by the current backend[/red]")
            sys.exit(1)
        
        try:
            config_query = json.loads(config_json)
        except json.JSONDecodeError:
            console.print("[red]Invalid JSON format for config[/red]")
            sys.exit(1)
        
        prompts = pm.backend.get_prompts_by_config(config_query)
        
        if not prompts:
            console.print(f"[yellow]No prompts found with config {config_json}[/yellow]")
            return
        
        if format == "json":
            console.print(_safe_json_dumps([p.model_dump() for p in prompts]))
        else:
            table = Table(title=f"Prompts with config {config_json}")
            table.add_column("Name", style="cyan")
            table.add_column("Version", style="magenta")
            table.add_column("Config", style="yellow")
            
            for prompt in prompts:
                table.add_row(
                    prompt.name,
                    prompt.version,
                    _safe_json_dumps(prompt.config) if prompt.config else "{}"
                )
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@app.command()
def test_connection():
    """Test database connection (for database backends)."""
    try:
        pm = PromptManager()
        
        # Check if backend supports connection testing
        if hasattr(pm.backend, 'get_connection'):
            console.print("[bold]Testing database connection...[/bold]")
            
            # Test connection
            conn = pm.backend.get_connection()
            if conn:
                console.print("[green]✓ Database connection successful[/green]")
                pm.backend.put_connection(conn)
                
                # Get database info
                if hasattr(pm.backend, 'get_stats'):
                    stats = pm.backend.get_stats()
                    console.print(f"Database: {stats.get('database_version', 'Unknown')}")
                    console.print(f"Pool size: {stats.get('pool_size', 'N/A')}")
                    console.print(f"Max connections: {stats.get('max_connections', 'N/A')}")
            else:
                console.print("[red]✗ Failed to connect to database[/red]")
                sys.exit(1)
        else:
            console.print("[yellow]Connection testing not supported by current backend[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Connection test failed:[/red] {e}")
        sys.exit(1)


def _display_prompt(prompt: PromptTemplate):
    """Display a prompt in rich format."""
    panel_content = f"""[bold cyan]Name:[/bold cyan] {prompt.name}
[bold magenta]Version:[/bold magenta] {prompt.version}

[bold green]System Prompt:[/bold green]
{prompt.system_prompt}

[bold blue]User Prompt:[/bold blue]
{prompt.user_prompt}

[bold yellow]Config:[/bold yellow]
{_safe_json_dumps(prompt.config) if prompt.config else '{}'}"""
    
    console.print(Panel(panel_content, title="Prompt Template", expand=False))


if __name__ == "__main__":
    app()
