
config_example = """
<pre>
    <code>
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
        "Default": "This is a default prompt."
        "J2E":"Translate to natural American English.",
        "Proofread":"Please proofread and revise the following English text to make it sound more natural. Additionally, at the end, explain any grammatical errors or areas for improvement",
    }
}
    </code>
</pre>

"""


message_missing_openaikey = """

<h2>WARNING: OpenAI API Key is missing.</h2>

<ol type="1">
    <li>Get your API key from https://platform.openai.com/account/api-keys</li>
    <li>Set the API key as an environment variable.</li>
</ol>

<h3>MacOS/Linux:</h3>
in your terminal, run the following command:
<pre><code>
export OPENAI_API_KEY="your-api-key"
</code></pre>

<h3>Windows:</h3>
open environment variables and add a new user variable called OPENAI_API_KEY with your API key as the value.
"""

message_missing_anthropickey = """
<h2>WARNING: Anthropic API Key is missing.</h2>

<ol type="1">
    <li>Get your API key from https://console.anthropic.com/settings/keys</li>
    <li>Set the API key as an environment variable.</li>

<h3>MacOS/Linux:</h3>
in your terminal, run the following command:

<pre><code>
export ANTHROPIC_API_KEY="your-api-key"
</code></pre>

<h3>Windows:</h3>
open environment variables and add a new user variable called ANTHROPIC_API
"""

message_missing_both_keys = """
<h1>FATAL ERROR: Both OpenAI and Anthropic API keys are missing. Set the OPENAI_API_KEY and ANTHROPIC_API_KEY environment variables.</h1>

<ol type="1">

    <li>Get your API keys from:
        <ul>
            <li>OpenAI: https://platform.openai.com/account/api-keys</li>
            <li>Anthropic: https://app.anthropic.com/account/api-keys</li>
        </ul>
    </li>

    <li>Set the API keys as environment variables.
        <ul>
            <li>MacOS/Linux:
                <p>in your terminal, run the following commands:</p>
                <p>export OPENAI_API_KEY="your-openai-api-key"</p>
                <p>export ANTHROPIC_API_KEY="your-anthropic-api-key"</p>
            </li>
            <li>Windows:
                <p>open environment variables and add new user variables called OPENAI_API_KEY and ANTHROPIC_API_KEY with your API keys as the values.</p>
            </li>
        </ul>
        """


error_message_missing_config = """
<p>Conifg.json file is missing or corrupted. Place the config.json file in the same directory as the app.
See github.com/uegamiw/myLLM for more information.</p>

Following is the example of the config.json file:
""" + config_example

error_missing_prompts = """
<h1>ERROR: No prompts found in the config.json file.</h1>

<p>Place the prompt templates in the config.json file. See the example below:</p>
""" + config_example

error_missing_models = """
<h1>ERROR: No models found in the config.json file.</h1>
<p>Place the model names and IDs in the config.json file. See the example below:</p>
""" + config_example


welcome_message = """
<font color='gray'>
<h1> Welcome to myLLM! </h1>
<h2> How to use</h2>
<ol type="1">
    <li> (optional) Select a prompt template from the buttons above.</li>
    <li> Enter your prompt in the text area.</li>
    <li> Select a model from the radio buttons.</li>
    <li> Click the 'Send' button to generate a response.</li>
    <li> The response will be displayed in the output area.</li>
    <li> Click the '↑' button to append the response to the prompt.</li>
</ol>

<h2> config.json </h2>
You can customize the models and prompts by editing the config.json file. <br>
Keep the config.json file in the same directory as the app.

<h2> Shortcuts </h2>
<ul>
    <li> Prompt buttons: Ctrl+1, Ctrl+2, ...</li>
    <li> Clear input area: Ctrl+0</li>
    <li> Model radio buttons: Ctrl+Alt+1, Ctrl+Alt+2, ...</li>
    <li> Send button: Ctrl+Return</li>
    <li> ↑ button: Alt+Return</li>
    <li> Zoom in: Ctrl++</li>
    <li> Zoom out: Ctrl+-</li>
</ul>

<h2> Logging </h2>
The app logs and all input/responses are saved in the log directory. Check the log file for more information. <br>

Author: Wataru Uegami, MD PhD (wuegami@gmail.com)
</font>
"""

loading_message = """
<font color='gray'>
<h1>Loading...</h1>
<p>Fetching the response from the API. This may take a few seconds.</p>
</font>
"""