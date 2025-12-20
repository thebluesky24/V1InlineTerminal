'''
AI Powered Inline Terminal Assistant

This file has some changes made for the writing of the code by the gemini to the file system.

Author:
--Pranav Digraskar
Starting-Date: 29/11/25
Last-Modified: 30/11/25

logs:
- 30/11/25: Fixed bugs in execute_with_ieditor function for correct file writing and directory handling.
- 06/12/25: Started implenting the class APIKeyManager for managing multiple API keys using keyring.
- 07/12/25: Added inline getmodels and setmodel to set the model dynamically.
'''


import subprocess
import os
import threading
import sys
import site
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, Completer, Completion
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory
import re
import ast
import time
from google import genai
from dotenv import load_dotenv
import pathlib
import nltk
import json
from prompt_toolkit.styles import Style
from pathlib import Path
import keyring
from openai import OpenAI
import anthropic
from argon2 import PasswordHasher, Type
import yaml

def addSpacing():# this is a custom function to add the spacing in the automated task
    print("########################################################")
    print()


#Password Hashing
ph = PasswordHasher(
    time_cost=2,
    memory_cost=102400,
    parallelism=8,
    hash_len=64,
    salt_len=16,
    type = Type.ID
)



class Config:
    isPasswordSet : bool = False
    isAPIKeyConfig : bool = False
    isSetupDone : bool = False
    GEMINI_API_KEY : str = None
    OPENAI_API_KEY : str = None
    ANTHROPIC_API_KEY : str = None
    
    def __init__(self):
        self.ConfigSet()
        self.PassSet()

    def ConfigSet():
        try:
            home_dir = os.path.expanduser("~")
            app_dir = os.path.join(home_dir, ".inlineterminal")
            logs_dir = os.path.join(app_dir, "logs")
            config_dir = os.path.join(app_dir, "config")
            config_file_path = os.path.join(config_dir, "config.yml")
            logs_file_path = os.path.join(logs_dir, "logs.yml")
            if not os.path.exists(app_dir):
                addSpacing()
                print("No Set-up Directory Found For Inline-Terminal")
                addSpacing()
                print("Setting up the dir and the all the necessary files for the Safe Execution of Inline-Terminal")
                addSpacing()
                os.makedirs(app_dir, exist_ok=True)
                logs_dir = os.path.join(app_dir, "logs")
                config_dir = os.path.join(app_dir, "config")
                os.makedirs(logs_dir, exist_ok=True)
                os.makedirs(config_dir, exist_ok=True)
                addSpacing()
                config_file_path = os.path.join(config_dir, "config.yml")
                logs_file_path = os.path.join(logs_dir, "logs.yml")
                default_config_content = f'''
serviceName: Inline-Terminal
version : 1.0
setupVar:
    isPasswordSet: false
    isAPIKeyConfig: false
    isSetupDone: false

env: 
    appPath: {app_dir}
    configPath: {config_dir}
    logsPath: {logs_dir}
apikey:
    setGemini: false
    setOpenAI: false
    setAnthropic: false
'''
                with open(config_file_path, "w") as f:
                    f.write(default_config_content)
                    print("Setting up Completed")
            else:
                with open(config_file_path, "r")as f:
                    configdata = yaml.safe_load(f)
                    isPasswordSet = configdata["setupVar"]["isPasswordSet"]
                    isAPIKeyConfig = configdata["setupVar"]["isAPIKeyConfig"]
                    isSetupDone = configdata["setupVar"]["isSetupDone"]
        
        except FileNotFoundError as e:
            print(f"Error Occurred: {e}")


    def PassSet():
        if not Config.isPasswordSet:
            passwordsetIP = input("do you want to set the passwords for api-keys??(Y/N)")
            while(passwordsetIP.lower() not in ["y","n"]):
                print("Invalid Input Please enter Y or N")
                passwordsetIP = input("do you want to set the passwords for api-keys??(Y/N)")
            if passwordsetIP.lower()=="y":
                print("If you don't have API-KEY Press ENTER...")
                setGeminiApiKey = input("Enter Gemini-API-Key: ")
                setOPENAIApiKey = input("Enter OpenAI-API-Key: ")
                setAnthropicApiKey = input("Enter Anthropic-API-Key: ")
                print("Type a Password which you will remeber it will ask for each session of a terminal to avoid any conflict.")
                API_Password = input("Enter the Password to store API-KEY's: ")
                hashed_password = ph.hash(API_Password)
                hashed_password_list = hashed_password.split("$")
                if setGeminiApiKey:
                    keyring.set_password(service_name= "Gemini", username=hashed_password_list[len(hashed_password_list)-1], password=setGeminiApiKey)
                if setOPENAIApiKey:
                    keyring.set_password(service_name="OpenAI", username=hashed_password_list[len(hashed_password_list)-1], password=setOPENAIApiKey)
                if setAnthropicApiKey:
                    keyring.set_password(service_name="Anthropic", username=hashed_password_list[len(hashed_password_list)-1], password=setAnthropicApiKey)
                print("API-KEY's Set Successfully")
            else:
                print("Skipping API-KEY setup")
    
    def addAPIKEYS():
        if 
        

        

            
                

                    
                    

            


   











custom_style = Style.from_dict({
    # Prompt styling
    'prompt': '#00ff00 bold',      # Bright green, bold
    # Input text styling
    '': '#00ff00',                 # Green color for input text
    # Placeholder text
    'placeholder': '#888888',      # Gray for placeholder
    # Bottom toolbar
    'bottom-toolbar': 'bg:#222222 #00ffff',  # Cyan text on dark background
})


