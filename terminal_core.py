import os
import sys
import subprocess
import platform
from typing import Dict, List, Tuple
from colorama import Fore, Back, Style, init
import psutil
import shlex

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class PythonTerminal:
    def __init__(self):
        self.current_directory = os.getcwd()
        self.command_history = []
        self.environment_vars = os.environ.copy()
        self.aliases = {}
        self.system_info = self._get_system_info()
        
    def _get_system_info(self) -> Dict:
        """Get basic system information"""
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
    
    def execute_command(self, command: str) -> Tuple[str, int, str]:
        """
        Execute a command and return output, return code, and error
        Returns: (output, return_code, error)
        """
        if not command.strip():
            return "", 0, ""
        
        # Add to history
        self.command_history.append(command)
        
        # Parse command
        try:
            parts = shlex.split(command)
        except ValueError as e:
            return "", 1, f"Command parsing error: {str(e)}"
        
        if not parts:
            return "", 0, ""
            
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Handle built-in commands first
        if cmd in ['cd', 'pwd', 'ls', 'dir', 'mkdir', 'rmdir', 'rm', 'del', 
                   'cp', 'copy', 'mv', 'move', 'cat', 'type', 'echo', 'touch', 'set', 
                   'export', 'alias', 'history', 'clear', 'cls', 'exit', 'quit', 'help']:
            return self._handle_builtin_command(cmd, args)
        
        # Handle special terminal commands
        if cmd in ['ai', 'normal']:
            return f"terminal_command:{cmd}", 0, ""
        
        # Handle system monitoring commands
        if cmd in ['ps', 'top', 'htop', 'tasklist', 'kill', 'taskkill']:
            return self._handle_system_command(cmd, args)
        
        # Execute external command
        return self._execute_external_command(command)
    
    def _handle_builtin_command(self, cmd: str, args: List[str]) -> Tuple[str, int, str]:
        """Handle built-in terminal commands"""
        try:
            if cmd == 'cd':
                return self._cmd_cd(args)
            elif cmd == 'pwd':
                return self.current_directory, 0, ""
            elif cmd in ['ls', 'dir']:
                return self._cmd_ls(args)
            elif cmd == 'mkdir':
                return self._cmd_mkdir(args)
            elif cmd in ['rmdir', 'rm', 'del']:
                return self._cmd_remove(args)
            elif cmd in ['cp', 'copy']:
                return self._cmd_copy(args)
            elif cmd in ['mv', 'move']:
                return self._cmd_move(args)
            elif cmd in ['cat', 'type']:
                return self._cmd_cat(args)
            elif cmd == 'echo':
                return self._cmd_echo(args)
            elif cmd == 'touch':
                return self._cmd_touch(args)
            elif cmd in ['set', 'export']:
                return self._cmd_set_env(args)
            elif cmd == 'alias':
                return self._cmd_alias(args)
            elif cmd == 'history':
                return self._cmd_history(args)
            elif cmd in ['clear', 'cls']:
                return "\033[2J\033[H", 0, ""  # Clear screen ANSI codes
            elif cmd == 'help':
                return self._cmd_help(args)
            elif cmd in ['exit', 'quit']:
                return "exit", -1, ""
            else:
                return "", 1, f"Unknown built-in command: {cmd}"
                
        except Exception as e:
            return "", 1, str(e)

    def _cmd_cd(self, args: List[str]) -> Tuple[str, int, str]:
        """Change directory command"""
        if not args:
            # Go to home directory
            target = os.path.expanduser("~")
        elif args[0] == "..":
            target = os.path.dirname(self.current_directory)
        elif args[0] == ".":
            target = self.current_directory
        else:
            if os.path.isabs(args[0]):
                target = args[0]
            else:
                target = os.path.join(self.current_directory, args[0])
        
        if os.path.exists(target) and os.path.isdir(target):
            self.current_directory = os.path.abspath(target)
            os.chdir(self.current_directory)
            return self.current_directory, 0, ""
        else:
            return "", 1, f"cd: no such file or directory: {args[0]}"
    
    def _cmd_ls(self, args: List[str]) -> Tuple[str, int, str]:
        """List directory contents"""
        show_hidden = '-a' in args or '--all' in args
        long_format = '-l' in args or '--long' in args
        
        # Filter out flags to get path
        paths = [arg for arg in args if not arg.startswith('-')]
        target_dir = paths[0] if paths else self.current_directory
        
        if not os.path.isabs(target_dir):
            target_dir = os.path.join(self.current_directory, target_dir)
        
        if not os.path.exists(target_dir):
            return "", 1, f"ls: cannot access '{target_dir}': No such file or directory"
        
        if os.path.isfile(target_dir):
            return target_dir, 0, ""
        
        try:
            items = os.listdir(target_dir)
            if not show_hidden:
                items = [item for item in items if not item.startswith('.')]
            
            items.sort()
            
            if long_format:
                output = []
                for item in items:
                    item_path = os.path.join(target_dir, item)
                    stat_info = os.stat(item_path)
                    is_dir = os.path.isdir(item_path)
                    permissions = 'drwxrwxrwx' if is_dir else '-rw-rw-rw-'
                    size = stat_info.st_size
                    output.append(f"{permissions} {size:8d} {item}")
                return '\n'.join(output), 0, ""
            else:
                return '  '.join(items), 0, ""
                
        except PermissionError:
            return "", 1, f"ls: cannot open directory '{target_dir}': Permission denied"
        except Exception as e:
            return "", 1, str(e)
    
    def _cmd_mkdir(self, args: List[str]) -> Tuple[str, int, str]:
        """Create directory"""
        if not args:
            return "", 1, "mkdir: missing operand"
        
        create_parents = '-p' in args or '--parents' in args
        dirs_to_create = [arg for arg in args if not arg.startswith('-')]
        
        for dir_name in dirs_to_create:
            if not os.path.isabs(dir_name):
                dir_path = os.path.join(self.current_directory, dir_name)
            else:
                dir_path = dir_name
                
            try:
                if create_parents:
                    os.makedirs(dir_path, exist_ok=True)
                else:
                    os.mkdir(dir_path)
            except FileExistsError:
                return "", 1, f"mkdir: cannot create directory '{dir_name}': File exists"
            except Exception as e:
                return "", 1, f"mkdir: cannot create directory '{dir_name}': {str(e)}"
        
        return f"Created directory: {', '.join(dirs_to_create)}", 0, ""
    
    def _cmd_remove(self, args: List[str]) -> Tuple[str, int, str]:
        """Remove files/directories"""
        if not args:
            return "", 1, "rm: missing operand"
        
        recursive = '-r' in args or '-R' in args or '--recursive' in args
        force = '-f' in args or '--force' in args
        items_to_remove = [arg for arg in args if not arg.startswith('-')]
        
        removed_items = []
        for item in items_to_remove:
            if not os.path.isabs(item):
                item_path = os.path.join(self.current_directory, item)
            else:
                item_path = item
            
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    removed_items.append(item)
                elif os.path.isdir(item_path):
                    if recursive:
                        import shutil
                        shutil.rmtree(item_path)
                        removed_items.append(item)
                    else:
                        return "", 1, f"rm: cannot remove '{item}': Is a directory"
                else:
                    if not force:
                        return "", 1, f"rm: cannot remove '{item}': No such file or directory"
            except Exception as e:
                if not force:
                    return "", 1, f"rm: cannot remove '{item}': {str(e)}"
        
        return f"Removed: {', '.join(removed_items)}" if removed_items else "", 0, ""
    
    def _cmd_copy(self, args: List[str]) -> Tuple[str, int, str]:
        """Copy files/directories"""
        if len(args) < 2:
            return "", 1, "cp: missing destination file operand"
        
        source = args[0]
        destination = args[1]
        
        if not os.path.isabs(source):
            source = os.path.join(self.current_directory, source)
        if not os.path.isabs(destination):
            destination = os.path.join(self.current_directory, destination)
        
        try:
            import shutil
            if os.path.isfile(source):
                shutil.copy2(source, destination)
            elif os.path.isdir(source):
                shutil.copytree(source, destination)
            else:
                return "", 1, f"cp: cannot stat '{args[0]}': No such file or directory"
            
            return f"Copied {args[0]} to {args[1]}", 0, ""
        except Exception as e:
            return "", 1, f"cp: {str(e)}"
    
    def _cmd_move(self, args: List[str]) -> Tuple[str, int, str]:
        """Move/rename files/directories"""
        if len(args) < 2:
            return "", 1, "mv: missing destination file operand"
        
        source = args[0]
        destination = args[1]
        
        if not os.path.isabs(source):
            source = os.path.join(self.current_directory, source)
        if not os.path.isabs(destination):
            destination = os.path.join(self.current_directory, destination)
        
        try:
            import shutil
            shutil.move(source, destination)
            return f"Moved {args[0]} to {args[1]}", 0, ""
        except Exception as e:
            return "", 1, f"mv: {str(e)}"
    
    def _cmd_cat(self, args: List[str]) -> Tuple[str, int, str]:
        """Display file contents"""
        if not args:
            return "", 1, "cat: missing file operand"
        
        output = []
        for file_name in args:
            if not os.path.isabs(file_name):
                file_path = os.path.join(self.current_directory, file_name)
            else:
                file_path = file_name
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    output.append(content)
            except FileNotFoundError:
                return "", 1, f"cat: {file_name}: No such file or directory"
            except PermissionError:
                return "", 1, f"cat: {file_name}: Permission denied"
            except Exception as e:
                return "", 1, f"cat: {file_name}: {str(e)}"
        
        return '\n'.join(output), 0, ""
    
    def _cmd_echo(self, args: List[str]) -> Tuple[str, int, str]:
        """Echo command with file redirection support"""
        if not args:
            return "", 0, ""
        
        # Join all arguments
        text = ' '.join(args)
        
        # Check for output redirection
        if '>' in text:
            parts = text.split('>', 1)
            content = parts[0].strip().strip('"\'')
            filename = parts[1].strip()
            
            # Handle file path
            if not os.path.isabs(filename):
                filepath = os.path.join(self.current_directory, filename)
            else:
                filepath = filename
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"Content written to {filename}", 0, ""
            except Exception as e:
                return "", 1, f"echo: cannot write to '{filename}': {str(e)}"
        else:
            # Just echo the text
            return text.strip('"\''), 0, ""
    
    def _cmd_touch(self, args: List[str]) -> Tuple[str, int, str]:
        """Create empty file(s)"""
        if not args:
            return "", 1, "touch: missing file operand"
        
        created_files = []
        for filename in args:
            if not os.path.isabs(filename):
                filepath = os.path.join(self.current_directory, filename)
            else:
                filepath = filename
            
            try:
                # Create the file (or update timestamp if exists)
                with open(filepath, 'a', encoding='utf-8'):
                    pass
                created_files.append(filename)
            except Exception as e:
                return "", 1, f"touch: cannot create '{filename}': {str(e)}"
        
        return f"Created/updated: {', '.join(created_files)}", 0, ""
    
    def _cmd_help(self, args: List[str]) -> Tuple[str, int, str]:
        """Show help for built-in commands"""
        help_text = f"""
Available Commands:

File Operations:
  ls, dir       - List directory contents
  cd <path>     - Change directory  
  pwd           - Print working directory
  mkdir <n>  - Create directory
  rmdir <n>  - Remove empty directory
  rm <file>     - Remove file/directory (-r for recursive)
  cp <src> <dst> - Copy file/directory
  mv <src> <dst> - Move/rename file/directory
  cat <file>    - Display file contents
  touch <file>  - Create empty file or update timestamp
  echo <text>   - Display text (use > filename to redirect to file)

System Monitoring:
  ps            - List running processes
  top           - Show system information and top processes
  kill <pid>    - Terminate process by PID

Terminal Features:
  history       - Show command history
  clear, cls    - Clear screen
  alias         - Create command aliases
  set, export   - Set environment variables
  help          - Show this help message
  exit, quit    - Exit the terminal

Examples:
  echo "Hello World" > test.txt    - Create file with content
  ls -la                           - List all files with details
  mkdir -p dir1/dir2              - Create nested directories
  rm -r folder                    - Remove folder recursively
  cp *.txt backup/                - Copy all txt files to backup
  ps                              - Show running processes
  top                             - Show system stats

AI Mode:
  Type 'ai' to enable natural language commands
  Example: "create a folder called documents"
        """
        return help_text.strip(), 0, ""
    
    def _cmd_set_env(self, args: List[str]) -> Tuple[str, int, str]:
        """Set environment variable"""
        if not args:
            # Show all environment variables
            env_vars = []
            for key, value in sorted(self.environment_vars.items()):
                env_vars.append(f"{key}={value}")
            return '\n'.join(env_vars), 0, ""
        
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                self.environment_vars[key] = value
                os.environ[key] = value
            else:
                # Show specific variable
                if arg in self.environment_vars:
                    return f"{arg}={self.environment_vars[arg]}", 0, ""
                else:
                    return "", 1, f"Variable '{arg}' not found"
        
        return "Environment variable(s) set", 0, ""
    
    def _cmd_alias(self, args: List[str]) -> Tuple[str, int, str]:
        """Create command alias"""
        if not args:
            # Show all aliases
            if not self.aliases:
                return "No aliases defined", 0, ""
            
            alias_list = []
            for alias, command in self.aliases.items():
                alias_list.append(f"alias {alias}='{command}'")
            return '\n'.join(alias_list), 0, ""
        
        for arg in args:
            if '=' in arg:
                alias, command = arg.split('=', 1)
                self.aliases[alias] = command.strip('"\'')
            else:
                if arg in self.aliases:
                    return f"alias {arg}='{self.aliases[arg]}'", 0, ""
                else:
                    return "", 1, f"Alias '{arg}' not found"
        
        return "Alias(es) created", 0, ""
    
    def _cmd_history(self, args: List[str]) -> Tuple[str, int, str]:
        """Show command history"""
        if not self.command_history:
            return "No commands in history", 0, ""
        
        numbered_history = []
        for i, cmd in enumerate(self.command_history, 1):
            numbered_history.append(f"{i:4d}  {cmd}")
        
        return '\n'.join(numbered_history), 0, ""
    
    def _handle_system_command(self, cmd: str, args: List[str]) -> Tuple[str, int, str]:
        """Handle system monitoring commands"""
        try:
            if cmd in ['ps', 'tasklist']:
                return self._cmd_ps(args)
            elif cmd in ['top', 'htop']:
                return self._cmd_top(args)
            elif cmd in ['kill', 'taskkill']:
                return self._cmd_kill(args)
            else:
                return "", 1, f"Unknown system command: {cmd}"
        except Exception as e:
            return "", 1, str(e)
    
    def _cmd_ps(self, args: List[str]) -> Tuple[str, int, str]:
        """List running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    processes.append(f"{proc_info['pid']:8d} {proc_info['name']:20s} "
                                   f"CPU: {proc_info['cpu_percent']:5.1f}% "
                                   f"MEM: {proc_info['memory_percent']:5.1f}%")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not processes:
                return "No processes found", 0, ""
            
            header = f"{'PID':8s} {'NAME':20s} {'CPU':12s} {'MEMORY':10s}"
            return header + '\n' + '\n'.join(processes), 0, ""
            
        except Exception as e:
            return "", 1, f"ps: {str(e)}"
    
    def _cmd_top(self, args: List[str]) -> Tuple[str, int, str]:
        """Show system information and top processes"""
        try:
            # System info
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_info = [
                f"CPU Usage: {cpu_percent:.1f}%",
                f"Memory Usage: {memory.percent:.1f}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)",
                f"Disk Usage: {disk.percent:.1f}% ({disk.used // 1024 // 1024 // 1024}GB / {disk.total // 1024 // 1024 // 1024}GB)",
                "",
                f"{'PID':8s} {'NAME':20s} {'CPU%':8s} {'MEM%':8s}",
                "-" * 50
            ]
            
            # Top processes by CPU usage
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    processes.append((proc_info['pid'], proc_info['name'], 
                                    proc_info['cpu_percent'], proc_info['memory_percent']))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage and take top 10
            processes.sort(key=lambda x: x[2], reverse=True)
            top_processes = processes[:10]
            
            for pid, name, cpu, mem in top_processes:
                system_info.append(f"{pid:8d} {name[:19]:20s} {cpu:7.1f} {mem:7.1f}")
            
            return '\n'.join(system_info), 0, ""
            
        except Exception as e:
            return "", 1, f"top: {str(e)}"
    
    def _cmd_kill(self, args: List[str]) -> Tuple[str, int, str]:
        """Kill process by PID"""
        if not args:
            return "", 1, "kill: missing process ID"
        
        try:
            pid = int(args[0])
            proc = psutil.Process(pid)
            proc.terminate()
            return f"Process {pid} terminated", 0, ""
        except ValueError:
            return "", 1, f"kill: invalid process ID '{args[0]}'"
        except psutil.NoSuchProcess:
            return "", 1, f"kill: no such process: {args[0]}"
        except psutil.AccessDenied:
            return "", 1, f"kill: permission denied: {args[0]}"
        except Exception as e:
            return "", 1, f"kill: {str(e)}"
    
    def _execute_external_command(self, command: str) -> Tuple[str, int, str]:
        """Execute external system command"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.current_directory,
                env=self.environment_vars,
                timeout=30
            )
            
            return result.stdout, result.returncode, result.stderr
            
        except subprocess.TimeoutExpired:
            return "", 1, "Command timed out after 30 seconds"
        except Exception as e:
            return "", 1, str(e)
    
    def get_prompt(self) -> str:
        """Get command prompt string"""
        user = os.getenv('USER', os.getenv('USERNAME', 'user'))
        hostname = platform.node()
        current_dir = os.path.basename(self.current_directory) or self.current_directory
        
        return f"{user}@{hostname}:{current_dir}$ "