# V1InlineTerminal
This is the Version 1 (V1) of Inline Terminal which is AI augmented Terminal
# inlineTerminal: An AI-Powered Command-Line Interface

## Overview

**inlineTerminal** is a powerful, custom command-line interface (CLI) built in Python, designed to enhance developer productivity and safety. It integrates the Gemini API for natural language-to-shell command translation, offers AI-powered command suggestions, and includes built-in security features like dangerous command detection and a Docker sandbox for safe command execution.

This terminal provides a dynamic, smart environment, especially beneficial for users who frequently switch between different operating systems or need quick command assistance without leaving the prompt.

---

## Features

### 🚀 AI-Enhanced Functionality
* **AI Command Generation (`inline --ask`)**: Translate natural language queries into executable shell commands (e.g., "how do i list files in a directory" $\rightarrow$ `ls` or `dir`).
* **AI Command & Execution (`inline --execute`)**: Generates a list of commands from a query, previews the results in a isolated **Docker sandbox**, and prompts the user for confirmation before executing them on the host machine.
* **Predictive AI Suggestions (Ctrl+T)**: Asynchronously fetches and updates command autocompletion based on your command history, making it smarter as you use it.

### ✨ Usability & Environment Control
* **Smart Autocompletion**: Provides context-aware completion for both common commands and file paths, especially for `cd` and `activate`.
* **Virtual Environment Management**: Built-in `activate` and `deactivate` commands to manage Python virtual environments within the terminal process.
* **Prompt Toolkit Integration**: Utilizes `prompt_toolkit` for a rich, interactive, and aesthetically pleasing terminal experience with key bindings and history.

### 🛡️ Security
* **Dangerous Command Detection**: Automatically identifies high-risk commands (e.g., `rm -rf /`, Windows formatting commands, fork bombs) and requires explicit user confirmation before execution.
* **Docker Sandboxing**: The `inline --execute` feature runs generated commands in an isolated Docker container with **network, memory, and CPU limits**, providing a secure preview of the command's potential impact.

---

## Installation and Setup

### Prerequisites

1.  **Python 3.7+**: The terminal is built in Python.
2.  **Gemini API Key**: You need an API key from Google AI Studio.
3.  **Docker**: Required for the secure command execution sandboxing feature (`inline --execute`).

### Step-by-Step Guide

1.  **Clone the repository:**
    ```bash
    git clone [YOUR_REPO_URL]
    cd inlineTerminal
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You will need to create a `requirements.txt` file containing all the imported libraries: `prompt-toolkit`, `python-dotenv`, `google-genai`, `nltk`, `pathlib`, etc.)*

3.  **Set up Environment Variables:**
    Create a file named `.env` in the project root and add your Gemini API key:
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ```

4.  **Run the Terminal:**
    ```bash
    python inline_terminal.py
    ```

---

## Usage

Once running, the terminal provides a standard CLI experience with additional `inline` commands and special key bindings.

### Core Commands

| Command | Description |
| :--- | :--- |
| `exit` | Quits the terminal application. |
| `cd <path>` | Change directory (standard). |
| `activate <venv-path>` | Activates a Python virtual environment. |
| `deactivate` | Deactivates the current virtual environment. |

### AI and Utility Commands

All AI features are accessed via the `inline` command:

| Command | Description |
| :--- | :--- |
| `inline --help` | Displays the help index for all `inline` commands. |
| `inline --ask <Query>` | **Ask**: Get a command suggestion from the AI based on your query. |
| `inline --execute <Query>` | **Execute**: Get a list of commands, preview their execution in a **Docker sandbox**, and confirm execution on the host. |
| `inline --contact` | Displays the help team's contact details. |

### Key Bindings

| Key | Action |
| :--- | :--- |
| **Tab** | Autocompletes the current word/command. |
| **Right Arrow** | Accepts the auto-suggested command completion. |
| **Ctrl+T** | **Initiates AI Suggestion thread** to update command autocompleter. |
| **Ctrl+C** | Interrupts the current operation (KeyboardInterrupt). |

---

## Code Structure Highlights

* **`DANGEROUS_COMMAND_PATTERNS`**: A list of regex patterns used to intercept potentially harmful commands across Linux, macOS, and Windows.
* **`run_in_docker(cmd)`**: Implements the isolated execution of commands using a secure Docker setup (e.g., `--network none`, memory/CPU limits).
* **`activate_venv/deactivate_venv`**: Manages environment variables and `sys.path` to switch virtual environments in-process.
* **`command_prediction_async`**: A threaded function that calls the Gemini API to fetch a list of predicted next commands, updating the completer without blocking the main prompt loop.
* **`executeQuery(Query)`**: Uses the Gemini API to get a Python list of Windows-compatible commands from a natural language query for the sandbox and execution flow.

---

## Contributing

We welcome contributions to inlineTerminal! Please feel free to submit issues or pull requests to improve the features, security, or usability of the terminal.
