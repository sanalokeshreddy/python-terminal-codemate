# 🐍 Python Command Terminal

A fully functional command terminal built from the ground up in Python, featuring an AI-powered natural language command interpreter and a responsive web interface. This project was developed as a submission for the **#SRMHacksWithCodemate** Hackathon.

**Live Demo:** https://python-terminal-codemate.onrender.com/

## 🌟 Core Features

* **Complete Terminal Functionality**: Implements all standard terminal commands (`ls`, `cd`, `pwd`, `mkdir`, `rm`, `cp`, `mv`, `cat`, etc.) with custom Python logic.
* **Live System Monitoring**: Provides real-time insights into system health with integrated process management (`ps`, `kill`) and resource monitoring (`top`) powered by `psutil`.
* **🧠 AI-Powered Natural Language Processing**: The standout feature. Switch to "AI mode" and give commands in plain English (e.g., *"create a new folder called 'documents' and move my 'report.txt' file into it"*). The system interprets this and executes the correct sequence of shell commands.
* **Dual Interface**:
   * A feature-rich **Command-Line Interface (CLI)** with command history and auto-completion.
   * A clean, responsive **Web-Based Interface** built with Flask, accessible from any browser.
* **Cross-Platform**: Designed to work seamlessly on Windows, macOS, and Linux.

## 🛠️ Tech Stack

* **Backend**: Python, Flask
* **System Interaction**: `os`, `shutil`, `subprocess`, `psutil`
* **CLI Enhancement**: `prompt_toolkit`, `colorama`
* **Deployment**: Render

## 🚀 Getting Started

Follow these instructions to get the terminal running on your local machine.

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/python-terminal-codemate.git
cd python-terminal-codemate
```

*(Replace `your-username` with your actual GitHub username)*

### 2. Create and Activate a Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies and avoid conflicts.

```bash
# Create the virtual environment
python -m venv terminal_env

# Activate the environment
# On Windows (PowerShell):
.\terminal_env\Scripts\Activate.ps1

# On macOS/Linux:
source terminal_env/bin/activate
```

### 3. Install Dependencies

Install all the required Python packages using `pip`.

```bash
pip install -r requirements.txt
```

### 4. Run the Application

You can run the application in two modes:

#### As a Command-Line Interface (CLI)
This is the recommended mode for a traditional terminal experience.

```bash
python main.py
```

#### As a Web Interface
This will start a local web server, allowing you to access the terminal in your browser.

```bash
python main.py --web
```

Navigate to `http://127.0.0.1:5000` in your web browser to start using the terminal.