class APICALLS:
    def __init__(self, service_name = "Gemini", model_name = "gemini-2.0-flash"):
        self.service_name = service_name
        self.model_name = model_name

    def OpenAICall(self, model_name = None, content = None):
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = client.responses.create(
            model = model_name,
            input = content
        )
        return resp.output_text
        
    def GEMINICall(self, model_name = None, content = None):
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model=model_name,
            contents=content
        )
        return response.text

    def ANTHROPICCall(self, model_name = None, content = None):
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model=model_name,
            messages=content
        )
        return response['completion']
    
    def apiCall(self, service_name = None, model_name = None):
        if service_name == "Gemini" or service_name is None:
            self.GEMINICall(model_name=model_name)
        elif service_name == "OpenAI":
            self.OpenAICall(model_name=model_name)  
        elif service_name == "Anthropic":
            self.ANTHROPICCall(model_name=model_name)
        
    def allModels(self):
        models = {"gemini-3.0-pro",
                            "gemini-3.0-deep-think",
                            "gemini-2.5-pro",
                            "gemini-2.5-flash",
                            "gemini-2.5-flash-lite",
                            "gemini-2.0-flash",
                            "gemini-2.0-flash-lite",
                            "gpt-5",
                            "gpt-5-pro",
                            "gpt-5.2",
                            "openai-o3",
                            "openai-o4-mini",
                            "gpt-4o-mini",
                            "gpt-4",
                            "gpt-4-turbo",
                            "gpt-3.5-turbo",
                            "claude-sonnet-4-20250514",
                            "claude-opus-4-20250514",
                            "claude-3-5-sonnet-20241022",
                            "claude-3-5-haiku-20241022",
                            "claude-3-opus-20240229",
                            "claude-3-sonnet-20240229",
                            "claude-3-haiku-20240307"}
        return models

       



    
    




load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')
# Loading different api_keys from keyring
class APIKeyManager:
    SERVICE_NAME = "InlineTerminal"
    DEFAULT_PATH = os.path.expanduser("~/.inlineterminal/credentials.json")


    DEFAULT_USERNAME = ["gemini_api_key", "openai_api_key", "anthropic_api_key"]   
    def __init__(self):
        self.credentials = {}
    
    def askUserName():
        api_vault_password = input("Enter the password to access the API keys: ")
        return api_vault_password
    
    def verifyPassword(self, input_password):
        pass

    def routineCheck(self, username, api_key):
        for username in self.DEFAULT_USERNAME:
            pass
        
            


    def get_api_key(self, username):
        return keyring.get_password(self.SERVICE_NAME, username)
    




help_method = '''
inline help index
inline --help  > opens the inline index
inline --ask   > ask Query to the AI agent
inline --execute > ask Query and it will execute that query also
ctrl + e       > initiate the AI suggestions inside completer
inline --contact > Get Email ID of inline Help Team
exit           > quit/exit from terminal
'''

contact_inline = '''
CONTACT DETAILS
EMAIL ID : inlineterminal@gmail.com
'''
__inlineShowmodels__ = '''
supported models:
Service Name : Gemini
Models:
    1."gemini-3.0-pro",
    2."gemini-3.0-deep-think",
    3."gemini-2.5-pro",
    4."gemini-2.5-flash",
    5."gemini-2.5-flash-lite",
    6."gemini-2.0-flash",
    7."gemini-2.0-flash-lite"

Service Name: OpenAI
Models:
    1."gpt-5",
    2."gpt-5-pro",
    3."gpt-5.2",
    4."openai-o3",
    5."openai-o4-mini",
    6."gpt-4o-mini",
    7."gpt-4",
    8."gpt-4-turbo",
    9."gpt-3.5-turbo"

Service Name: Anthropic
Models:
    1."claude-sonnet-4-20250514",
    2."claude-opus-4-20250514",
    3."claude-3-5-sonnet-20241022",
    4."claude-3-5-haiku-20241022",
    5."claude-3-opus-20240229",
    6."claude-3-sonnet-20240229",
    7."claude-3-haiku-20240307"
'''

