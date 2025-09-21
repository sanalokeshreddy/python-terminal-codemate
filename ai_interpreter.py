import re
from typing import Dict, List, Tuple
import os

class AICommandInterpreter:
    def __init__(self):
        self.command_patterns = {
            # File operations
            r"create (?:a )?(?:new )?(?:file|document) (?:called |named |with name )?['\"]?([^'\"]+)['\"]?": "touch {0}",
            r"make (?:a )?(?:new )?(?:file|document) (?:called |named |with name )?['\"]?([^'\"]+)['\"]?": "touch {0}",
            r"create (?:a )?(?:new )?(?:folder|directory) (?:called |named |with name )?['\"]?([^'\"]+)['\"]?": "mkdir {0}",
            r"make (?:a )?(?:new )?(?:folder|directory) (?:called |named |with name )?['\"]?([^'\"]+)['\"]?": "mkdir {0}",
            
            # File management
            r"delete (?:the )?(?:file|document) (?:called |named )?['\"]?([^'\"]+)['\"]?": "rm {0}",
            r"remove (?:the )?(?:file|document) (?:called |named )?['\"]?([^'\"]+)['\"]?": "rm {0}",
            r"delete (?:the )?(?:folder|directory) (?:called |named )?['\"]?([^'\"]+)['\"]?": "rm -r {0}",
            r"remove (?:the )?(?:folder|directory) (?:called |named )?['\"]?([^'\"]+)['\"]?": "rm -r {0}",
            
            # Copy operations
            r"copy ['\"]?([^'\"]+)['\"]? to (?:the )?['\"]?([^'\"]+)['\"]?(?: folder| directory)?": "cp {0} {1}",
            r"copy ['\"]?([^'\"]+)['\"]? into (?:the )?['\"]?([^'\"]+)['\"]?(?: folder| directory)?": "cp {0} {1}/",
            r"duplicate ['\"]?([^'\"]+)['\"]? (?:as |to |into )?['\"]?([^'\"]+)['\"]?": "cp {0} {1}",
            
            # Move operations  
            r"move ['\"]?([^'\"]+)['\"]? to (?:the )?['\"]?([^'\"]+)['\"]?(?: folder| directory)?": "mv {0} {1}",
            r"move ['\"]?([^'\"]+)['\"]? into (?:the )?['\"]?([^'\"]+)['\"]?(?: folder| directory)?": "mv {0} {1}/",
            r"rename ['\"]?([^'\"]+)['\"]? to ['\"]?([^'\"]+)['\"]?": "mv {0} {1}",
            
            # Navigation
            r"go to (?:the )?(?:folder|directory) (?:called |named )?['\"]?([^'\"]+)['\"]?": "cd {0}",
            r"change to (?:the )?(?:folder|directory) (?:called |named )?['\"]?([^'\"]+)['\"]?": "cd {0}",
            r"navigate to ['\"]?([^'\"]+)['\"]?": "cd {0}",
            r"(?:go|move) up": "cd ..",
            r"(?:go|move) back": "cd ..",
            r"go home": "cd ~",
            
            # Listing - FIXED PATTERNS
            r"(?:list|show)(?: me)?(?: all)?(?: the)? files": "ls",
            r"(?:list|show)(?: me)?(?: all)?(?: the)? contents": "ls",
            r"(?:list|show)(?: me)?(?: all)?(?: the)? items": "ls",
            r"what'?s (?:in )?(?:here|this folder|this directory)": "ls",
            r"list (?:all )?(?:files|contents) with details": "ls -la",
            r"show (?:all )?(?:files|contents) with details": "ls -la",
            r"list (?:all )?(?:files )?in (?:the )?(?:folder |directory )?(?:called |named )?['\"]?([^'\"]+)['\"]?": "ls {0}",
            r"show (?:me )?(?:all )?(?:files )?in (?:the )?(?:folder |directory )?(?:called |named )?['\"]?([^'\"]+)['\"]?": "ls {0}",
            
            # File viewing
            r"(?:show|display|read) (?:me )?(?:the )?(?:contents of |file )?['\"]?([^'\"]+)['\"]?": "cat {0}",
            r"open (?:the file )?['\"]?([^'\"]+)['\"]?": "cat {0}",
            
            # System info
            r"(?:show|display) (?:me )?(?:the )?(?:current )?(?:directory|folder|location)": "pwd",
            r"where am i": "pwd",
            r"(?:show|list) (?:running )?processes": "ps",
            r"(?:show|display) system (?:info|information|stats)": "top",
            
            # Clear screen
            r"clear (?:the )?screen": "clear",
            r"clean (?:the )?screen": "clear",
            r"clean up": "clear",
            
            # Help
            r"(?:show )?help": "help",
            r"what (?:can i do|commands are available)": "help",
        }
        
        self.multi_step_patterns = {
            r"create (?:a )?(?:new )?(?:folder|directory) (?:called |named )?['\"]?([^'\"]+)['\"]? and (?:move|put) ['\"]?([^'\"]+)['\"]? (?:into it|there|inside)": [
                "mkdir {0}",
                "mv {1} {0}/"
            ],
            r"make (?:a )?(?:new )?(?:folder|directory) ['\"]?([^'\"]+)['\"]? and (?:copy|put) ['\"]?([^'\"]+)['\"]? (?:into it|there|inside)": [
                "mkdir {0}",
                "cp {1} {0}/"
            ],
            r"create ['\"]?([^'\"]+)['\"]? (?:folder|directory) and move ['\"]?([^'\"]+)['\"]? (?:into it|there)": [
                "mkdir {0}",
                "mv {1} {0}/"
            ]
        }
    
    def interpret(self, natural_command: str) -> List[str]:
        """
        Convert natural language command to terminal command(s)
        Returns list of commands to execute
        """
        natural_command = natural_command.lower().strip()
        
        # Check multi-step patterns first
        for pattern, commands in self.multi_step_patterns.items():
            match = re.search(pattern, natural_command, re.IGNORECASE)
            if match:
                result = []
                for cmd_template in commands:
                    result.append(cmd_template.format(*match.groups()))
                return result
        
        # Check single-step patterns
        for pattern, command_template in self.command_patterns.items():
            match = re.search(pattern, natural_command, re.IGNORECASE)
            if match:
                try:
                    return [command_template.format(*match.groups())]
                except IndexError:
                    # Pattern matched but no groups captured
                    return [command_template]
        
        # If no pattern matches, return the original command
        return [natural_command]
    
    def suggest_commands(self, natural_command: str) -> List[str]:
        """Suggest possible commands based on keywords"""
        suggestions = []
        keywords = natural_command.lower().split()
        
        keyword_commands = {
            'file': ['ls', 'cat', 'touch', 'rm'],
            'folder': ['mkdir', 'ls', 'cd', 'rmdir'],
            'directory': ['mkdir', 'ls', 'cd', 'rmdir'],
            'create': ['mkdir', 'touch'],
            'delete': ['rm', 'rmdir'],
            'copy': ['cp'],
            'move': ['mv'],
            'list': ['ls', 'ps'],
            'show': ['ls', 'cat', 'pwd', 'ps', 'top'],
            'all': ['ls -la'],
            'files': ['ls', 'cat'],
            'contents': ['ls', 'cat']
        }
        
        for keyword in keywords:
            if keyword in keyword_commands:
                suggestions.extend(keyword_commands[keyword])
        
        return list(set(suggestions))  # Remove duplicates
    
    def get_help(self) -> str:
        """Get help text for natural language commands"""
        help_text = """
Natural Language Command Help:

File Operations:
- "create a file called test.txt" → touch test.txt
- "make a new folder named documents" → mkdir documents
- "delete the file readme.txt" → rm readme.txt
- "copy file1.txt to backup folder" → cp file1.txt backup/

Navigation:
- "go to the documents folder" → cd documents
- "go up" → cd ..
- "go home" → cd ~

Viewing:
- "list all files" → ls
- "show me all files" → ls
- "show the contents of file.txt" → cat file.txt
- "where am i" → pwd

System:
- "show running processes" → ps
- "clear the screen" → clear

Multi-step commands:
- "create a new folder called test and move file.txt into it"
  → mkdir test; mv file.txt test/
        """
        return help_text