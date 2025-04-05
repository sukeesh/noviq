#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import webbrowser
import signal

def print_colored(text, color="green"):
    colors = {
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "end": "\033[0m"
    }
    print(f"{colors.get(color, colors['green'])}{text}{colors['end']}")

def main():
    print_colored("Starting Noviq Research Interface", "blue")
    
    # Check if we're in a virtual environment
    if not os.environ.get('VIRTUAL_ENV'):
        print_colored("Warning: It appears you are not running in a virtual environment.", "yellow")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print_colored("Exiting...", "red")
            sys.exit(1)
    
    # Check if Ollama is running
    try:
        import requests
        requests.get("http://localhost:11434/api/tags", timeout=1)
        print_colored("✓ Ollama is running", "green")
    except:
        print_colored("✗ Ollama is not running or not accessible.", "red")
        print_colored("Please start Ollama first with 'ollama serve'", "yellow")
        sys.exit(1)
    
    # Check if required packages are installed
    required_packages = ["fastapi", "uvicorn", "dspy", "ollama", "inquirer"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print_colored(f"✗ Required package '{package}' is not installed.", "red")
            print_colored(f"Please install it with 'pip install {package}'", "yellow")
            sys.exit(1)
    
    processes = []
    
    try:
        # Start backend server in a new process
        print_colored("Starting backend server...", "blue")
        backend_cmd = [sys.executable, "-m", "noviq.backend.server"]
        backend_process = subprocess.Popen(
            backend_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        processes.append(backend_process)
        
        # Give the backend a moment to start
        time.sleep(2)
        
        # Check if backend started successfully
        if backend_process.poll() is not None:
            print_colored("✗ Backend failed to start!", "red")
            stdout, stderr = backend_process.communicate()
            print_colored("Error:", "red")
            print(stderr)
            print(stdout)
            sys.exit(1)
        
        print_colored("✓ Backend server started on port 8001", "green")
        
        # Start frontend in a new process
        print_colored("Starting frontend server...", "blue")
        os.chdir("ui")
        frontend_cmd = "npm start"
        if os.name == 'nt':  # Windows
            frontend_process = subprocess.Popen(
                frontend_cmd, 
                shell=True, 
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:  # Unix/Mac
            frontend_process = subprocess.Popen(
                frontend_cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
        processes.append(frontend_process)
        
        print_colored("✓ Frontend server starting", "green")
        print_colored("Noviq will open in your browser shortly...", "blue")
        
        # Give the frontend a moment to start
        time.sleep(5)
        
        # Open browser
        webbrowser.open("http://localhost:3000")
        
        print_colored("Noviq is now running!", "green")
        print_colored("Press Ctrl+C to stop all servers", "yellow")
        
        # Keep the script running
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print_colored("\nShutting down Noviq...", "yellow")
    finally:
        # Clean up processes
        for process in processes:
            if process.poll() is None:  # If process is still running
                if os.name == 'nt':  # Windows
                    process.terminate()
                else:  # Unix/Mac
                    process.send_signal(signal.SIGTERM)
                    
        print_colored("Noviq has been stopped.", "blue")

if __name__ == "__main__":
    main() 