#Implementing the $ DANGEROUS PATTERN $ recognisation
DANGEROUS_COMMAND_PATTERNS = [
    # Linux & macOS
    r"rm\s+-rf\s+/",                          # Deletes the entire root filesystem
    r"dd\s+if=/dev/zero\s+of=/dev/sd[a-z]",   # Overwrites a hard drive with zeros
    r"mkfs\..+\s+/dev/sd[a-z]",               # Formats a hard drive
    r"\breboot\b",                            # Reboots the system
    r"shutdown\s+-h\s+now",                   # Shuts down the system
    r"\bhalt\b",                              # Halts the system
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\};\s*:", # Fork bomb
    r"\bkillall\b",                           # Kills all processes by name
    r"\bpkill\b",                             # Kills processes by name

    # Windows
    r"echo del\s+/s\s+/q\s+[a-zA-Z]:\\\\",
    r"format\s+[a-zA-Z]:",                    # Formats ANY drive (not just C:)
    r"del\s+/s\s+/q\s+[a-zA-Z]:\\\\",         # Recursive delete from a drive
    r"rmdir\s+/s\s+/q\s+[a-zA-Z]:\\\\",       # Recursive directory delete
    r"erase\s+[a-zA-Z]:\\\\",                 # Erase files on drive
    r"shutdown\s+/s",                         # Shuts down the system
    r"shutdown\s+/r",                         # Restarts the system
    r"taskkill\s+/f",                         # Forcefully kills processes
    r"sfc\s+/scannow",                        # System File Checker
    r"chkdsk\s+/f\s+[a-zA-Z]:",               # Disk check (can force reboot)
    r"bootrec\s+/fixmbr",                     # Overwrites Master Boot Record
    r"bootrec\s+/fixboot",                    # Alters boot sector
    r"bcdedit\s+/deletevalue",                # Breaks boot config
    r"net\s+user\s+\w+\s+/delete",            # Deletes user accounts
    r"net\s+user\s+administrator\s+\*",       # Resets admin password
    r"cipher\s+/w:[a-zA-Z]:",                 # Wipes free space
    r"reg\s+delete\s+HK(LM|CU)",              # Registry deletion
    r"powershell\s+Remove-Item\s+-Recurse",   # Recursive delete in PowerShell

    # macOS specific
    r"sudo\s+rm\s+-rf\s+/",                   # Deletes root filesystem
    r"diskutil\s+eraseDisk",                  # Erases a disk
    r"srm\s+-rf\s+/",                         # Secure remove root filesystem
    r"killall\s+Finder",                      # Kills Finder process
    r"killall\s+Dock"                         # Kills Dock process
]


def is_dangerous(cmd):
    return any(re.search(p, cmd, re.IGNORECASE) for p in DANGEROUS_COMMAND_PATTERNS)





_VENV_STACK = []

def activate_venv(venv_path):
    """
    Activate a Python virtual environment inside this Python process.
    Updates PATH, VIRTUAL_ENV, and sys.path so subprocesses also use the venv's Python.
    """
    try:
        venv_path = os.path.abspath(venv_path)
        if not os.path.isdir(venv_path) or not os.path.exists(os.path.join(venv_path, "pyvenv.cfg")):
            print(f"Not a valid virtual environment: {venv_path}")
            return False

        if "VIRTUAL_ENV" in os.environ and os.environ["VIRTUAL_ENV"]:
            _VENV_STACK.append({
                "VIRTUAL_ENV": os.environ["VIRTUAL_ENV"],
                "PATH": os.environ["PATH"],
                "sys.path": list(sys.path)
            })
            deactivate_venv(silent=True)

        bin_folder = os.path.join(venv_path, "Scripts" if os.name == "nt" else "bin")
        if not os.path.isdir(bin_folder):
            print(f"No Scripts/bin folder in: {venv_path}")
            return False

        os.environ["VIRTUAL_ENV"] = venv_path
        os.environ["PATH"] = bin_folder + os.pathsep + os.environ.get("PATH", "")

        py_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        site_packages = (
            os.path.join(venv_path, "Lib", "site-packages")
            if os.name == "nt"
            else os.path.join(venv_path, "lib", py_version, "site-packages")
        )
        if os.path.exists(site_packages):
            site.addsitedir(site_packages)
        else:
            print(f"No site-packages found in: {site_packages}")

        print(f"Activated virtual environment: {venv_path}")
        return True

    except Exception as e:
        print(f"Failed to activate venv: {e}")
        return False

def deactivate_venv(silent=False):
    """
    Deactivate the currently active virtual environment.
    Restores the previous one if available.
    """
    try:
        if "VIRTUAL_ENV" not in os.environ or not os.environ["VIRTUAL_ENV"]:
            if not silent:
                print("No virtual environment is currently active.")
            return False

        current_venv = os.environ["VIRTUAL_ENV"]
        bin_folder = os.path.join(current_venv, "Scripts" if os.name == "nt" else "bin")
        os.environ["PATH"] = os.pathsep.join(
            [p for p in os.environ["PATH"].split(os.pathsep) if os.path.abspath(p) != os.path.abspath(bin_folder)]
        )

        py_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
        site_packages = (
            os.path.join(current_venv, "Lib", "site-packages")
            if os.name == "nt"
            else os.path.join(current_venv, "lib", py_version, "site-packages")
        )
        sys.path[:] = [p for p in sys.path if not p.startswith(os.path.abspath(site_packages))]
        os.environ.pop("VIRTUAL_ENV", None)

        if _VENV_STACK:
            prev_env = _VENV_STACK.pop()
            os.environ["VIRTUAL_ENV"] = prev_env["VIRTUAL_ENV"]
            os.environ["PATH"] = prev_env["PATH"]
            sys.path[:] = prev_env["sys.path"]
            if not silent:
                print(f"Restored previous virtual environment: {prev_env['VIRTUAL_ENV']}")
        else:
            if not silent:
                print(f"Deactivated virtual environment: {current_venv}")

        return True

    except Exception as e:
        print(f"Failed to deactivate venv: {e}")
        return False

def askQuestions(Query):
    try:
        client = genai.Client(api_key=gemini_api_key)
#         system_prompt = system_prompt = """
# <identity>
# You are an AI CLI Assistant called Inline Terminal Assistant.
# </identity>

