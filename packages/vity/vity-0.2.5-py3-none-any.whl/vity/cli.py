#!/usr/bin/env python3
"""
Vity CLI - AI-powered terminal assistant
"""
import sys
import os
import argparse
import json
from pathlib import Path

from .llm import generate_command, generate_chat_response, remove_terminal_history_tags
from . import __version__


def check_config() -> bool:
    """Check if configuration exists"""
    config_dir = Path.home() / ".config" / "vity"
    config_file = config_dir / ".env"
    return config_file.exists()

def setup_config() -> bool:
    """Setup configuration on first run"""
    config_dir = Path.home() / ".config" / "vity"
    config_file = config_dir / ".env"
    
    if not config_file.exists():
        print("🤖 Welcome to Vity! Let's set up your OpenAI API key.")
        print("You can get one at: https://platform.openai.com/api-keys")
        print()
        
        base_url = input("Enter your LLM provider base url: ").strip()
        api_key = input("Enter your LLM provider API key[Use 'NONE' if not needed]: ").strip()
        llm_model = input("Enter LLM model name to use: ").strip()
        terminal_history_limit = input("How many lines of terminal history do you wanna send to the LLM[Leave empty for default: last 1000 lines]: ").strip()

        if not api_key:
            print("❌ API key is required")
            return False
        if not base_url:
            print("❌ Base URL is required")
            return False
        if not llm_model:
            print("❌ LLM model name is required")
        if not terminal_history_limit:
            terminal_history_limit = "1000"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        config_text = f"VITY_LLM_API_KEY={api_key}\nVITY_LLM_MODEL={llm_model}\nVITY_LLM_BASE_URL={base_url}\nVITY_TERMINAL_HISTORY_LIMIT={terminal_history_limit}"
        config_file.write_text(config_text)
        
        print("✅ Configuration saved!")
        print(f"Config file: {config_file}")
        print()
        
    else:
        print("✅ Configuration already exists")
        print(f"Config file: {config_file}")
        print("Run 'vity config --reset' to reset the configuration")




def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Vity - AI-powered terminal assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vity do "find all python files"
  vity chat "explain this error"
  vity -f session.log do "fix the deployment issue"
  vity -c chat.json chat "continue our conversation"
  vity -f session.log -c chat.json do "help with this error"
  vity config --reset
  vity reinstall
  vity uninstall
  
