#!/usr/bin/env python3
"""
Python Terminal - A fully functional command terminal built in Python
"""

import sys
import os
from typing import Optional
from colorama import Fore, Back, Style, init
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.formatted_text import HTML

from terminal_core import PythonTerminal
from ai_interpreter import AICommandInterpreter

# Initialize colorama
init(autoreset=True)

class TerminalInterface:
    def __init__(self):
        self.terminal = PythonTerminal()
        self.ai_interpreter = AICommandInterpreter()
        self.history = InMemoryHistory()
        self.ai_mode = False
        
        # Command completion
        self.commands = [
            'ls', 'cd', 'pwd', 'mkdir', 'rmdir', 'rm', 'cp', 'mv', 'cat', 'echo', 'touch',
            'clear', 'exit', 'quit', 'ps', 'top', 'kill', 'history', 'alias',
            'set', 'export', 'help', 'ai', 'normal'
        ]
        self.completer = WordCompleter(self.commands)
    
    def print_welcome(self):
        """Print welcome message"""
        welcome_text = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    Python Terminal v1.0                     ║
║              A fully functional command terminal             ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.YELLOW}Features:{Style.RESET_ALL}
• Full file and directory operations
• System monitoring (processes, CPU, memory)
• AI-powered natural language commands
• Command history and auto-completion
• Cross-platform compatibility

{Fore.GREEN}Type 'help' for available commands or 'ai' to enable AI mode{Style.RESET_ALL}
{Fore.GREEN}Type 'exit' or 'quit' to exit the terminal{Style.RESET_ALL}

"""
        print(welcome_text)
    
    def print_help(self):
        """Print help message"""
        help_text = f"""
{Fore.CYAN}Available Commands:{Style.RESET_ALL}

{Fore.YELLOW}File Operations:{Style.RESET_ALL}
  ls, dir       - List directory contents
  cd <path>     - Change directory
  pwd           - Print working directory
  mkdir <name>  - Create directory
  rmdir <name>  - Remove empty directory
  rm <file>     - Remove file/directory (-r for recursive)
  cp <src> <dst> - Copy file/directory
  mv <src> <dst> - Move/rename file/directory
  cat <file>    - Display file contents
  touch <file>  - Create empty file or update timestamp
  echo <text>   - Display text (use > filename to redirect to file)

{Fore.YELLOW}System Monitoring:{Style.RESET_ALL}
  ps            - List running processes
  top           - Show system information and top processes
  kill <pid>    - Terminate process by PID

{Fore.YELLOW}Terminal Features:{Style.RESET_ALL}
  history       - Show command history
  clear, cls    - Clear screen
  alias         - Create command aliases
  set, export   - Set environment variables
  help          - Show this help message
  
{Fore.YELLOW}AI Features:{Style.RESET_ALL}
  ai            - Enter AI natural language mode
  normal        - Exit AI mode (return to normal terminal)
  
{Fore.YELLOW}Examples:{Style.RESET_ALL}
  echo "Hello World" > test.txt    - Create file with content
  ls -la                           - List all files with details
  mkdir -p dir1/dir2              - Create nested directories
  rm -r folder                    - Remove folder recursively
  cp *.txt backup/                - Copy all txt files to backup
  ps                              - Show running processes
  top                             - Show system stats

{Fore.GREEN}In AI mode, you can use natural language:{Style.RESET_ALL}
  "create a new folder called test"
  "copy file.txt to backup folder"
  "show me all files in this directory"
  "list all files"