# <capabilities>
# - Always return a valid JSON object with a single key "commands".
# - The value of "commands" must be a list of shell command strings.
# - Example output format:
#   {
#     "commands": ["dir", "cd ..", "pip list"]
#   }
# - Do not include any explanations, markdown formatting, or additional text — only JSON.
# - Do not add labels, warnings, or prefixes such as "[DANGEROUS]" or "[SAFE]".
# - Assume all commands will be reviewed and safely executed in an isolated Docker environment.
# - If unsure or no valid command applies, return {"commands": []}.
# </capabilities>
# """
        system_prompt = """
<identity>
You are an AI CLI Assistant called Inline Terminal Assistant.
You operate inside a Windows Command Prompt environment.
</identity>

<capabilities>
- Always return a valid JSON object with a single key "commands".
- The value of "commands" must be a list of **Windows CMD commands only** (not PowerShell or Bash).
- Example output format:
  {
    "commands": ["dir", "cd ..", "pip list"]
  }

- Commands must be syntactically correct for Windows Command Prompt.
- Do NOT include:
  • Any explanations, markdown, code fences, or extra text.
  • Any labels such as [DANGEROUS], [SAFE], or comments.
  • Any Linux or PowerShell commands (e.g., ls, rm, echo '...', | Out-File).

- Assume all commands will be shown to the user for confirmation and executed in a secure sandbox (Docker container).
- Therefore, **no safety labels or warnings** are needed — just clean CMD commands.
- If unsure or no valid command applies, return {"commands": []}.
</capabilities>
"""

        content = f"{system_prompt}\n\nUser request: {Query}"
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=content
        )
        # time.sleep(3)
        start_find_index = response.text.find('{')
        end_find_index = response.text.rfind('}') + 1
        extracted_json = response.text[start_find_index:end_find_index]
        json_response = json.loads(extracted_json)
        list_of_commands = json_response["commands"]
        print("List of commands:", list_of_commands)
        return
    except:
        print("Something Error has occurred!!!!, Please check the network connection")
        return

def executeQuery(Query): #this is the function which will return list of commands to be executed --used by inline --execute
    try:
        client = genai.Client(api_key=gemini_api_key)
        system_prompt = """
<identity>
You are an AI CLI Assistant called Inline Terminal Assistant.
You operate inside a Windows Command Prompt environment.
</identity>

<capabilities>
- Always return a valid JSON object with a single key "commands".
- The value of "commands" must be a list of **Windows CMD commands only** (not PowerShell or Bash).
- FIRST CREATE DIRECTORIES IF NEEDED using mkdir command before using cd into them. AND THEN create files using echo or WRITE_FILE command.(VERY IMPORTANT FOR FILE CREATION)
- For file creation with code, use this format:
  "WRITE_FILE:filename|||code_content_here"
  
Example:
{
  "commands": [
    "mkdir myproject",
    "cd myproject",
    "WRITE_FILE:app.py|||def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nprint(fibonacci(10))",
    "python app.py"
  ]
}

- Commands must be syntactically correct for Windows Command Prompt.
- Do NOT include:
  • Any explanations, markdown, code fences, or extra text.
  • Any labels such as [DANGEROUS], [SAFE], or comments.
  • Any Linux or PowerShell commands (e.g., ls, rm, echo '...', | Out-File).

- Assume all commands will be shown to the user for confirmation and executed in a secure sandbox (Docker container).
- Therefore, **no safety labels or warnings** are needed — just clean CMD commands.
- If unsure or no valid command applies, return {"commands": []}.
</capabilities>
"""
#         system_prompt = """
# <identity>
# You are an AI CLI Assistant called Inline Terminal Assistant.
# You operate inside a Windows Command Prompt environment.
# </identity>

# <capabilities>
# - Return JSON with key "commands" containing a list of commands.
# - For file creation with code, use this format:
#   "WRITE_FILE:filename|||code_content_here"
  
# Example:
# {
#   "commands": [
#     "mkdir myproject",
#     "cd myproject",
#     "WRITE_FILE:app.py|||def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n\nprint(fibonacci(10))",
#     "python app.py"
#   ]
# }

# - Use normal CMD commands for everything else: dir, cd, pip install, etc.
# - Do NOT include explanations or markdown.
# </capabilities>
# """
        content = f"{system_prompt}\n\nUser request: {Query}"
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=content
        )
        time.sleep(1)
        start_find_index = response.text.find('{')
        end_find_index = response.text.rfind('}') + 1
        extracted_json = response.text[start_find_index:end_find_index]
        json_response = json.loads(extracted_json)
        list_of_commands = json_response["commands"]
        return list_of_commands
        # response_text = response.text.strip()
        # code_blocks = re.findall(r"```(?:\w+)?\s*([\s\S]+?)```", response_text)
        # for block in code_blocks:
        #     block = block.strip()
        #     try:
        #         execution_cmd_list = ast.literal_eval(block)
        #         if isinstance(execution_cmd_list, list):
        #             print(execution_cmd_list)
        #             return execution_cmd_list
        #     except Exception:
        #         continue
        # print("Something Error has occurred!!!!, Please check the network connection, we are Trying Again")
        # return []
    except:
        print("Something Error has occurred!!!!, Please check the network connection, we are Trying Again")
        return []


