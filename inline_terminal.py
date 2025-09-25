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

load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')

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
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"you are a cli expert this is query {Query} give me only command dont give me anything so i can parse this thing where i want which i can type and execute it"
        )
        time.sleep(3)
        print(response.text)
        return
    except:
        print("Something Error has occurred!!!!, Please check the network connection")
        return

def executeQuery(Query):
    try:
        client = genai.Client(api_key=gemini_api_key)
        content = (
            "You are a command line expert. Convert the following natural language request "
            "into a Python list of shell commands. and give the commands for windows and which can be used in command prompt. Output ONLY the list. No explanation. "
            "For example: ['dir', 'cd ..', 'pip list'].\n\n"
            f"Request: {Query}"
        )
        # content = (
        #     "You are a powerful agentic AI coding assistant, operating inside a custom inline terminal. "
        #     "Follow these rules carefully:\n"
        #     "1. Convert the user's natural language request into safe, executable Windows CMD commands.\n"
        #     "2. Respond ONLY with a valid Python list of strings, e.g. ['dir', 'cd ..', 'pip list'].\n"
        #     "3. Do not explain, add text, or format with markdown code fences.\n"
        #     "4. Ensure the commands can run inside Windows Command Prompt.\n"
        #     f"User request: {Query}"
        # )
        
        #Modified content --1st
        # content = ("You are a command line expert. Convert the following natural language request into a Python list of Windows Command Prompt commands. Output ONLY the list in the format ['command1', 'command2', ...] with no explanation or extra text. Request: {Query}")

        #Modified content --2nd
        # content=f"you are a cli expert this is query {Query} of the user can you give me cmds and give me the list of it. only list dont give me any thing so i can parse these things like a list, for example:['dir', 'cd ..', 'pip list'] "

        #Modified content --3rd
        # content = (f"you are a cli expert this is query {Query} give me only command dont give me anything so i can parse this thing where i want which i can type and execute it")

        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=content
        )
        time.sleep(3)
        response_text = response.text.strip()
        code_blocks = re.findall(r"```(?:\w+)?\s*([\s\S]+?)```", response_text)
        for block in code_blocks:
            block = block.strip()
            try:
                execution_cmd_list = ast.literal_eval(block)
                if isinstance(execution_cmd_list, list):
                    print(execution_cmd_list)
                    return execution_cmd_list
            except Exception:
                continue
        print("Something Error has occurred!!!!, Please check the network connection, we are Trying Again")
        return []
    except:
        print("Something Error has occurred!!!!, Please check the network connection, we are Trying Again")
        return []

def suggest_commands(cmd_history):
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
        current_dir = os.getcwd()
        words = text.split()
        
        if not words or words[0] not in ['cd', 'activate']:
            return

        partial = words[-1] if len(words) > 1 else ""
        try:
            base_path = os.path.join(current_dir, partial)
            base_dir = os.path.dirname(base_path) if partial else current_dir
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
        text = document.text_before_cursor.strip()
        words = text.split()

        if words and words[0] in ['cd', 'activate']:
            yield from self.path_completer.get_completions(document, complete_event)
        else:
            yield from self.command_completer.get_completions(document, complete_event)

suggestion_list = ['exit', 'help', 'cd', 'inline --help', 'inline --ask', 'inline --execute', 'activate', 'deactivate', 'inline --contact', 'mkdir']
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
def run_in_docker(cmd, timeout=5):
    docker_cmd = [
        "docker", "run", "--rm",
        "--network", "none",     # no internet
        "--memory", "128m",      # RAM limit
        "--cpus", "0.5",         # CPU limit
        "--pids-limit", "50",    # limit processes (stops fork bombs)
        "ubuntu", "bash", "-c", cmd
    ]
    try:
        result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout if result.stdout else result.stderr
    except subprocess.TimeoutExpired:
        return "[!] Command killed (timeout — harmful or infinite loop)."





