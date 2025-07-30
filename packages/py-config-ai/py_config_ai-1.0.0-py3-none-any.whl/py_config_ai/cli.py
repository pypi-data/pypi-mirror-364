"""
Command-line interface for py-config-ai.

This module provides the main CLI interface using Typer for a polished experience.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

from .core.generator import ConfigGenerator
from .core.key_manager import KeyManager
from .configs.config_types import SUPPORTED_CONFIGS, get_config_info, list_configs_by_category, get_categories
from .configs.presets import PRESETS, get_preset_info, list_presets
from .utils.validation import validate_api_key

app = typer.Typer(
    name="py-config-ai",
    help="AI-powered configuration file generator for developers",
    add_completion=False,
    rich_markup_mode="rich"
)

console = Console()


# This is the main entry point - the app() function is called by Typer


@app.command()
def generate(
    config_type: Optional[str] = typer.Option(
        None, 
        "--type", "-t", 
        help="Type of configuration to generate"
    ),
    description: Optional[str] = typer.Option(
        None, 
        "--description", "-d", 
        help="Description of desired configuration"
    ),
    provider: str = typer.Option(
        "openai", 
        "--provider", "-p", 
        help="AI provider to use (openai, anthropic, gemini, groq)"
    ),
    preset: Optional[str] = typer.Option(
        None, 
        "--preset", 
        help="Use a preset configuration"
    ),
    context: Optional[str] = typer.Option(
        None, 
        "--context", "-c", 
        help="Path to codebase for context"
    ),
    output: Optional[str] = typer.Option(
        None, 
        "--output", "-o", 
        help="Output file path (auto-detected if not provided)"
    ),
    preview: bool = typer.Option(
        False, 
        "--preview", 
        help="Show preview before saving (default: save directly)"
    ),
    interactive: bool = typer.Option(
        False, 
        "--interactive", "-i", 
        help="Run in interactive mode"
    )
):
    """Generate a configuration file using AI."""
    generator = ConfigGenerator()
    
    if interactive:
        _run_interactive_generate(generator)
        return

    # Validate provider
    if provider not in generator.get_available_providers():
        console.print(f"[red]Error: Unsupported provider '{provider}'[/red]")
        console.print(f"Available providers: {', '.join(generator.get_available_providers())}")
        raise typer.Exit(1)

    # Check if provider has API key
    key_manager = KeyManager()
    if not key_manager.has_key(provider):
        console.print(f"[red]Error: No API key configured for provider '{provider}'[/red]")
        console.print(f"Use [bold]py-config-ai add-key {provider}[/bold] to add your API key")
        raise typer.Exit(1)

    # Validate required parameters
    if not config_type:
        console.print("[red]Error: --type is required for non-interactive mode[/red]")
        console.print("Use --interactive for guided mode or specify --type")
        raise typer.Exit(1)
    
    if not description:
        console.print("[red]Error: --description is required for non-interactive mode[/red]")
        console.print("Use --interactive for guided mode or specify --description")
        raise typer.Exit(1)

    # Validate config type
    if not get_config_info(config_type):
        console.print(f"[red]Error: Unsupported config type '{config_type}'[/red]")
        console.print("Use 'py-config-ai list' to see supported types")
        raise typer.Exit(1)

    # Determine output filename
    if output is None:
        output = _get_default_filename(config_type)
        console.print(f"[green]Will save to: {output}[/green]")

    # Generate the configuration
    console.print(f"[bold green]Generating {config_type} configuration...[/bold green]")
    
    try:
        result = asyncio.run(generator.generate_config(
            config_type=config_type,
            description=description,
            provider=provider,
            context=context,
            preset=preset,
            output_file=output,
            preview=preview
        ))
        
        if result:
            console.print(f"\n[bold green]✓ Configuration generated successfully![/bold green]")
            console.print(f"Saved to: [bold]{output}[/bold]")
            console.print(f"\nYou can now edit the file: [bold]code {output}[/bold] or [bold]nano {output}[/bold]")
        else:
            console.print(f"\n[red]Failed to generate configuration.[/red]")
            
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def create(
    description: str = typer.Argument(..., help="Natural language description of what you want to configure"),
    provider: str = typer.Option(
        "openai", 
        "--provider", "-p", 
        help="AI provider to use (openai, anthropic, gemini, groq)"
    ),
    context: Optional[str] = typer.Option(
        None, 
        "--context", "-c", 
        help="Path to codebase for context"
    ),
    output: Optional[str] = typer.Option(
        None, 
        "--output", "-o", 
        help="Output file path (auto-detected if not provided)"
    ),
    no_preview: bool = typer.Option(
        True, 
        "--preview", 
        help="Show preview before saving (default: save directly)"
    )
):
    """Create a configuration file using natural language description.
    
    Examples:
        py-config-ai create "I want to format Python code with 88 character line length"
        py-config-ai create "Generate a prettier config for a React project"
        py-config-ai create "Create a dockerfile for a Python web app"
    """
    generator = ConfigGenerator()
    
    # Validate provider
    if provider not in generator.get_available_providers():
        console.print(f"[red]Error: Unsupported provider '{provider}'[/red]")
        console.print(f"Available providers: {', '.join(generator.get_available_providers())}")
        raise typer.Exit(1)

    # Check if provider has API key
    key_manager = KeyManager()
    if not key_manager.has_key(provider):
        console.print(f"[red]Error: No API key configured for provider '{provider}'[/red]")
        console.print(f"Use [bold]py-config-ai add-key {provider}[/bold] to add your API key")
        raise typer.Exit(1)

    # Try to infer config type from description
    config_type = _infer_config_type(description)
    
    if config_type:
        console.print(f"[green]Detected configuration type: {config_type}[/green]")
    else:
        console.print("[yellow]Could not determine configuration type from description.[/yellow]")
        console.print("Available types:")
        for category in get_categories():
            configs = list_configs_by_category(category)
            console.print(f"  {category}: {', '.join(configs)}")
        raise typer.Exit(1)

    # Determine output filename
    if output is None:
        output = _get_default_filename(config_type)
        console.print(f"[green]Will save to: {output}[/green]")

    # Generate the configuration
    console.print(f"[bold green]Generating {config_type} configuration...[/bold green]")
    
    try:
        result = asyncio.run(generator.generate_config(
            config_type=config_type,
            description=description,
            provider=provider,
            context=context,
            output_file=output,
            preview=not no_preview
        ))
        
        if result:
            console.print(f"\n[bold green]✓ Configuration generated successfully![/bold green]")
            console.print(f"Saved to: [bold]{output}[/bold]")
            console.print(f"\nYou can now edit the file: [bold]code {output}[/bold] or [bold]nano {output}[/bold]")
        else:
            console.print(f"\n[red]Failed to generate configuration.[/red]")
            
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def list():
    """List supported configuration types."""
    table = Table(title="Supported Configuration Types")
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Category", style="green")
    table.add_column("Format", style="yellow")

    for config_type, info in SUPPORTED_CONFIGS.items():
        table.add_row(
            config_type,
            info["description"],
            info["category"],
            info["file_extension"] or "text"
        )

    console.print(table)


@app.command()
def presets():
    """List available presets."""
    table = Table(title="Available Presets")
    table.add_column("Preset", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    table.add_column("Configs", style="green")

    for preset_name in list_presets():
        preset_info = get_preset_info(preset_name)
        if preset_info:
            table.add_row(
                preset_name,
                preset_info["description"],
                ", ".join(preset_info["configs"])
            )

    console.print(table)


@app.command()
def add_key(
    provider: str = typer.Argument(..., help="Provider name (openai, anthropic, gemini, groq)"),
    key: Optional[str] = typer.Option(None, "--key", "-k", help="API key (will prompt if not provided)")
):
    """Add an API key for an AI provider."""
    key_manager = KeyManager()
    
    # Validate provider
    if provider not in ["openai", "anthropic", "gemini", "groq"]:
        console.print(f"[red]Error: Unsupported provider '{provider}'[/red]")
        console.print("Supported providers: openai, anthropic, gemini, groq")
        raise typer.Exit(1)

    # Get API key if not provided
    if not key:
        key = Prompt.ask(f"Enter your {provider} API key", password=True)

    # Validate API key
    is_valid, error_msg = validate_api_key(key, provider)
    if not is_valid:
        console.print(f"[red]Error: {error_msg}[/red]")
        raise typer.Exit(1)

    # Store the key
    if key_manager.add_key(provider, key):
        console.print(f"[green]✓ API key for {provider} stored successfully[/green]")
    else:
        console.print(f"[red]Error: Failed to store API key for {provider}[/red]")
        raise typer.Exit(1)


@app.command()
def remove_key(
    provider: str = typer.Argument(..., help="Provider name to remove key for")
):
    """Remove an API key for an AI provider."""
    key_manager = KeyManager()
    
    if key_manager.remove_key(provider):
        console.print(f"[green]✓ API key for {provider} removed successfully[/green]")
    else:
        console.print(f"[yellow]No API key found for {provider}[/yellow]")


@app.command()
def list_keys():
    """List configured API keys."""
    key_manager = KeyManager()
    providers = key_manager.list_providers()
    
    if not providers:
        console.print("[yellow]No API keys configured[/yellow]")
        console.print("Use [bold]py-config-ai add-key <provider>[/bold] to add API keys")
        return

    table = Table(title="Configured API Keys")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")

    for provider in providers:
        table.add_row(provider, "✓ Configured")

    console.print(table)


@app.command()
def test(
    provider: str = typer.Option("openai", "--provider", "-p", help="Provider to test")
):
    """Test connection to an AI provider."""
    generator = ConfigGenerator()
    
    console.print(f"[bold]Testing connection to {provider}...[/bold]")
    
    if generator.test_provider(provider):
        console.print(f"[green]✓ Connection to {provider} successful[/green]")
    else:
        console.print(f"[red]✗ Connection to {provider} failed[/red]")
        console.print("Make sure you have:")
        console.print("1. Added an API key using [bold]py-config-ai add-key {provider}[/bold]")
        console.print("2. Valid API key for the provider")
        console.print("3. Internet connection")
        raise typer.Exit(1)


def _run_interactive_generate(generator: ConfigGenerator):
    """Run interactive configuration generation."""
    console.print("[bold blue]Interactive Configuration Generator[/bold blue]\n")
    console.print("I'll help you generate a configuration file! Let me ask you a few questions.\n")

    # Select config type
    config_type = _prompt_config_type()
    
    # Select provider
    provider = _prompt_provider(generator)
    
    # Get description in natural language
    description = _prompt_description(config_type)
    
    # Ask about context
    context = _prompt_context()
    
    # Generate the configuration
    console.print(f"\n[bold green]Generating {config_type} configuration...[/bold green]")
    
    try:
        # Generate with automatic file saving
        result = asyncio.run(generator.generate_config(
            config_type=config_type,
            description=description,
            provider=provider,
            context=context,
            output_file=_get_default_filename(config_type),
            preview=False  # Don't show preview, just save directly
        ))
        
        if result:
            filename = _get_default_filename(config_type)
            console.print(f"\n[bold green]✓ Configuration generated successfully![/bold green]")
            console.print(f"Saved to: [bold]{filename}[/bold]")
            console.print(f"\nYou can now edit the file: [bold]code {filename}[/bold] or [bold]nano {filename}[/bold]")
        else:
            console.print(f"\n[red]Failed to generate configuration.[/red]")
            
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")


def _get_default_filename(config_type: str) -> str:
    """Get the default filename for a configuration type."""
    config_info = get_config_info(config_type)
    extension = config_info['file_extension']
    
    # Handle special cases
    if config_type.startswith('.'):
        return config_type  # e.g., .prettierrc, .eslintrc
    elif config_type == 'dockerfile':
        return 'Dockerfile'  # Capitalize Dockerfile
    elif config_type == 'gitignore':
        return '.gitignore'
    elif config_type == 'pyproject.toml':
        return 'pyproject.toml'  # Don't add .toml extension
    else:
        return f"{config_type}{extension}"


def _prompt_description(config_type: str) -> str:
    """Prompt user for configuration description in natural language."""
    config_info = get_config_info(config_type)
    
    console.print(f"\n[bold]Tell me about your {config_type} configuration:[/bold]")
    console.print(f"Current config: {config_info['description']}")
    
    examples = config_info.get('examples', [])
    if examples:
        console.print(f"Common options: {', '.join(examples)}")
    
    console.print("\n[dim]Examples:[/dim]")
    console.print("  • '100 character line length with strict formatting'")
    console.print("  • 'relaxed rules for a small team project'")
    console.print("  • 'production-ready with all strict checks enabled'")
    console.print("  • 'just the basic settings, keep it simple'")
    
    while True:
        try:
            description = Prompt.ask("\nDescribe your preferences", default="standard configuration")
            if description.strip():
                return description
            console.print("[red]Please provide a description.[/red]")
        except KeyboardInterrupt:
            raise typer.Exit(0)


def _prompt_context() -> Optional[str]:
    """Prompt user for codebase context."""
    console.print(f"\n[bold]Do you want to provide codebase context?[/bold]")
    console.print("[dim]This helps generate more relevant configurations based on your project structure.[/dim]")
    
    if Confirm.ask("Include codebase context?", default=False):
        while True:
            try:
                context_path = Prompt.ask("Path to your codebase", default=".")
                if Path(context_path).exists():
                    return context_path
                console.print(f"[red]Path '{context_path}' does not exist.[/red]")
            except KeyboardInterrupt:
                raise typer.Exit(0)
    
    return None


def _prompt_output(config_type: str) -> str:
    """Prompt user for output file path with smart defaults."""
    default_filename = _get_default_filename(config_type)
    
    console.print(f"\n[bold]Configuration will be saved to:[/bold] [green]{default_filename}[/green]")
    
    if Confirm.ask("Use this filename?", default=True):
        return default_filename
    
    while True:
        try:
            output_path = Prompt.ask("Enter custom filename", default=default_filename)
            if output_path.strip():
                return output_path
            console.print("[red]Please provide a filename.[/red]")
        except KeyboardInterrupt:
            raise typer.Exit(0)


def _prompt_config_type() -> str:
    """Prompt user to select a configuration type."""
    console.print("\n[bold]Available configuration types:[/bold]")
    
    # Build a flat list with global numbering
    all_configs = []
    categories = get_categories()
    
    for category in categories:
        configs = list_configs_by_category(category)
        console.print(f"\n[bold]{category.title()}:[/bold]")
        for config in configs:
            all_configs.append(config)
            info = get_config_info(config)
            console.print(f"  {len(all_configs)}. {config} - {info['description']}")
    
    while True:
        try:
            choice = Prompt.ask("\nSelect configuration type (number or name)")
            
            # Try as number first
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(all_configs):
                    return all_configs[choice_num - 1]
            except ValueError:
                pass
            
            # Try as name
            if choice in SUPPORTED_CONFIGS:
                return choice
            
            # Try fuzzy matching for natural language
            matched_config = _fuzzy_match_config(choice)
            if matched_config:
                return matched_config
            
            console.print("[red]Invalid choice. Please try again.[/red]")
        except KeyboardInterrupt:
            raise typer.Exit(0)


def _fuzzy_match_config(user_input: str) -> Optional[str]:
    """Fuzzy match user input to configuration types using natural language."""
    user_input_lower = user_input.lower()
    
    # Direct matches
    for config_name in SUPPORTED_CONFIGS.keys():
        if user_input_lower in config_name.lower() or config_name.lower() in user_input_lower:
            return config_name
    
    # Keyword-based matching (prioritize more specific matches)
    keyword_mapping = [
        # Most specific matches first
        ('eslint', '.eslintrc'),
        ('react', '.eslintrc'),
        ('typescript', 'tsconfig.json'),
        ('ts', 'tsconfig.json'),
        ('prettier', '.prettierrc'),
        ('javascript', '.prettierrc'),
        ('js', '.prettierrc'),
        
        # Python configs
        ('black', 'black'),
        ('format', 'black'),
        ('formatter', 'black'),
        ('sort', 'isort'),
        ('import', 'isort'),
        ('linter', 'ruff'),
        ('ruff', 'ruff'),
        ('flake', 'flake8'),
        ('pylint', 'pylint'),
        ('mypy', 'mypy'),
        ('type', 'mypy'),
        ('python', 'pyproject.toml'),
        
        # Other configs
        ('markdown', 'markdownlint.json'),
        ('md', 'markdownlint.json'),
        ('css', 'stylelint'),
        ('style', 'stylelint'),
        ('docker', 'dockerfile'),
        ('container', 'dockerfile'),
        ('env', '.env'),
        ('environment', '.env'),
        ('compose', 'docker-compose.yml'),
        ('nginx', 'nginx.conf'),
        ('server', 'nginx.conf'),
        ('git', 'gitignore'),
        ('ignore', 'gitignore'),
    ]
    
    for keyword, config_name in keyword_mapping:
        if keyword in user_input_lower:
            return config_name
    
    # Description-based matching
    for config_name, info in SUPPORTED_CONFIGS.items():
        description_lower = info['description'].lower()
        if any(word in description_lower for word in user_input_lower.split()):
            return config_name
    
    return None


def _prompt_provider(generator: ConfigGenerator) -> str:
    """Prompt user to select a provider."""
    console.print("\n[bold]Available providers:[/bold]")
    
    providers = generator.get_available_providers()
    key_manager = KeyManager()
    
    for i, provider in enumerate(providers, 1):
        status = "✓" if key_manager.has_key(provider) else "✗"
        console.print(f"  {i}. {provider} {status}")
    
    while True:
        try:
            choice = Prompt.ask("\nSelect provider (number or name)")
            
            # Try as number first
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(providers):
                    provider = providers[choice_num - 1]
                else:
                    raise ValueError()
            except ValueError:
                provider = choice
            
            if provider in providers:
                if key_manager.has_key(provider):
                    return provider
                else:
                    console.print(f"[red]No API key configured for {provider}[/red]")
                    console.print(f"Use [bold]py-config-ai add-key {provider}[/bold] to add your API key")
                    raise typer.Exit(1)
            
            console.print("[red]Invalid choice. Please try again.[/red]")
        except KeyboardInterrupt:
            raise typer.Exit(0)


def _prompt_preset() -> str:
    """Prompt user to select a preset."""
    console.print("\n[bold]Available presets:[/bold]")
    
    presets = list_presets()
    for i, preset in enumerate(presets, 1):
        preset_info = get_preset_info(preset)
        if preset_info:
            console.print(f"  {i}. {preset} - {preset_info['description']}")
    
    while True:
        try:
            choice = Prompt.ask("\nSelect preset (number or name)")
            
            # Try as number first
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(presets):
                    return presets[choice_num - 1]
            except ValueError:
                pass
            
            # Try as name
            if choice in presets:
                return choice
            
            console.print("[red]Invalid choice. Please try again.[/red]")
        except KeyboardInterrupt:
            raise typer.Exit(0)


def _infer_config_type(description: str) -> Optional[str]:
    """Infer configuration type from natural language description."""
    description_lower = description.lower()
    
    # Use the same fuzzy matching logic as the interactive mode
    return _fuzzy_match_config(description) 