def giveDescription(content):# this function will give the description of the project present in the folder path
    try:
        client = genai.Client(api_key=gemini_api_key)
        system_prompt = """
<identity>
You are an OPEN SOURCE EXPERT Assistant called OPEN SOURCE Assistant.
You operate inside a Windows environment.
</identity>

<capabilities>
- Always return a valid JSON object with a single key "main-points".
- The value of "main-points" must be a list of important points about the PROJECT.
- Example output format:
  {
    "main-points": ["This project does X", "Run main.py to start", "Dependencies: Flask, SQLAlchemy"]
  }

- Focus on what the project does and how to run it.
- Do NOT include extra text outside the JSON.
</capabilities>
"""
        full_prompt = f"{system_prompt}\n\nUser request:\n{content}"
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt
        )

        text = response.text.strip()
        # Extract JSON from response
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if not match:
            print(" No JSON found in response.\nResponse was:\n", text)
            return

        extracted_json = match.group(0)

        # Fix common JSON mistakes
        extracted_json = (
            extracted_json
            .replace("'", '"')  # single to double quotes
            .replace("“", '"').replace("”", '"')  # fancy quotes
            .replace("\n", " ").strip()
        )

        try:
            data = json.loads(extracted_json)
            print("Project Summary:\n", json.dumps(data, indent=2))
        except json.JSONDecodeError as e:
            print("JSON parsing error:", e)
            print("Raw extracted JSON:\n", extracted_json)
    except Exception as e:
        print(f"Error in askQuestions: {e}")


def read_all_files(folder_path, exclude_folders=None):# this function will read all the files from the given folder path and give the content to giveDescription function
    if exclude_folders is None:
        exclude_folders = [
    '.git', '.github', '.gitlab', '.svn', '.hg', '.idea', '.vscode',
    '__pycache__', '.pytest_cache', '.mypy_cache', '.tox', '.venv',
    'env','.env', 'venv', 'build', 'dist', 'egg-info',
    'node_modules', '.next', '.nuxt', 'coverage', '.parcel-cache', 'bower_components',
    '$RECYCLE.BIN', 'System Volume Information', '.Trash', '.cache', '.local', '.config',
    'AppData', 'Program Files', 'Program Files (x86)',
    'temp', 'tmp', 'logs', 'log', '.DS_Store', 'Thumbs.db'
]

    folder = Path(folder_path)
    file_contents = ""

    for file_path in folder.rglob('*'):
        if file_path.is_dir() or any(excluded in file_path.parts for excluded in exclude_folders):
            continue

        if file_path.suffix.lower() not in [".py", ".js", ".md", ".txt", ".json"]:
            continue  # only read relevant files

        print("📄 Reading:", file_path)
        try:
            file_contents += file_path.read_text(encoding="utf-8") + f"\n\n--- End of {file_path.name} ---\n\n"
        except Exception as e:
            print(f"Could not read {file_path}: {e}")

    if file_contents.strip():
        giveDescription(file_contents)
    else:
        print("No valid files found to read.")



def suggest_commands(cmd_history):# this function will suggest the commands based on the history of the commands used earlier
    try:
        client = genai.Client(api_key=gemini_api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"you are a cli expert this is history of the cmd used earlier can you predict the next 5 cmds and give me the list of it only list dont give me any thing so i can parse these things cmdhistory={cmd_history}"
        )
        response_list = ast.literal_eval(response.text)
        return response_list
    except:
        return []

class PathCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor.strip()
        current_path = os.getcwd()
        words = text.split()
        
        # Handle model completions for "inline --setmodel <provider>"
        if len(words) >= 2 and words[0] == "inline":
            try:
                setmodel_idx = words.index("--setmodel")
                
                # If we're at the provider position (right after --setmodel)
                if len(words) == setmodel_idx + 2:
                    provider = words[setmodel_idx + 1].lower()
                    partial = provider
                    
                    # Suggest provider names
                    providers = ["gemini", "openai", "anthropic"]
                    for p in providers:
                        if p.startswith(partial):
                            yield Completion(
                                p,
                                start_position=-len(partial),
                                display=p
                            )
                    return
                
                # If we're at the model position (after provider name)
                elif len(words) >= setmodel_idx + 3:
                    provider = words[setmodel_idx + 1].lower()
                    partial = words[-1].lower()
                    
                    models = []
                    if provider == "gemini":
                        models = [
                            "gemini-3.0-pro",
                            "gemini-3.0-deep-think",
                            "gemini-2.5-pro",
                            "gemini-2.5-flash",
                            "gemini-2.5-flash-lite",
                            "gemini-2.0-flash",
                            "gemini-2.0-flash-lite"
                        ]
                    elif provider == "openai":
                        models = [
                            "gpt-5",
                            "gpt-5-pro",
                            "gpt-5.2",
                            "openai-o3",
                            "openai-o4-mini",
                            "gpt-4o-mini",
                            "gpt-4",
                            "gpt-4-turbo",
                            "gpt-3.5-turbo",
                        ]
                    elif provider == "anthropic":
                        models = [
                            "claude-sonnet-4-20250514",
                            "claude-opus-4-20250514",
                            "claude-3-5-sonnet-20241022",
                            "claude-3-5-haiku-20241022",
                            "claude-3-opus-20240229",
                            "claude-3-sonnet-20240229",
                            "claude-3-haiku-20240307",
                        ]
                    
                    # Yield matching models
                    for model in models:
                        if model.lower().startswith(partial):
                            yield Completion(
                                model,
                                start_position=-len(partial),
                                display=model
                            )
                    return  # Don't do path completion for model commands
                    
            except ValueError:
                pass  # --setmodel not found, continue to path completion
        
        # Default: Handle path completions for everything else
        partial = words[-1] if len(words) > 0 else ""
        try:
            base_path = os.path.join(current_path, partial)
            base_dir = os.path.dirname(base_path) if partial else current_path
            partial_name = os.path.basename(partial).lower()

            for entry in pathlib.Path(base_dir).iterdir():
                name = entry.name
                if name.lower().startswith(partial_name):
                    display = name + (os.sep if entry.is_dir() else "")
                    yield Completion(name, start_position=-len(partial), display=display)
        except Exception:
            pass

