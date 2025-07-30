# Semantic EQ Client

This package provides a simple Python client for the Semantic EQ API.

## Installation
```bash
pip install semantic-eq
```

## Usage

```python
from client_lib import SemanticEQ
import openai

# Initialize SemanticEQ client, compress your system prompt
seq_client = SemanticEQ(api_key="YOUR_SEMANTIC_EQ_API_KEY", system_prompt="<your-input-system-prompt>")

# Compress the original user prompt and system prompt
compressed = seq_client.compress_prompt(user_prompt="Your long and detailed prompt...")

# Call OpenAI's GPT-4 with the compressed prompt
openai.api_key = "YOUR_OPENAI_API_KEY"
response = openai.ChatCompletion.create(
    model="gpt-4o",  # or "gpt-4" if preferred
    messages=[
        {"role": "system", "content": compressed.compressed_system_prompt},
        {"role": "user", "content": compressed.compressed_user_prompt}
    ]
)

# Print the response from GPT-4
print(response["choices"][0]["message"]["content"])

```

## Publishing a New Version (for Maintainers)

Publishing the client is handled by a script that automates the entire process.

**Prerequisites:**
1.  **PyPI Account:** You need an account on [PyPI](https://pypi.org) and an API token.
2.  **Twine Configuration:** Your local machine must be configured to authenticate with PyPI. You can do this by setting the `TWINE_USERNAME` and `TWINE_PASSWORD` environment variables.

**To publish a new version:**
1.  Navigate to the client directory: `cd semantic_eq_client`
2.  Run the publishing script. You have two options:
    *   **To automatically bump the patch version** (e.g., `1.0.1` -> `1.0.2`), run the script without arguments:
        ```bash
        ./publish_client_lib.sh
        ```
    *   **To specify an exact version** (e.g., for a major release like `2.0.0`), provide it as an argument:
        ```bash
        ./publish_client_lib.sh 2.0.0
        ```
3.  The script will handle everything else automatically.