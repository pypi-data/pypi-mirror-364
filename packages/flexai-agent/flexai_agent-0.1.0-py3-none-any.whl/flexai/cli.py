"""
Command Line Interface for Flexai
"""

import argparse
import os
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax

from .agent import Agent
from .config import Config
from .project import ProjectAnalyzer
from .utils import setup_logging

console = Console()


class FlexaiCLI:
    """Main CLI class for Flexai"""

    def __init__(self):
        self.config = Config()
        self.agent: Agent | None = None

    def setup_agent(self):
        """Initialize the agent with current configuration"""
        try:
            self.agent = Agent(self.config)
            console.print("[green]✓[/green] Agent initialized successfully")
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to initialize agent: {e}")
            sys.exit(1)

    def configure_api(self):
        """Interactive API configuration"""
        console.print(Panel.fit("🔧 API Configuration", style="blue"))

        # Get API provider details
        provider_name = Prompt.ask("Provider name", default="openai")
        
        # Check if this is a local provider that doesn't need API keys
        is_local_provider = provider_name.lower() in ["ollama", "lm-studio", "local"]
        
        if is_local_provider:
            console.print(f"[dim]Local provider '{provider_name}' detected - no API key needed[/dim]")
            api_key = "not-needed"
            
            # Set appropriate defaults for local providers
            if provider_name.lower() == "ollama":
                base_url = Prompt.ask("Base URL", default="http://localhost:11434/v1")
                model = Prompt.ask("Default model", default="llama2:latest")
            elif provider_name.lower() == "lm-studio":
                base_url = Prompt.ask("Base URL", default="http://localhost:1234/v1")
                model = Prompt.ask("Default model", default="local-model")
            else:
                base_url = Prompt.ask("Base URL", default="http://localhost:8000/v1")
                model = Prompt.ask("Default model", default="local-model")
        else:
            # Cloud providers need API keys
            api_key = Prompt.ask("API Key", password=True)
            
            if provider_name.lower() == "openai":
                base_url = Prompt.ask("Base URL", default="https://api.openai.com/v1")
                model = Prompt.ask("Default model", default="gpt-4o-mini")
            elif provider_name.lower() == "anthropic":
                base_url = Prompt.ask("Base URL", default="https://api.anthropic.com/v1")
                model = Prompt.ask("Default model", default="claude-3-5-sonnet-20241022")
            else:
                base_url = Prompt.ask("Base URL", default="https://api.openai.com/v1")
                model = Prompt.ask("Default model", default="gpt-4o-mini")

        # Save configuration
        self.config.add_provider(
            provider_name, {"api_key": api_key, "base_url": base_url, "model": model}
        )

        # Set as active provider
        self.config.set_active_provider(provider_name)
        self.config.save()

        console.print(
            f"[green]✓[/green] Configuration saved for provider '{provider_name}'"
        )
        
        if is_local_provider:
            console.print(f"[yellow]Note: Make sure {provider_name} is running at {base_url}[/yellow]")

    def list_providers(self):
        """List all configured providers"""
        providers = self.config.list_providers()

        if not providers:
            console.print("[yellow]No providers configured yet[/yellow]")
            console.print("\nTo get started:")
            console.print(
                "1. Run [bold]flexai configure[/bold] to set up a provider"
            )
            console.print("2. Or set environment variables:")
            console.print("   • [dim]export OPENAI_API_KEY='your-key-here'[/dim]")
            console.print(
                "   • [dim]export API_KEY='your-key-here'[/dim] (generic fallback)"
            )
            console.print(
                "\nSupported providers:"
            )
            console.print("   • [bold]Cloud:[/bold] OpenAI, Anthropic")
            console.print("   • [bold]Local:[/bold] Ollama (no API key needed), LM Studio")
            console.print("   • [bold]Ollama:[/bold] Default URL: http://localhost:11434/v1")
            return

        console.print(Panel.fit("🔧 Configured Providers", style="blue"))

        for provider in providers:
            active_marker = "🟢" if provider == self.config.active_provider else "⚪"
            provider_config = self.config.get_provider(provider)

            # Show provider info
            console.print(f"{active_marker} [bold]{provider}[/bold]")
            console.print(f"   Base URL: {provider_config.get('base_url', 'N/A')}")
            console.print(f"   Model: {provider_config.get('model', 'N/A')}")

            # Check API key status
            try:
                api_key = self.config.get_api_key(provider)
                if api_key == "not-needed":
                    console.print("   API Key: [dim]Not required[/dim]")
                else:
                    console.print("   API Key: [green]✓ Configured[/green]")
            except Exception:
                console.print("   API Key: [red]✗ Missing[/red]")

            console.print()

        if self.config.active_provider:
            console.print(
                f"Active provider: [green]{self.config.active_provider}[/green]"
            )
        else:
            console.print("[yellow]No active provider set[/yellow]")

    def switch_provider(self, provider_name: str):
        """Switch to a different provider"""
        if provider_name not in self.config.list_providers():
            console.print(f"[red]✗[/red] Provider '{provider_name}' not found")
            return

        self.config.set_active_provider(provider_name)
        self.config.save()
        console.print(f"[green]✓[/green] Switched to provider '{provider_name}'")

        # Reinitialize agent with new provider
        if self.agent:
            self.setup_agent()

    def chat_mode(self):
        """Interactive chat mode"""
        if not self.agent:
            console.print("[red]✗[/red] Agent not initialized. Run 'configure' first.")
            return

        console.print(Panel.fit("💬 Chat Mode - Type 'exit' to quit", style="green"))
        console.print(
            "You can ask questions, request code generation, or get help with programming tasks.\n"
        )

        while True:
            try:
                user_input = Prompt.ask("[bold blue]You[/bold blue]")

                if user_input.lower() in ["exit", "quit", "bye"]:
                    console.print("[yellow]Goodbye![/yellow]")
                    break

                if not user_input.strip():
                    continue

                # Get response from agent
                console.print("[dim]Thinking...[/dim]")
                response = self.agent.chat(user_input)

                # Display response
                console.print(f"[bold green]Agent[/bold green]: {response}\n")

            except KeyboardInterrupt:
                console.print("\n[yellow]Chat session ended[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}\n")

    def generate_code(self, prompt: str, language: str = "python", auto_save: bool = False, output_file: str = None):
        """Generate code based on prompt"""
        if not self.agent:
            console.print("[red]✗[/red] Agent not initialized. Run 'configure' first.")
            return

        try:
            console.print(f"[dim]Generating {language} code...[/dim]")
            code = self.agent.generate_code(prompt, language)

            # Display generated code with syntax highlighting (code is already cleaned by agent)
            syntax = Syntax(code, language, theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"Generated {language.title()} Code"))

            # Handle saving based on auto flag
            if auto_save:
                # Auto-save mode
                if output_file:
                    filename = output_file
                else:
                    # Generate default filename based on language
                    ext_map = {
                        "python": ".py",
                        "javascript": ".js",
                        "go": ".go",
                        "rust": ".rs",
                        "java": ".java",
                        "cpp": ".cpp",
                        "c": ".c",
                    }
                    ext = ext_map.get(language, ".txt")
                    filename = f"generated_code{ext}"
                
                try:
                    with open(filename, "w") as f:
                        f.write(code)
                    console.print(f"[green]✓[/green] Code auto-saved to {filename}")
                except Exception as e:
                    console.print(f"[red]✗[/red] Failed to save file: {e}")
            else:
                # Interactive mode - ask if user wants to save the code
                if Confirm.ask("Save this code to a file?"):
                    filename = Prompt.ask("Enter filename")
                    try:
                        with open(filename, "w") as f:
                            f.write(code)
                        console.print(f"[green]✓[/green] Code saved to {filename}")
                    except Exception as e:
                        console.print(f"[red]✗[/red] Failed to save file: {e}")

        except Exception as e:
            console.print(f"[red]Error generating code:[/red] {e}")

    def execute_code(self, code: str, language: str = "python", auto_execute: bool = False):
        """Execute code safely"""
        if not self.agent:
            console.print("[red]✗[/red] Agent not initialized. Run 'configure' first.")
            return

        # Handle execution confirmation based on auto flag
        if not auto_execute:
            if not Confirm.ask("Are you sure you want to execute this code?"):
                console.print("[yellow]Code execution cancelled[/yellow]")
                return

        try:
            console.print("[dim]Executing code...[/dim]")
            result = self.agent.execute_code(code, language)

            if result["success"]:
                if result["output"]:
                    console.print(Panel(result["output"], title="Execution Output"))
                else:
                    console.print(
                        "[green]✓[/green] Code executed successfully (no output)"
                    )
            else:
                console.print(
                    Panel(result["error"], title="Execution Error", style="red")
                )

        except Exception as e:
            console.print(f"[red]Error executing code:[/red] {e}")

    def project_workflow(self, project_dir: str, task: str):
        """Execute a project-aware workflow"""
        console.print(f"[blue]🔍 Analyzing project: {project_dir}[/blue]")

        # Initialize project analyzer
        try:
            analyzer = ProjectAnalyzer(project_dir)
            context = analyzer.crawl_project()
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to analyze project: {e}")
            return

        # Display project info
        console.print(
            Panel.fit(f"📁 Project: {context['project_path']}", style="green")
        )

        # Show git status
        git_info = context["git_status"]
        if git_info["is_git_repo"]:
            if git_info.get("has_changes"):
                console.print("[yellow]⚠[/yellow] Git repo has uncommitted changes")
                console.print(f"   Branch: {git_info.get('current_branch', 'unknown')}")
            else:
                console.print(
                    f"[green]✓[/green] Git repo clean on branch: {git_info.get('current_branch', 'unknown')}"
                )
        else:
            console.print("[yellow]⚠[/yellow] Not a git repository")

        # Show agent.md status
        agent_context = context["agent_context"]
        if agent_context.get("created"):
            console.print("[green]✓[/green] Created new agent.md for project context")
        elif agent_context.get("exists"):
            console.print("[blue]ℹ[/blue] Using existing agent.md for context")

        # Prepare comprehensive context for the agent
        project_context = self._format_project_context(context)

        # Setup agent and execute task
        self.setup_agent()
        if not self.agent:
            return

        console.print(f"[blue]🤖 Executing task: {task}[/blue]")

        # Create enhanced prompt with full project context
        enhanced_prompt = f"""You are working on a project with the following context:

PROJECT CONTEXT:
{project_context}

TASK: {task}

Please analyze the project thoroughly and complete the requested task. Consider:
- The current project structure and key files
- Git status and recent changes
- Existing documentation and patterns
- Dependencies and technologies used
- Any context from agent.md

Provide a comprehensive solution that fits well with the existing codebase."""

        try:
            response = self.agent.chat(enhanced_prompt)
            console.print(Panel(Markdown(response), title="Task Result", expand=False))

            # Update agent.md with task completion
            analyzer.update_agent_context(
                task, "Completed task via Agentix. See above for details."
            )
            console.print("[green]✓[/green] Updated agent.md with task completion")

        except Exception as e:
            console.print(f"[red]✗[/red] Task execution failed: {e}")

    def _format_project_context(self, context: dict) -> str:
        """Format project context for the agent"""
        lines = []

        # Basic info
        lines.append(f"Project Path: {context['project_path']}")
        lines.append(f"Analysis Time: {context['timestamp']}")

        # Git status
        git_info = context["git_status"]
        if git_info["is_git_repo"]:
            lines.append("\nGIT STATUS:")
            lines.append(f"- Branch: {git_info.get('current_branch', 'unknown')}")
            lines.append(f"- Has Changes: {git_info.get('has_changes', False)}")
            if git_info.get("recent_commits"):
                lines.append("- Recent Commits:")
                for commit in git_info["recent_commits"][:3]:
                    lines.append(f"  • {commit}")

        # File structure (summarized)
        lines.append("\nPROJECT STRUCTURE:")
        structure = context["file_structure"]
        for path, info in list(structure.items())[:10]:  # Limit to first 10 directories
            if path == "":
                path = "."
            lines.append(f"- {path}/")
            for file in info["files"][:5]:  # First 5 files per directory
                lines.append(f"  • {file}")

        # Key files content
        lines.append("\nKEY FILES:")
        for filename, file_info in context["key_files"].items():
            lines.append(f"- {filename}:")
            if "content" in file_info:
                lines.append(f"  Content preview: {file_info['content'][:500]}...")
            elif "error" in file_info:
                lines.append(f"  Error: {file_info['error']}")

        # Dependencies
        deps = context["dependencies"]
        if deps:
            lines.append("\nDEPENDENCIES:")
            for lang, dep_info in deps.items():
                lines.append(f"- {lang}: {dep_info}")

        # Agent context
        agent_context = context["agent_context"]
        if agent_context.get("content"):
            lines.append("\nAGENT CONTEXT (from agent.md):")
            lines.append(agent_context["content"][:1000])  # First 1000 chars

        return "\n".join(lines)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Flexai - API-agnostic agentic Python package",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--version", action="version", version="Flexai 0.1.0")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Configure command
    subparsers.add_parser("configure", help="Configure API provider")

    # List providers command
    subparsers.add_parser("list", help="List configured providers")

    # Switch provider command
    switch_parser = subparsers.add_parser("switch", help="Switch active provider")
    switch_parser.add_argument("provider", help="Provider name to switch to")

    # Chat command
    subparsers.add_parser("chat", help="Start interactive chat mode")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate code")
    generate_parser.add_argument("prompt", help="Code generation prompt")
    generate_parser.add_argument(
        "--language", "-l", default="python", help="Programming language"
    )
    generate_parser.add_argument(
        "--auto", "-a", action="store_true", help="Auto-save code without prompting"
    )
    generate_parser.add_argument(
        "--output", "-o", help="Output filename for auto-save mode"
    )

    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute code from file")
    execute_parser.add_argument("file", help="Code file to execute")
    execute_parser.add_argument(
        "--language", "-l", help="Programming language (auto-detected if not specified)"
    )
    execute_parser.add_argument(
        "--auto", "-a", action="store_true", help="Auto-execute without prompting"
    )

    # Project workflow command
    project_parser = subparsers.add_parser(
        "project", help="Execute project-aware workflow"
    )
    project_parser.add_argument(
        "--dir", required=True, help="Project directory to analyze"
    )
    project_parser.add_argument(
        "--task", required=True, help="Task to execute with project context"
    )

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        setup_logging(level="DEBUG")
    else:
        setup_logging(level="INFO")

    # Initialize CLI
    cli = FlexaiCLI()

    # Handle commands
    if args.command == "configure":
        cli.configure_api()
    elif args.command == "list":
        cli.list_providers()
    elif args.command == "switch":
        cli.switch_provider(args.provider)
    elif args.command == "chat":
        cli.setup_agent()
        cli.chat_mode()
    elif args.command == "generate":
        cli.setup_agent()
        cli.generate_code(args.prompt, args.language, args.auto, args.output)
    elif args.command == "execute":
        if not os.path.exists(args.file):
            console.print(f"[red]✗[/red] File not found: {args.file}")
            return 1

        with open(args.file) as f:
            code = f.read()

        language = args.language
        if not language:
            # Auto-detect language from file extension
            _, ext = os.path.splitext(args.file)
            language_map = {
                ".py": "python",
                ".js": "javascript",
                ".go": "go",
                ".rs": "rust",
            }
            language = language_map.get(ext, "python")

        cli.setup_agent()
        cli.execute_code(code, language, args.auto)
    elif args.command == "project":
        cli.project_workflow(args.dir, args.task)
    else:
        # Show help if no command provided
        console.print(Panel.fit("🤖 Flexai - API-agnostic Agent", style="blue"))
        console.print("\nAvailable commands:")
        console.print("  • [bold]configure[/bold] - Set up API provider")
        console.print("  • [bold]list[/bold] - List configured providers")
        console.print("  • [bold]switch <provider>[/bold] - Switch active provider")
        console.print("  • [bold]chat[/bold] - Start interactive chat")
        console.print("  • [bold]generate <prompt>[/bold] - Generate code")
        console.print("  • [bold]execute <file>[/bold] - Execute code file")
        console.print(
            "  • [bold]project --dir <path> --task <task>[/bold] - Project-aware workflow"
        )
        console.print("\nUse --help for more details on each command.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