For shell integration, run: vity install
        """
    )
    
    parser.add_argument(
        "-f", "--file", dest="history_file",
        help="Path to terminal session log file for context"
    )
    parser.add_argument(
        "-c", "--chat", dest="chat_file",
        help="Path to chat history file for conversation context"
    )
    parser.add_argument(
        "-m", "--mode", dest="interaction_mode",
        choices=["do", "chat"],
        default="do",
        help="Interaction mode (default: do)"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Do command
    do_parser = subparsers.add_parser("do", help="Generate shell command")
    do_parser.add_argument("prompt", nargs="+", help="What you want to do")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Chat with AI")
    chat_parser.add_argument("prompt", nargs="+", help="Your question")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install shell integration")
    
    # Reinstall command
    reinstall_parser = subparsers.add_parser("reinstall", help="Reinstall shell integration")
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall vity completely")
    uninstall_parser.add_argument("--force", action="store_true", help="Skip confirmation prompts")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("--reset", action="store_true", help="Reset configuration")
    config_parser.add_argument("--show", action="store_true", help="Show configuration")
    
    args = parser.parse_args()
    
    # Handle special commands first (always available)
    if args.command == "install":
        install_shell_integration()
        return
    
    if args.command == "reinstall":
        reinstall_shell_integration()
        return
    
    if args.command == "uninstall":
        uninstall_shell_integration(args.force)
        return
    
    if args.command == "config":
        if args.reset:
            reset_config()
            return
        elif args.show:
            show_config()
            return
        else:
            setup_config()
            return
    
    # Setup config if needed (for other commands)
    if not check_config():
        setup_config()
        return
    
    # Handle main commands
    if not args.command:
        parser.print_help()
        return
    
    if args.command in ["do", "chat"]:
        from vity.config import config
        if "googleapis" in config.vity_llm_base_url:
            provider = "google"
        else:
            provider = "openai"
        user_input = " ".join(args.prompt)
        
        # Load terminal history if provided
        terminal_history = ""
        if args.history_file:
            try:
                with open(args.history_file, "r") as f:
                    terminal_history = f.read()
            except FileNotFoundError:
                print(f"⚠️  Warning: history file '{args.history_file}' not found")
        
        # Load chat history if provided
        chat_history = []
        if args.chat_file:
            try:
                with open(args.chat_file, "r") as f:
                    chat_history = json.load(f)
            except FileNotFoundError:
                # Create empty chat history file if it doesn't exist
                chat_history = []
            except json.JSONDecodeError:
                print(f"⚠️  Warning: chat file '{args.chat_file}' contains invalid JSON, starting fresh")
                chat_history = []
        
        print("🤖 Vity is thinking...")
        
        try:
            if args.command == "do":
                
                updated_chat_history = generate_command(terminal_history, chat_history, user_input, provider)

                for message in reversed(updated_chat_history):
                    if message["role"] == "user":
                        message["content"][0]["text"] = remove_terminal_history_tags(message["content"][0]["text"]) 
                        break

                # Extract the command from the last assistant message
                last_assistant_msg = None
                for msg in reversed(updated_chat_history):
                    if msg.get("role") == "assistant":
                        last_assistant_msg = msg
                        break
                
                if last_assistant_msg:
                    # Extract command from assistant response
                    content = last_assistant_msg.get("content", [{}])[0].get("text", "")
                    if " # " in content:
                        cmd_part = content.split(" # ")[0]
                        comment_part = content.split(" # ")[1].replace(" * vity generated command", "")
                        cmd_string = f"{cmd_part} # {comment_part}"
                    else:
                        cmd_string = content
                    print(f"Command: {cmd_string}")
                    
                    # Add to bash history
                    history_file = Path.home() / ".bash_history"
                    if history_file.exists():
                        with open(history_file, "a") as f:
                            f.write(f"{cmd_string} # Vity generated\n")

                
                # Save updated chat history
                if args.chat_file:
                    with open(args.chat_file, "w") as f:
                        json.dump(updated_chat_history, f, indent=2)
                
            elif args.command == "chat":
                updated_chat_history = generate_chat_response(terminal_history, chat_history, user_input, provider)

                for message in reversed(updated_chat_history):
                    if message["role"] == "user":
                        message["content"][0]["text"] = remove_terminal_history_tags(message["content"][0]["text"]) 
                        break

                # Extract the response from the last assistant message
                last_assistant_msg = None
                for msg in reversed(updated_chat_history):
                    if msg.get("role") == "assistant":
                        last_assistant_msg = msg
                        break
                
                if last_assistant_msg:
                    content = last_assistant_msg.get("content", [{}])[0].get("text", "")
                    print(content)
                
                # Save updated chat history
                if args.chat_file:
                    with open(args.chat_file, "w") as f:
                        json.dump(updated_chat_history, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)


def install_shell_integration():
    """Install shell integration"""
    script_content = '''
# Vity shell integration
vity() {
    if [[ "$1" == "record" ]]; then
        shift
        log_dir="$HOME/.local/share/vity/logs"
        chat_dir="$HOME/.local/share/vity/chat"
        mkdir -p "$log_dir"
        mkdir -p "$chat_dir"
        logfile="$log_dir/$(date +%Y%m%d-%H%M%S)-$$.log"
        chatfile="$chat_dir/$(date +%Y%m%d-%H%M%S)-$$.json"
        
        export VITY_ACTIVE_LOG="$logfile"
        export VITY_ACTIVE_CHAT="$chatfile"
        echo "🔴 Starting recording session"
        echo "📝 Use 'vity do' or 'vity chat' for contextual help"
        echo "🛑 Type 'exit' to stop recording"
        
        script -f "$logfile"
        
        unset VITY_ACTIVE_LOG VITY_ACTIVE_CHAT
        echo "🟢 Recording session ended"
        
    elif [[ "$1" == "do" ]]; then
        shift
        if [[ -n "$VITY_ACTIVE_LOG" && -f "$VITY_ACTIVE_LOG" ]]; then
            command vity -f "$VITY_ACTIVE_LOG" -c "$VITY_ACTIVE_CHAT" do "$@"
        else
            echo "⚠️  No active recording. Use 'vity record' for context."
            command vity do "$@"
        fi
        
    elif [[ "$1" == "chat" ]]; then
        shift
        if [[ -n "$VITY_ACTIVE_LOG" && -f "$VITY_ACTIVE_LOG" ]]; then
            command vity -f "$VITY_ACTIVE_LOG" -c "$VITY_ACTIVE_CHAT" chat "$@"
        else
            echo "⚠️  No active recording. Use 'vity record' for context."
            command vity chat "$@"
        fi
        
    elif [[ "$1" == "status" ]]; then
        if [[ -n "$VITY_ACTIVE_LOG" ]]; then
            echo "🔴 Recording active:"
            echo "  📝 Terminal log: $VITY_ACTIVE_LOG"
            echo "  💬 Chat history: $VITY_ACTIVE_CHAT"
        else
            echo "⚫ No active recording"
        fi
        
    # Forward commands that should be handled directly by the Python CLI
    elif [[ "$1" == "install" || "$1" == "reinstall" || "$1" == "config" || "$1" == "uninstall" ]]; then
        # Call the underlying vity executable with the provided arguments unchanged
        command vity "$@"
        
    elif [[ "$1" == "help" || "$1" == "-h" || "$1" == "--help" ]]; then
        cat << 'EOF'
🤖 Vity - AI Terminal Assistant

USAGE:
    vity <command> [options] [prompt]

COMMANDS:
    do <prompt>      Generate a shell command (adds to history)
    chat <prompt>    Chat with AI about terminal/coding topics
    record           Start recording session for context
    status           Show current recording status
    config           Show configuration
    config --reset   Reset configuration (always available)
    install          Install shell integration (always available)
    reinstall        Reinstall shell integration (always available)
    uninstall        Completely remove vity and all data
    help             Show this help message

EXAMPLES:
    vity do "find all python files"
    vity chat "explain this error message"
    vity record
    vity do "deploy the app"  # (with context from recording)
    vity status
    vity config --reset
    vity reinstall

CONTEXT:
    • Use 'vity record' to start capturing session context
    • Commands run during recording provide better AI responses
    • Recording captures both terminal output and chat history
    • Recording indicator (🔴) shows in your prompt
    • Use 'exit' to stop recording
EOF
        
    else
        # Show help for unknown commands or no arguments
        if [[ -n "$1" ]]; then
            echo "❌ Unknown command: $1"
            echo ""
        fi
        echo "🤖 Vity - AI Terminal Assistant"
        echo ""
        echo "Usage: vity <command> [prompt]"
        echo ""
        echo "Commands:"
        echo "  do <prompt>      Generate shell command"
        echo "  chat <prompt>    Chat with AI"
        echo "  record           Start recording session"
        echo "  status           Show recording status"
        echo "  config           Show configuration"
        echo "  config --reset   Reset configuration"
        echo "  install          Install shell integration"
        echo "  reinstall        Reinstall shell integration"
        echo "  uninstall        Completely remove vity and all data"
        echo "  help             Show detailed help"
        echo ""
        echo "Run 'vity help' for more details and examples."
    fi
    
    history -n 2>/dev/null || true
}
'''
    
    bashrc = Path.home() / ".bashrc"
    if bashrc.exists():
        content = bashrc.read_text()
        if "# Vity shell integration" not in content:
            with open(bashrc, "a") as f:
                f.write(f"\n{script_content}")
            print("✅ Shell integration installed!")
            print("Run 'source ~/.bashrc' or start a new terminal session")
        else:
            print("✅ Shell integration already installed")
    else:
        print("❌ ~/.bashrc not found")


def reinstall_shell_integration():
    """Reinstall shell integration (remove existing and install fresh)"""
    bashrc = Path.home() / ".bashrc"
    
    if not bashrc.exists():
        print("❌ ~/.bashrc not found")
        return
    
    print("🔄 Reinstalling shell integration...")
    
    # Read the current bashrc content
    content = bashrc.read_text()
    
    # Find and remove existing vity shell integration
    lines = content.split('\n')
    new_lines = []
    in_vity_section = False
    
    for line in lines:
        if line.strip() == "# Vity shell integration":
            in_vity_section = True
            print("🗑️  Removing existing shell integration...")
            continue
        elif in_vity_section and line.strip() == "}":
            in_vity_section = False
            continue
        elif not in_vity_section:
            new_lines.append(line)
    
    # Write the cleaned content back
    bashrc.write_text('\n'.join(new_lines))
    
    # Install fresh shell integration
    print("✨ Installing fresh shell integration...")
    install_shell_integration()


def uninstall_shell_integration(force: bool = False):
    """Completely uninstall vity and clean up all data"""
    print("🗑️  Vity Uninstaller")
    print()
    
    if not force:
        print("This will remove:")
        print("• Shell integration from ~/.bashrc")
        print("• Configuration files (~/.config/vity/)")
        print("• Log files (~/.local/share/vity/)")
        print("• Chat history files")
        print("• Vity-generated bash history entries")
        print("• Vity package itself")
        print()
        
        confirm = input("Are you sure you want to uninstall vity? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Uninstall cancelled")
            return
    
    # 1. Remove shell integration
    remove_shell_integration()
    
    # 2. Remove configuration
    remove_configuration()
    
    # 3. Remove logs and chat data
    remove_data_files()
    
    # 4. Clean bash history
    clean_bash_history()
    
    # 5. Remove package (this needs to be last)
    remove_package()
    
    print("✅ Vity has been completely uninstalled!")
    print("Please restart your terminal for changes to take effect.")


def remove_shell_integration():
    """Remove vity function from ~/.bashrc"""
    bashrc = Path.home() / ".bashrc"
    
    if not bashrc.exists():
        print("ℹ️  ~/.bashrc not found, skipping shell integration removal")
        return
    
    content = bashrc.read_text()
    
    if "# Vity shell integration" not in content:
        print("ℹ️  Shell integration not found in ~/.bashrc")
        return
    
    # Remove the entire vity function
    lines = content.split('\n')
    new_lines = []
    in_vity_section = False
    
    for line in lines:
        if line.strip() == "# Vity shell integration":
            in_vity_section = True
            print("🗑️  Removing shell integration from ~/.bashrc")
            continue
        elif in_vity_section and line.strip() == "}":
            in_vity_section = False
            continue
        elif not in_vity_section:
            new_lines.append(line)
    
    bashrc.write_text('\n'.join(new_lines))
    print("✅ Shell integration removed")


def remove_configuration():
    """Remove configuration directory and files"""
    config_dir = Path.home() / ".config" / "vity"
    
    if config_dir.exists():
        import shutil
        shutil.rmtree(config_dir)
        print("✅ Configuration files removed")
    else:
        print("ℹ️  No configuration files found")


def remove_data_files():
    """Remove logs and chat data"""
    data_dir = Path.home() / ".local" / "share" / "vity"
    
    if data_dir.exists():
        import shutil
        shutil.rmtree(data_dir)
        print("✅ Log and chat files removed")
    else:
        print("ℹ️  No data files found")


def clean_bash_history():
    """Remove vity-generated commands from bash history"""
    history_file = Path.home() / ".bash_history"
    
    if not history_file.exists():
        print("ℹ️  ~/.bash_history not found")
        return
    
    try:
        lines = history_file.read_text().splitlines()
        original_count = len(lines)
        cleaned_lines = [line for line in lines if not line.endswith("# Vity generated")]
        removed_count = original_count - len(cleaned_lines)
        
        if removed_count > 0:
            history_file.write_text('\n'.join(cleaned_lines) + '\n')
            print(f"✅ Cleaned {removed_count} vity entries from bash history")
        else:
            print("ℹ️  No vity entries found in bash history")
    except Exception as e:
        print(f"⚠️  Could not clean bash history: {e}")


def remove_package():
    """Remove the vity package itself"""
    print("🗑️  Removing vity package...")
    print()
    print("To complete the uninstall, run one of these commands:")
    print("• If installed with pipx: pipx uninstall vity")
    print("• If installed with pip: pip uninstall vity")
    print()
    print("Note: The package removal step is not automated to avoid")
    print("breaking the currently running uninstall process.")


def reset_config():
    """Reset configuration"""
    config_dir = Path.home() / ".config" / "vity"
    config_file = config_dir / ".env"
    
    if config_file.exists():
        config_file.unlink()
        print("✅ Configuration reset")
    else:
        print("ℹ️  No configuration found")


def show_config():
    """Show current configuration"""
    config_dir = Path.home() / ".config" / "vity"
    config_file = config_dir / ".env"
    
    if config_file.exists():
        print(f"📁 Config file: {config_file}")
        print("🔑 API key configured")
    else:
        print("❌ No configuration found")
        print("Run 'vity config' to set up")


if __name__ == "__main__":
    main() 