class PythonTerminal {
    constructor() {
        this.terminal = document.getElementById('terminal');
        this.commandInput = document.getElementById('command-input');
        this.prompt = document.getElementById('prompt');
        this.aiToggle = document.getElementById('ai-toggle');
        this.clearBtn = document.getElementById('clear-btn');
        
        this.aiMode = false;
        this.sessionId = this.generateSessionId();
        this.commandHistory = [];
        this.historyIndex = -1;
        
        this.init();
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }
    
    init() {
        this.commandInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        this.aiToggle.addEventListener('click', () => this.toggleAIMode());
        this.clearBtn.addEventListener('click', () => this.clearTerminal());
        
        // Focus on input
        this.commandInput.focus();
        
        // Load initial system info
        this.loadSystemInfo();
    }
    
    async loadSystemInfo() {
        try {
            const response = await fetch(`/system_info?session_id=${this.sessionId}`);
            const data = await response.json();
            
            if (data.prompt) {
                this.prompt.textContent = data.prompt;
            }
        } catch (error) {
            console.error('Error loading system info:', error);
        }
    }
    
    handleKeyDown(e) {
        switch (e.key) {
            case 'Enter':
                e.preventDefault();
                this.executeCommand();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.navigateHistory(-1);
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.navigateHistory(1);
                break;
            case 'Tab':
                e.preventDefault();
                // TODO: Implement tab completion
                break;
        }
    }
    
    navigateHistory(direction) {
        if (this.commandHistory.length === 0) return;
        
        if (direction === -1) {
            // Up arrow
            if (this.historyIndex < this.commandHistory.length - 1) {
                this.historyIndex++;
                this.commandInput.value = this.commandHistory[this.commandHistory.length - 1 - this.historyIndex];
            }
        } else {
            // Down arrow
            if (this.historyIndex > 0) {
                this.historyIndex--;
                this.commandInput.value = this.commandHistory[this.commandHistory.length - 1 - this.historyIndex];
            } else if (this.historyIndex === 0) {
                this.historyIndex = -1;
                this.commandInput.value = '';
            }
        }
    }
    
    async executeCommand() {
        const command = this.commandInput.value.trim();
        
        if (!command) return;
        
        // Add to history
        this.commandHistory.push(command);
        this.historyIndex = -1;
        
        // Show command in terminal
        this.addToTerminal(`${this.prompt.textContent}${command}`, 'command-executed');
        
        // Clear input
        this.commandInput.value = '';
        
        // Handle special commands
        if (command.toLowerCase() === 'clear') {
            this.clearTerminal();
            return;
        }
        
        try {
            const response = await fetch('/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    command: command,
                    session_id: this.sessionId,
                    ai_mode: this.aiMode
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.handleCommandResponse(data);
            } else {
                this.addToTerminal(data.error || 'Unknown error', 'error');
            }
        } catch (error) {
            this.addToTerminal(`Network error: ${error.message}`, 'error');
        }
    }
    
    handleCommandResponse(data) {
        if (data.ai_mode) {
            // AI mode response
            if (data.interpreted_commands && data.interpreted_commands.length > 0) {
                this.addToTerminal(`AI interpreted: "${data.original_command}"`, 'ai-interpretation');
                
                for (let i = 0; i < data.results.length; i++) {
                    const result = data.results[i];
                    this.addToTerminal(`→ ${result.command}`, 'info');
                    
                    if (result.output) {
                        this.addToTerminal(result.output, result.return_code === 0 ? 'success' : 'error');
                    }
                    
                    if (result.error) {
                        this.addToTerminal(result.error, 'error');
                    }
                }
            } else {
                this.addToTerminal('Could not interpret natural language command', 'error');
            }
        } else {
            // Normal mode response
            if (data.output) {
                this.addToTerminal(data.output, data.return_code === 0 ? 'success' : 'error');
            }
            
            if (data.error) {
                this.addToTerminal(data.error, 'error');
            }
        }
        
        // Update prompt
        if (data.prompt) {
            this.prompt.textContent = data.prompt;
        }
    }
    
    addToTerminal(text, className = '') {
        const output = document.createElement('div');
        output.className = `output ${className}`;
        output.textContent = text;
        
        // Insert before the command line
        const commandLine = this.terminal.querySelector('.command-line');
        this.terminal.insertBefore(output, commandLine);
        
        // Scroll to bottom
        this.terminal.scrollTop = this.terminal.scrollHeight;
    }
    
    toggleAIMode() {
        this.aiMode = !this.aiMode;
        
        if (this.aiMode) {
            this.aiToggle.textContent = 'AI Mode: ON';
            this.aiToggle.classList.add('active');
            this.addToTerminal('AI Mode enabled. Use natural language commands.', 'info');
            this.prompt.innerHTML = '<span style="color: #ff6b00;">[AI]</span> ' + this.prompt.textContent.replace('[AI] ', '');
        } else {
            this.aiToggle.textContent = 'AI Mode: OFF';
            this.aiToggle.classList.remove('active');
            this.addToTerminal('Normal terminal mode enabled.', 'info');
            this.prompt.textContent = this.prompt.textContent.replace('[AI] ', '');
        }
    }
    
    clearTerminal() {
        // Remove all output elements except welcome message and command line
        const outputs = this.terminal.querySelectorAll('.output');
        outputs.forEach(output => output.remove());
    }
}

// Initialize terminal when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PythonTerminal();
});