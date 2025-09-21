from flask import Flask, render_template, request, jsonify
import json
import os
from terminal_core import PythonTerminal
from ai_interpreter import AICommandInterpreter

app = Flask(__name__)
terminal = PythonTerminal()
ai_interpreter = AICommandInterpreter()

# Store session data (in production, use proper session management)
sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_command():
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        session_id = data.get('session_id', 'default')
        ai_mode = data.get('ai_mode', False)
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        # Initialize session if not exists
        if session_id not in sessions:
            sessions[session_id] = {
                'terminal': PythonTerminal(),
                'ai_interpreter': AICommandInterpreter()
            }
        
        session_terminal = sessions[session_id]['terminal']
        session_ai = sessions[session_id]['ai_interpreter']
        
        if ai_mode:
            # Process AI command
            commands = session_ai.interpret(command)
            results = []
            
            for cmd in commands:
                output, return_code, error = session_terminal.execute_command(cmd)
                results.append({
                    'command': cmd,
                    'output': output,
                    'error': error,
                    'return_code': return_code
                })
                
                # Stop on error
                if return_code != 0 and return_code != -1:
                    break
            
            return jsonify({
                'success': True,
                'ai_mode': True,
                'original_command': command,
                'interpreted_commands': commands,
                'results': results,
                'current_directory': session_terminal.current_directory,
                'prompt': session_terminal.get_prompt()
            })
        else:
            # Process normal command
            output, return_code, error = session_terminal.execute_command(command)
            
            return jsonify({
                'success': True,
                'ai_mode': False,
                'command': command,
                'output': output,
                'error': error,
                'return_code': return_code,
                'current_directory': session_terminal.current_directory,
                'prompt': session_terminal.get_prompt()
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/system_info')
def system_info():
    try:
        session_id = request.args.get('session_id', 'default')
        
        if session_id not in sessions:
            sessions[session_id] = {
                'terminal': PythonTerminal(),
                'ai_interpreter': AICommandInterpreter()
            }
        
        session_terminal = sessions[session_id]['terminal']
        
        return jsonify({
            'current_directory': session_terminal.current_directory,
            'system_info': session_terminal.system_info,
            'prompt': session_terminal.get_prompt()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_web_interface():
    """Run the web interface"""
    print("Starting Python Terminal Web Interface...")
    print("Access the terminal at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    run_web_interface()
    
# Add this for Vercel compatibility
if __name__ != "__main__":
    # This runs when imported by Vercel
    pass