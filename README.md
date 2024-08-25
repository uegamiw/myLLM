# myLLM

myLLM is a desktop application that allows users to interact with various language models from OpenAI and Anthropic. It provides a simple interface for sending prompts and receiving responses from these AI models.

## Installation

### Option 1: Running the Python Script

1. Clone the repository:
   ```
   git clone https://github.com/uegamiw/myLLM.git
   cd myLLM
   ```

2. Create a Conda virtual environment (recommended):
   ```
   conda create -n myllm python=3.9
   conda activate myllm
   ```

3. Install the required packages:
   ```
   pip install -r openai anthropic PySide6 pyinstaller
   ```

### Option 2: Using the Distributed Binary

Download the appropriate binary for your operating system from the releases page.

## Configuration

1. Create a `config.json` file in the same directory as the application with the following structure:

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

2. Obtain API keys:
   - OpenAI API key: https://platform.openai.com/account/api-keys
   - Anthropic API key: https://console.anthropic.com/settings/keys

3. Set environment variables:

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

## Usage

1. Run the application:
   - If using the Python script: `python main.py`
   - If using the binary: Double-click the executable file

2. The main window will open with the following components:
   - Prompt template buttons
   - System message input (for Claude models)
   - Prompt input area
   - Model selection radio buttons
   - Send and Append buttons
   - Progress bar
   - Response output area

3. (Optional) Select a prompt template using the buttons at the top
4. Enter your prompt in the text area
5. Select a model using the radio buttons
6. Click "Send" or use the shortcut (Ctrl+Return or Cmd+Return) to generate a response
7. The response will appear in the output area
8. Use the "Append" button (↑) or Alt+Return to add the response to your prompt for continued conversation

### Shortcuts

- Prompt template buttons: Ctrl+1, Ctrl+2, ...
- Model selection: Ctrl+Alt+1, Ctrl+Alt+2, ...
- Send: Ctrl+Return (Cmd+Return on Mac)
- Append: Alt+Return

## Logging

Logs are generated in the `log` directory, with the main log file named `llm_app.log`. This file contains information about the application's operation, including any errors or warnings.

## Troubleshooting

1. If you encounter a "Missing API Key" error, ensure that you've properly set the environment variables for your API keys.
2. If the `config.json` file is missing or corrupted, you'll see an error message in the application. Make sure the file exists and is properly formatted.
3. If no models or prompts are found, check your `config.json` file to ensure it contains the correct structure and data.
4. For any other issues, check the log file (`log/llm_app.log`) for more detailed error messages and information.