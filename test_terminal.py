#!/usr/bin/env python3
"""
Quick test script to verify terminal functionality
"""

from terminal_core import PythonTerminal
from ai_interpreter import AICommandInterpreter

def test_terminal():
    print("Testing Python Terminal...")
    terminal = PythonTerminal()
    ai = AICommandInterpreter()
    
    # Test basic commands
    test_commands = [
        'help',
        'pwd',
        'mkdir test_folder',
        'cd test_folder',
        'echo "Hello World" > test.txt',
        'cat test.txt',
        'ls -la',
        'cd ..',
        'rm -r test_folder'
    ]
    
    print("\n=== Testing Basic Commands ===")
    for cmd in test_commands:
        print(f"\n> {cmd}")
        output, return_code, error = terminal.execute_command(cmd)
        
        if return_code == 0:
            if output and not output.startswith("terminal_command:"):
                print(output)
        else:
            if error:
                print(f"Error: {error}")
            if output:
                print(output)
    
    # Test AI commands with better examples
    print("\n=== Testing AI Commands ===")
    ai_commands = [
        "create a folder called test_docs",
        "show me all files",
        "list all files",  # This should work better
        "show all files",  # Alternative phrasing
        "list files in test_docs folder"
    ]
    
    for natural_cmd in ai_commands:
        print(f"\nAI: '{natural_cmd}'")
        interpreted = ai.interpret(natural_cmd)
        print(f"Interpreted as: {interpreted}")
        
        for cmd in interpreted:
            output, return_code, error = terminal.execute_command(cmd)
            if return_code == 0 and output and not output.startswith("terminal_command:"):
                print(f"  Result: {output}")
            elif error:
                print(f"  Error: {error}")
    
    # Clean up test folder
    terminal.execute_command("rm -r test_docs")
    print("\nTest completed!")

if __name__ == "__main__":
    test_terminal()