class CompositeCompleter(Completer):
    def __init__(self, command_completer, path_completer):
        self.command_completer = command_completer
        self.path_completer = path_completer

    def get_completions(self, document, complete_event):
        seen = set()

        # First yield command completer suggestions
        for comp in self.command_completer.get_completions(document, complete_event):
            text = getattr(comp, "text", None)
            if text is None or text in seen:
                continue
            seen.add(text)
            yield comp

        # Then yield path completer suggestions (deduped)
        for comp in self.path_completer.get_completions(document, complete_event):
            text = getattr(comp, "text", None)
            if text is None or text in seen:
                continue
            seen.add(text)
            yield comp       
        # text = document.text_before_cursor.strip()
        # words = text.split()

        # #if words and words[0] in ['cd', 'activate']:
        # yield from self.path_completer.get_completions(document, complete_event)
        # #else:
        #  #   yield from self.command_completer.get_completions(document, complete_event)

suggestion_list = ['exit', 'help', 'cd', 'inline --help', 'inline --ask', 'inline --execute', 'activate', 'deactivate', 'inline --contact', 'mkdir','inline --readfolder', 'inline --setmodel', 'inline --getmodel', 'inline --showmodels']
suggestion_set = set(suggestion_list)
command_completer = WordCompleter(suggestion_list, ignore_case=True)
path_completer = PathCompleter()
completer = CompositeCompleter(command_completer, path_completer)
cmd_history = []
first_path_flag = False
bindings = KeyBindings()
history = InMemoryHistory()
lock = threading.Lock()

class AutoSuggestCmd(AutoSuggest):
    def get_suggestion(self, buffer, document):
        text = document.text.strip()
        if text is None:
            return None
        for cmd in suggestion_list:
            if cmd.startswith(text) and cmd != text:
                return Suggestion(cmd[len(text):])
        return None

def command_prediction_async():
    with lock:
        predicted_cmds = suggest_commands(cmd_history)
        for cmd in predicted_cmds:
            if cmd not in suggestion_set:
                suggestion_set.add(cmd)
                suggestion_list.append(cmd)
        global command_completer, completer
        command_completer = WordCompleter(suggestion_list, ignore_case=True)
        completer = CompositeCompleter(command_completer, path_completer)

@bindings.add('c-t')
def _(event):
    threading.Thread(target=command_prediction_async, daemon=True).start()

#Implementing the Docker for the secure terminal
# def run_in_docker(cmd, timeout=5):
#     docker_cmd = [
#         "docker", "run", "--rm",
#         "--network", "none",     # no internet
#         "--memory", "128m",      # RAM limit
#         "--cpus", "0.5",         # CPU limit
#         "--pids-limit", "50",    # limit processes (stops fork bombs)
#         "ubuntu", "bash", "-c", cmd
#     ]
#     try:
#         result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=timeout)
#         return result.stdout if result.stdout else result.stderr
#     except subprocess.TimeoutExpired:
#         return "[!] Command killed (timeout — harmful or infinite loop)."

# Add this function to your terminal.py file

def execute_with_ieditor(execute_cmd_list):
    """
    Execute commands, and if a file needs code written, 
    open ieditor automatically with AI-generated content
    """
    current_dir = os.getcwd()
    _dir_stack = [current_path]  # Stack to keep track of directory changes
    
    for cmd in execute_cmd_list:
        # Check if this is a file write operation
        if cmd.startswith("WRITE_FILE:"):
            # Format: WRITE_FILE:filename|||code_content
            parts = cmd.split("|||", 1)
            if len(parts) == 2:
                filename = parts[0].replace("WRITE_FILE:", "").strip()
                code_content = parts[1].strip()
                
                # FIX 1: Use os.path.join() instead of string concatenation
                # CRITICAL BUG: You wrote r"\filename" which is literal text!
                full_path = os.path.join(current_dir, filename)
                
                print(f"AI writing code to: {full_path}")
                
                # Direct write to correct path
                with open(full_path, 'w') as f:
                    f.write(code_content)
                print(f"Code written to {full_path}")
                

        # FIX 2: Handle "cd .." BEFORE general "cd " to avoid conflict
        elif cmd.strip() == "cd ..":
            if len(_dir_stack) > 1:
                _dir_stack.pop()  # Remove current directory
                parent_directory = _dir_stack[-1]
                os.chdir(parent_directory)
                current_dir = parent_directory
                print(f"Changed directory to: {parent_directory}")
            else:
                print("Already at the root directory, cannot go up.")

        elif cmd.startswith('cd '):
            target_directory = cmd[3:].strip()
            try:
                # FIX 3: Handle relative and absolute paths correctly
                if not os.path.isabs(target_directory):
                    new_directory = os.path.join(current_dir, target_directory)
                else:
                    new_directory = target_directory
                
                new_directory = os.path.abspath(new_directory)
                
                # FIX 4: Check if directory exists before changing
                if not os.path.exists(new_directory):
                    print(f"Error: Directory does not exist: {new_directory}")
                    continue
                
                os.chdir(new_directory)
                current_dir = new_directory
                _dir_stack.append(current_path)
                print(f"Changed directory to: {new_directory}")
            except Exception as e:
                print(f"Error changing directory: {e}")
        
        else:
            # Regular command execution
            print(f"Executing: {cmd}")
            try:
                # FIX 5: Execute commands in the correct directory using cwd parameter
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    env=os.environ.copy(),
                    stdin=sys.stdin,
                    stdout=sys.stdout,
                    stderr=sys.stderr, 
                    text=True,
                    cwd=current_dir  # IMPORTANT: Execute in tracked directory
                )
                if result.stdout:
                    print(result.stdout.strip())
                if result.stderr:
                    print(result.stderr.strip())
            except Exception as e:
                print(f"Error executing command: {e}")
    print("Finished executing all commands.")
    print("Restoring original directory.")
    

