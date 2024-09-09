# myLLM

User-friendly desktop client for Large Language Models (LLMs). This application offers a seamless interface to interact with cutting-edge AI models from OpenAI and Anthropic.

<img width="1312" alt="image" src="https://github.com/user-attachments/assets/c6aaabdb-ba90-47de-8de1-58c223698ba1">


## Key Features:
- Customizable prompts to enhance your AI interactions
- Supprt for the multiple requests in parallel
- Extensive keyboard shortcuts for efficient navigation
- Support for OpenAI and/or Anthropic APIs

## Installation

### Option 1: Using the Distributed Binary

Download the appropriate binary (exe) from the [release page](https://github.com/uegamiw/myLLM/releases).

### Option 2: Running the Python Script

1. Clone the repository:
   ```bash
   git clone https://github.com/uegamiw/myLLM.git
   cd myLLM
   ```

2. Create a Conda virtual environment (recommended):
   ```bash
   conda create -n myllm python=3.12
   conda activate myllm
   ```

3. Install the required packages:
   ```
   pip install -r openai anthropic PySide6
   ```

## Configuration

1. Obtain API keys:
   - OpenAI API key: https://platform.openai.com/account/api-keys
   - Anthropic API key: https://console.anthropic.com/settings/keys

2. Set environment variables:

   For MacOS/Linux:
   ```
   export OPENAI_API_KEY="your-openai-api-key"
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   ```

   For Windows:
   1. Open the Start menu and search for "Environment Variables"
   2. Click "Edit the system environment variables"
   3. Click the "Environment Variables" button
   4. Under "User variables", click "New"
   5. Add `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` with their respective values

3. When the app launches for the first time, a `config.json` file will be automatically created with default values if it doesn't already exist. Edit the `config.json` file to include the model names and IDs you want to use in the application. The model names will be displayed as options in the application's model selection radio buttons. Additionally, you can add/edit prompt templates to the `prompts` section. The first 5 prompts will be displayed as buttons at the top of the application.

Example `config.json` file:

```json
{
    "openai_models": {
        "GPT3.5": "gpt-3.5-turbo",
        "GPT4o-mini": "gpt-4o-mini",
        "GPT4o": "gpt-4o"
    },
    "anthropic_models": {
        "Claude3 Haiku": "claude-3-haiku-20240307",
        "Claude3 Sonnet": "claude-3-sonnet-20240229",
        "Claude3.5 Sonnet": "claude-3-5-sonnet-20240620"
    },
    "prompts": {
        "Default": "This is a default prompt.",
        "J2E": "Translate to natural American English.",
        "Proofread": "Please proofread and revise the following English text to make it sound more natural. Additionally, at the end, explain any grammatical errors or areas for improvement"
    }
}
```

## Usage

1. Run the application:
   - If using the binary: Double-click the executable file
   - If using the Python script: `python app.py`
2. (Optional) Select a prompt template using the buttons at the top
3. Enter your prompt in the text area
4. Select a model using the radio buttons
5. Click "Send" or use the shortcut (Ctrl+Return or Cmd+Return) to generate a response
6. The response will appear in the output area
7. Use the "Append" button or Alt+Return to add the response to your prompt for continued conversation

## Shortcuts

- Prompt template buttons: Ctrl+1, Ctrl+2, ...
- Clear prompt: Ctrl+0
- Model selection: Ctrl+Alt+1, Ctrl+Alt+2, ...
- Send: Ctrl+Return
- Append the response to the input area: Alt+Return
- Focus on prompt text area: Ctrl+L
- Focus on the search box: Ctrl+F

## Compile Executable

For Windows:

```
pip install nuitka
python -m nuitka --onefile --plugin-enable=pyside6 --windows-console-mode=disable app.py
```

## Troubleshooting

1. If you encounter a "Missing API Key" error, ensure that you've properly set the environment variables for your API keys.
2. For any other issues, check the log file (`log/llm_app.log`) for more detailed error messages and information.