"""
        print(help_text)
    
    def run_cli(self):
        """Run the command line interface"""
        self.print_welcome()
        
        try:
            while True:
                try:
                    # Get prompt
                    prompt_text = self.get_prompt()
                    
                    # Get user input with auto-completion and history
                    user_input = prompt(
                        prompt_text,
                        completer=self.completer,
                        history=self.history
                    ).strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle special commands first
                    if user_input.lower() in ['exit', 'quit']:
                        print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
                        break
                    elif user_input.lower() == 'help':
                        self.print_help()
                        continue
                    elif user_input.lower() == 'ai':
                        self.ai_mode = True
                        print(f"{Fore.CYAN}AI Mode enabled. Use natural language commands.{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}Type 'normal' to return to standard terminal mode.{Style.RESET_ALL}")
                        continue
                    elif user_input.lower() == 'normal':
                        self.ai_mode = False
                        print(f"{Fore.CYAN}Normal terminal mode enabled.{Style.RESET_ALL}")
                        continue
                    
                    # Process command based on mode
                    if self.ai_mode:
                        self.process_ai_command(user_input)
                    else:
                        self.process_normal_command(user_input)
                        
                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}Use 'exit' or 'quit' to exit the terminal{Style.RESET_ALL}")
                    continue
                except EOFError:
                    print(f"\n{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
                    break
                    
        except Exception as e:
            print(f"{Fore.RED}Fatal error: {str(e)}{Style.RESET_ALL}")
            sys.exit(1)
    
    def get_prompt(self) -> str:
        """Get the command prompt"""
        base_prompt = self.terminal.get_prompt()
        if self.ai_mode:
            return f"{Fore.MAGENTA}[AI] {Style.RESET_ALL}{base_prompt}"
        else:
            return f"{Fore.GREEN}{base_prompt}{Style.RESET_ALL}"
    
    def process_normal_command(self, command: str):
        """Process a normal terminal command"""
        output, return_code, error = self.terminal.execute_command(command)
        
        if return_code == -1:  # Exit command
            sys.exit(0)
        elif return_code == 0:
            if output:
                # Check for special terminal commands
                if output.startswith("terminal_command:"):
                    cmd = output.split(":", 1)[1]
                    if cmd == "ai":
                        self.ai_mode = True
                        print(f"{Fore.CYAN}AI Mode enabled. Use natural language commands.{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}Type 'normal' to return to standard terminal mode.{Style.RESET_ALL}")
                    elif cmd == "normal":
                        self.ai_mode = False
                        print(f"{Fore.CYAN}Normal terminal mode enabled.{Style.RESET_ALL}")
                else:
                    print(output)
        else:
            if error:
                print(f"{Fore.RED}{error}{Style.RESET_ALL}")
            if output:
                print(output)
    
    def process_ai_command(self, natural_command: str):
        """Process an AI natural language command"""
        # Special AI mode commands
        if natural_command.lower() in ['help ai', 'ai help']:
            print(self.ai_interpreter.get_help())
            return
        
        # Interpret natural language
        commands = self.ai_interpreter.interpret(natural_command)
        
        if len(commands) == 1 and commands[0] == natural_command:
            # No interpretation found, suggest commands
            suggestions = self.ai_interpreter.suggest_commands(natural_command)
            if suggestions:
                print(f"{Fore.YELLOW}Could not interpret command. Did you mean:{Style.RESET_ALL}")
                for suggestion in suggestions[:3]:  # Show top 3 suggestions
                    print(f"  • {suggestion}")
            else:
                print(f"{Fore.YELLOW}Could not interpret natural language command.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Trying to execute as regular command...{Style.RESET_ALL}")
                self.process_normal_command(natural_command)
        else:
            # Execute interpreted commands
            for i, cmd in enumerate(commands):
                print(f"{Fore.CYAN}Executing: {cmd}{Style.RESET_ALL}")
                output, return_code, error = self.terminal.execute_command(cmd)
                
                if return_code == 0:
                    if output:
                        print(output)
                else:
                    if error:
                        print(f"{Fore.RED}{error}{Style.RESET_ALL}")
                    if output:
                        print(output)
                    # Stop execution on error
                    if i < len(commands) - 1:
                        print(f"{Fore.YELLOW}Stopping execution due to error{Style.RESET_ALL}")
                        break

def main():
    """Main function"""
    try:
        # Check if web interface is requested
        if len(sys.argv) > 1 and sys.argv[1] == '--web':
            from web_interface import run_web_interface
            run_web_interface()
        else:
            # Run CLI interface
            terminal_interface = TerminalInterface()
            terminal_interface.run_cli()
    except KeyboardInterrupt:
        print(f"\n{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}Error starting terminal: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    main()