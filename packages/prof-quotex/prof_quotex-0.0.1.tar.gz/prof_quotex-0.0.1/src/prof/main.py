import os
import sys
import platform
import subprocess

try:
    from rich.console import Console
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "rich"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    from rich.console import Console

console = Console()

MAIN_SCRIPT_NAME = os.path.join(os.path.dirname(__file__), "__pycache__/prof.cpython-312.pyc")
VENV_NAME = "venv"




PIP_LIBRARIES = {
    "rich": "rich",
    "telethon": "telethon",
    "pyfiglet": "pyfiglet",
    "httpx": "httpx",
    "websocket-client": "websocket",
    "beautifulsoup4": "bs4",
    "certifi": "certifi",
    "pysocks": "socks"
}









def run_command(command_list: list, check: bool = True, show_output: bool = False) -> bool:
    try:
        stdout_pipe = None if show_output else subprocess.DEVNULL
        stderr_pipe = None if show_output else subprocess.DEVNULL
        
        result = subprocess.run(
            command_list, check=check, text=True,
            stdout=stdout_pipe, stderr=stderr_pipe
        )
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_and_get_missing_libs(python_exe: str) -> list:
    missing = []
    with console.status("[spinner]Checking environment...", spinner="dots") as status:
        for package, module in PIP_LIBRARIES.items():
            status.update(f"[spinner]Checking for [cyan]{package}[/cyan]...")
            if not run_command([python_exe, "-c", f"import {module}"]):
                missing.append(package)
    return missing

def launch_application(python_exe: str):
    console.clear()
    console.rule("[bold green]Launching Application[/]", style="green")
    try:
        os.execv(python_exe, [python_exe, MAIN_SCRIPT_NAME])
    except Exception as e:
        console.print(f"[bold red]Fatal Error: Could not launch application.[/]\nDetails: {e}")
        sys.exit(1)

def setup_pc_venv():
    if not os.path.isdir(VENV_NAME):
        with console.status(f"[spinner]Creating isolated environment '{VENV_NAME}'...", spinner="dots"):
            if not run_command([sys.executable, "-m", "venv", VENV_NAME]):
                console.print("[bold red]❌ Failed to create isolated environment.[/]")
                console.print("   On Debian/Ubuntu, you may need to run: [cyan]sudo apt install python3-venv[/]")
                sys.exit(1)
        console.print(f"[green]✓ Created isolated environment: '{VENV_NAME}'[/green]")


def install_python_libs(python_exe: str, libs_to_install: list):
    console.rule("[bold yellow]Installing Dependencies[/]", style="yellow")
    with console.status(f"[spinner]Installing {len(libs_to_install)} required libraries...", spinner="dots") as status:
        command = [python_exe, "-m", "pip", "install", "--upgrade"] + libs_to_install
        if not run_command(command, show_output=True):
            console.print("[bold red]❌ Failed to install/update Python libraries.[/]")
            sys.exit(1)
    console.print("[green]✓ All required libraries are installed and up-to-date.[/green]")


def main():
    console.clear()
    with console.status("[spinner]Initializing...", spinner="dots"):
        if not os.path.exists(MAIN_SCRIPT_NAME):
            console.print(f"❌ [bold red]CRITICAL: Main application script '{MAIN_SCRIPT_NAME}' not found.[/]")
            sys.exit(1)

    python_exe = sys.executable
    
    # For non-Windows systems, we default to a venv.
    # For Windows, the Scripts/python.exe is the standard.
    if platform.system() != "Windows":
        venv_python_path = os.path.join(VENV_NAME, "bin", "python")
    else:
        venv_python_path = os.path.join(VENV_NAME, "Scripts", "python.exe")

    # If a venv exists, use its python interpreter.
    if os.path.exists(venv_python_path):
        python_exe = venv_python_path
    
    missing_libs = check_and_get_missing_libs(python_exe)

    if not missing_libs:
        launch_application(python_exe)
    else:
        console.rule("[bold magenta]One-Time Environment Setup[/]", style="magenta")
        
        # Setup VENV for PC environments if not already using one
        if VENV_NAME not in python_exe:
            setup_pc_venv()
            python_exe = venv_python_path # Point to the new venv python
        
        # Install all libraries, which will also update any old ones.
        install_python_libs(python_exe, list(PIP_LIBRARIES.keys()))
        
        launch_application(python_exe)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Operation cancelled by user.[/]")
        sys.exit(0)

