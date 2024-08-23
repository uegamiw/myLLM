# myLLM Application

This simple desktop application allows you to interact with multiple Language Learning Models (LLMs) from OpenAI and Anthropic. It provides a user-friendly interface to send prompts, receive responses, and manage different models.

## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
   - [Running the Python Script](#running-the-python-script)
   - [Running the Executable](#running-the-executable)
3. [Configuration](#configuration)
   - [Environment Variables](#environment-variables)
   - [Config.json](#configjson)
4. [Behavior with Missing Configuration](#behavior-with-missing-configuration)
5. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites
- Python 3.7 or higher
- pip or conda package manager

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/uegamiw/myllm.git
   cd myllm
   ```

2. Create a virtual environment (optional but recommended):
   ```
   conda create -n myllm-env python=3.9
   conda activate myllm-env
   ```

3. Install the required packages:
   ```
   pip install openai anthropic PyQt5 pyinstaller
   ```

## Usage

### Running the Python Script

1. Ensure you have set up the environment variables and `config.json` file (see [Configuration](#configuration) section).

2. Run the script:
   ```
   python myLLM.py
   ```

### Running the Executable

1. Create the executable using PyInstaller:
   ```
   pyinstaller --onefile --windowed myLLM.py
   ```

2. Find the executable in the `dist` folder.

3. Double-click the executable to run the application.

## Configuration

### Environment Variables

Set the following environment variables with your API keys:

- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key

To set environment variables:

- On Windows:
  ```
  setx OPENAI_API_KEY "your-api-key"
  setx ANTHROPIC_API_KEY "your-api-key"
  ```

- On macOS/Linux:
  ```
  export OPENAI_API_KEY="your-api-key"
  export ANTHROPIC_API_KEY="your-api-key"
  ```

### Config.json

Create a `config.json` file in the same directory as the script with the following structure:

```json
{
    "openai_models": {
        "GPT3.5":"gpt-3.5-turbo",
        "GPT4o-mini": "gpt-4o-mini",
        "GPT4o": "gpt-4o"
    },
    "anthropic_models": {
        "Claude3 Haiku": "claude-3-haiku-20240307",
        "Claude3 Sonnet": "claude-3-sonnet-20240229",
        "Claude3.5 Sonnet": "claude-3-5-sonnet-20240620"
    },
    "prompts": {
        "J2E":"Translate to natural American English.",
        "Proofread":"Please proofread and revise the following English text to make it sound more natural. Additionally, at the end, explain any grammatical errors or areas for improvement",
        "debug": "Below is a Python error message. Please indicate the cause and provide a solution."
    }
}
```

To edit the `config.json`:
1. Open the file in a text editor.
2. Modify the models or prompts as needed.
3. Save the file.

Remember to restart the application after making changes to the environment variables or `config.json` for the changes to take effect.

## Behavior with Missing Configuration

- If `config.json` is missing or cannot be parsed:
  - The application will start with no preset prompts.
  - Default models will be used if available through API keys.

- If some models are missing:
  - Only the available models (those with valid API keys) will be shown in the interface.

- If both API keys are missing:
  - The application will display an error message and exit.
  
## Troubleshooting

If you encounter any issues, please check the log file located at `log/llm_app.log` for more information.

## License
MIT
