from pathlib import Path
import json
import sys
import google.generativeai as genai
# from dotenv import load_dotenv
from aiassistcli.ai_prompt import build_prompt
import questionary
from rich.console import Console

CONFIG_DIR = Path.home() / ".ai-assist"
CONFIG_PATH = CONFIG_DIR / "config.json"

# 🎨 Custom style for questionary
custom_style = questionary.Style([
   ('qmark', 'fg:#673ab7 bold'),        
    ('question', 'bold'),               
    ('answer', 'fg:#f44336 bold'),      
    ('pointer', 'fg:#673ab7 bold'),     
    ('highlighted', 'fg:#673ab7 bold'), 
    ('selected', 'fg:#cc5454'),         
    ('separator', 'fg:#cc5454'),        
    ('instruction', ''),               
    ('text', ''),                      
    ('disabled', 'fg:#858585 italic')
])

console = Console()

def save_api_key(key: str):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps({"api_key": key}))
    
    # secure file permissions (Linux/macOS)
    # CONFIG_PATH.chmod(stat.S_IRUSR | stat.S_IWUSR)  # rw-------

def load_api_key() -> str | None:
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text())
            return data.get("api_key")
        except Exception:
            return None
    return None

def get_command_from_ai(prompt, api_key):

    # Configure Gemini with the provided API key
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(build_prompt(prompt))
    return response.text.strip()
    
def explain_command_with_ai(command: str, api_key: str) -> str:
    prompt = f"""
    Generate the same CLI command as: {command}
    Add brief inline comments to each line explaining what it does.
    Only output the command with the comments, no extra explanation.
    """
    return get_command_from_ai(prompt, api_key)

def configure():
    try:
        api_key = questionary.password("🔐 Enter your Gemini API key:", style=custom_style).ask()
    except KeyboardInterrupt:
        sys.exit(1)
        
    if not api_key:
        console.print("[red]❗ No API key entered.[/red]")
        sys.exit(1)
    save_api_key(api_key)
    console.print("[green]✅ API key saved successfully![/green] You can now use: [bold cyan]ai <your instruction>[/bold cyan]")