# Main loop
while True:
    try:
        if first_path_flag == False:
            current_path = os.getcwd()
            first_path_flag = True

        venv_prefix = f"({os.path.basename(os.environ['VIRTUAL_ENV'])}) " if 'VIRTUAL_ENV' in os.environ else ""
        text = prompt(
            f"{venv_prefix}inlineTerminal<{current_path}> $ ",
            completer=completer,
            placeholder='⮞ Ctrl+T → Get AI CLI suggestions',
            auto_suggest=AutoSuggestCmd(),
            key_bindings=bindings,
            history=history,
            bottom_toolbar=HTML('<b><style fg="cyan">⮞ Right Arrow: accept suggestion | Tab: autocomplete | Ctrl+T: get AI suggestions | inline --ask: ask Query | inline --execute: ask and execute Query | inline --contact: Get contact of Inline Team </style></b>')
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
            elif text == 'inline --help':
                print(help_method)
            elif text == 'inline --contact':
                print(contact_inline)
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
                        for i in range(2):
                            time.sleep(3)
                            if not execute_cmd_list:
                                execute_cmd_list = executeQuery(Query)
                            else:
                                break
                        if execute_cmd_list:
                            print("List of Commands to be executed (given sequentially): ")
                            for commands_tobe_executed in execute_cmd_list:
                                print(commands_tobe_executed)
                            print('####')
                            print('####')
                            combined_command = " && ".join(execute_cmd_list)
                            virtual_execution_result = run_in_docker(combined_command)
                            print("#### RESULT OF DOCKER ####")
                            print(virtual_execution_result)
                            print()
                            print()
                            print()
                            execute_command_confirmation = input("Do you Want to Continue with Above List of Commands??(Y/N): ")
                            while(execute_command_confirmation.lower() not in ['y', 'n']):
                                print("Y/N?")
                                execute_command_confirmation = input("Do you Want to Continue with Above List of Commands??(Y/N): ")

                            if execute_command_confirmation.lower() == "y":
                                print(f"Executing: {combined_command}")
                                try:
                                    cmdExecution = subprocess.run(combined_command, shell=True, env=os.environ.copy(), capture_output=True, text=True)
                                    if cmdExecution.stdout:
                                        print()
                                        print()
                                        print('Output is given below : ')
                                        print(cmdExecution.stdout.strip())
                                    if cmdExecution.stderr:
                                        print(cmdExecution.stderr.strip())
                                    if cmdExecution.returncode == 0:
                                        cmd_history.append(text)
                                        if text not in suggestion_set:
                                            suggestion_set.add(text)
                                            suggestion_list.append(text)
                                            command_completer = WordCompleter(suggestion_list, ignore_case=True)
                                            completer = CompositeCompleter(command_completer, path_completer)
                                except Exception as e:
                                    print(f"Error Occurred: {e}")
                            elif execute_command_confirmation.lower() == "n":
                                print("YOU HIT NO!! ")
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
                #CHECKING THE COMMAND IS DANGEROUS OR NOT
                if is_dangerous(text):
                    print("POTENTIAL DANGEROUS COMMAND!!")
                    print("###")
                    print("###")
                    execute_command_confirmation = input("Do you want to Continue with the command?(Y/N): ")
                    while execute_command_confirmation.lower() not in ['y', 'n']:
                        print("Y/N?")
                        execute_command_confirmation =  input("Do you want to Continue with the command?(Y/N): ")
                    if execute_command_confirmation.lower()=='y':
                        # CHANGED: Use text instead of cmdLine for subprocess.run
                        cmdExecution = subprocess.run(text, shell=True, env=os.environ.copy(), capture_output=True, text=True)
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
                else:
                    cmdExecution = subprocess.run(text, shell=True, env=os.environ.copy(), capture_output=True, text=True)
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
            except Exception as e:
                print(f"Error Occurred: {e}")

        if len(cmd_history) % 2 == 0 and len(cmd_history) > 0:
            threading.Thread(target=command_prediction_async, daemon=True).start()

    except KeyboardInterrupt:
        print("\n[KeyboardInterrupt] Type 'exit' to quit.")
        continue
    except EOFError:
        print("\n[EOF] Exiting terminal.")