def inlineDebug(command, return_code, error_output):
    try:
        client = genai.Client(api_key=gemini_api_key)
        system_prompt = """
<identity>
You are an AI CLI Assistant called Inline Terminal Assistant.
You operate inside a Windows Command Prompt environment.
</identity>

<capabilities>
- Always return a valid JSON object with a single key "error_description".
- The value of "error_description" must be a list of **SUGGESTIONS ONLY** .

  
Example:
{
  "error_description": [
    "1.this error is because of ....",
    "2.possible fix is to ....",
    "3.Another suggestion is to ....",
    "4.Finally you can try to ...."
  ]
}

- Suggestions must be syntactically correct for Windows Command Prompt.
- Do NOT include:
  • Any explanations, markdown, code fences, or extra text.
  • Any labels such as [DANGEROUS], [SAFE], or comments.
  • Any Linux or PowerShell commands (e.g., ls, rm, echo '...', | Out-File).

- Assume all commands will be shown to the user for confirmation and executed in a secure sandbox (Docker container).
- Therefore, **no safety labels or warnings** are needed — just clean Suggestions.
- If unsure or no valid command applies, return {"error_description": []}.
</capabilities>
"""
        content = f"{system_prompt}\n\nUser request: command={command} , return_code={return_code} , error_output={error_output}"
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=content
        )
        time.sleep(1)
        start_find_index = response.text.find('{')
        end_find_index = response.text.rfind('}') + 1
        extracted_json = response.text[start_find_index:end_find_index]
        json_response = json.loads(extracted_json)
        list_of_commands = json_response["error_description"]
        print("Suggestions to fix the error:", list_of_commands)
        return
    except: 
        print("Something Error has occurred!!!!, Please check the network connection, we are Trying Again")
        return


# Main loop
while True:
    try:
        apicalls = APICALLS()
        if first_path_flag == False:
            current_path = os.getcwd()
            first_path_flag = True

        venv_prefix = f"({os.path.basename(os.environ['VIRTUAL_ENV'])}) " if 'VIRTUAL_ENV' in os.environ else ""
        text = prompt(
        [('class:prompt', f"{venv_prefix}inlineTerminal<{current_path}> $ ")],
        completer=completer,
        placeholder='⮞ Ctrl+T → Get AI CLI suggestions',
        auto_suggest=AutoSuggestCmd(),
        key_bindings=bindings,
        history=history,
        style=custom_style,  # Add this line
        bottom_toolbar=HTML(
            '<b><style fg="cyan">⮞ Right Arrow: accept suggestion | Tab: autocomplete | Ctrl+T: get AI suggestions | inline --ask: ask Query | inline --execute: ask and execute Query | inline --contact: Get contact of Inline Team </style></b>')
        ).strip()
        history.append_string(text)

        cmdLine = text.split(" ")

        if text.lower() == 'exit':
            break
        elif text == 'deactivate':
            if deactivate_venv():
                if text not in suggestion_set:
                    suggestion_set.add(text)
                    suggestion_list.append(text)
                    command_completer = WordCompleter(suggestion_list, ignore_case=True)
                    completer = CompositeCompleter(command_completer, path_completer)
        elif text.startswith('activate'):
            if len(cmdLine) == 1:
                print("[!] Usage: activate <venv-path>")
            else:
                venv_path = cmdLine[1]
                if activate_venv(venv_path):
                    if text not in suggestion_set:
                        suggestion_set.add(text)
                        suggestion_list.append(text)
                        command_completer = WordCompleter(suggestion_list, ignore_case=True)
                        completer = CompositeCompleter(command_completer, path_completer)
        elif text.startswith("inline"):
            if len(cmdLine) == 1:
                print("did you mean inline --help")
            elif text.strip() == 'inline --help':
                print(help_method)
            elif text.strip() == 'inline --contact':
                print(contact_inline)
            elif text.startswith("inline --getmodel"):
                print(f"Current Service: {apicalls.service_name}, Current Model: {apicalls.model_name}")
            elif text.startswith("inline --setmodel"):
                Query = text.split(" ")
                if len(Query) != 4:
                    print("Usage: inline --setmodel <provider> <model>")
                    print("Example: inline --setmodel gemini gemini-2.0-flash")
                else:
                    service_name = Query[2].lower()
                    model_name = Query[3]
                    if service_name not in ['gemini', 'openai', 'anthropic']:
                        print("Supported Providers are: gemini, openai, anthropic")
                    if model_name not in apicalls.allModels():
                        print(f"Model {model_name} is not supported. Use inline --showmodels to see supported models.")
                    else:
                        print(f"Setting Service to {service_name} and Model to {model_name}...")
            elif text.strip() == 'inline --showmodels':
                print(__inlineShowmodels__)

            elif text.startswith("inline --ask"):
                try:
                    Query = text[12:]
                    if Query.strip() == "":
                        print("You do not have asked anything")
                    else:
                        askQuestions(Query)
                except Exception as e:
                    print(f"Error Occurred: {e}")
            elif text.startswith("inline --execute"):
                try:
                    Query = text[len("inline --execute"):]
                    if Query.strip() == "":
                        print("Do not have anything to Execute")
                    else:
                        execute_cmd_list = executeQuery(Query)
                        for i in range(2):   # this loop will try twice to get commands
                            time.sleep(3)
                            if not execute_cmd_list:
                                execute_cmd_list = executeQuery(Query)    #here is the try again call
                            else:
                                break
                        if execute_cmd_list: # check successfully fetched commands
                            print("List of Commands to be executed (given sequentially): ")
                            for commands_tobe_executed in execute_cmd_list:
                                print(commands_tobe_executed) #print the commands to be executed
                            print('####')
                            print('####')
                            # combined_command = " && ".join(execute_cmd_list) #joining the commands with &&
                            execute_command_confirmation = input(
                                "Do you Want to Continue with Above List of Commands??(Y/N): ")
                            while (execute_command_confirmation.lower() not in ['y', 'n']):
                                print("Y/N?")
                                execute_command_confirmation = input(
                                    "Do you Want to Continue with Above List of Commands??(Y/N): ")

                            if execute_command_confirmation.lower() == "y":
                                print(f"Executing: commands")
                                try:
                                    current_dir_inUse = os.getcwd() # Save current directory
                                    execute_with_ieditor(execute_cmd_list)
                                    os.chdir(current_dir_inUse)  # Restore original directory
                                except Exception as e:
                                    print(f"Error Occurred: {e}")
                            elif execute_command_confirmation.lower() == "n":
                                print("YOU HIT N!! ")
                        else:
                            print("!!! Failed to fetch the commands, please modify your command or try again")
                except Exception as e:
                    print(f"Gemini Network Error: {e}")
            else:
                print("No command found, type inline --help to get help")
        elif text.startswith('cd') and len(cmdLine) == 1:
            current_path = os.getcwd()
            print(current_path)
        elif text.startswith('cd') and len(cmdLine) > 1:
            try:
                os.chdir(text[3:])
                if text not in suggestion_set:
                    suggestion_set.add(text)
                    suggestion_list.append(text)
                    # CHANGED: Update completers after directory change
                    command_completer = WordCompleter(suggestion_list, ignore_case=True)
                    completer = CompositeCompleter(command_completer, path_completer)
                current_path = os.getcwd()
            except Exception as e:
                print(f"Error occurred Invalid Command: {e}")
        else:
            try:
                # CHECKING THE COMMAND IS DANGEROUS OR NOT
                if is_dangerous(text):
                    print("POTENTIAL DANGEROUS COMMAND!!")
                    print("###")
                    print("###")
                    execute_command_confirmation = input("Do you want to Continue with the command?(Y/N): ")
                    while execute_command_confirmation.lower() not in ['y', 'n']:
                        print("Y/N?")
                        execute_command_confirmation = input("Do you want to Continue with the command?(Y/N): ")
                    if execute_command_confirmation.lower() == 'y':
                        # CHANGED: Use text instead of cmdLine for subprocess.run
                        cmdExecution = subprocess.run(text, shell=True, env=os.environ.copy(), stdin=sys.stdin,stdout=sys.stdout, stderr=sys.stderr, cwd=current_path,
                                                      text=True)
                        if cmdExecution.stdout:
                            print(cmdExecution.stdout.strip())
                        if cmdExecution.stderr:
                            print(cmdExecution.stderr.strip())
                        if cmdExecution.returncode == 0:
                            cmd_history.append(text)
                            if text not in suggestion_set:
                                suggestion_set.add(text)
                                suggestion_list.append(text)
                                # CHANGED: Update completers after execution
                                command_completer = WordCompleter(suggestion_list, ignore_case=True)
                                completer = CompositeCompleter(command_completer, path_completer)
                        elif cmdExecution.returncode != 0:
                            print(f"Command failed with return code: {cmdExecution.returncode}")
                            inlineDebug(text, cmdExecution.returncode, cmdExecution.stderr)
                else:
                    cmdExecution = subprocess.run(text, shell=True, env=os.environ.copy(), stdin=sys.stdin,stdout=sys.stdout, stderr=sys.stderr,
                                                  text=True, cwd=current_path)
                    if cmdExecution.stdout:
                        print(cmdExecution.stdout.strip())
                    if cmdExecution.stderr:
                        print(cmdExecution.stderr.strip())
                    if cmdExecution.returncode == 0:
                        cmd_history.append(text)
                        if text not in suggestion_set:
                            suggestion_set.add(text)
                            suggestion_list.append(text)
                            # CHANGED: Update completers after execution
                            command_completer = WordCompleter(suggestion_list, ignore_case=True)
                            completer = CompositeCompleter(command_completer, path_completer)
                    elif cmdExecution.returncode != 0:
                        print(f"Command failed with return code: {cmdExecution.returncode}")
                        # inlineDebug(text, cmdExecution.returncode, cmdExecution.stderr.strip())
            except Exception as e:
                print(f"Error Occurred: {e}")

        if len(cmd_history) % 2 == 0 and len(cmd_history) > 0:
            threading.Thread(target=command_prediction_async, daemon=True).start()

    except KeyboardInterrupt:
        print("\n[KeyboardInterrupt] Type 'exit' to quit.")
        continue
    except EOFError:
        print("\n[EOF] Exiting terminal.")
