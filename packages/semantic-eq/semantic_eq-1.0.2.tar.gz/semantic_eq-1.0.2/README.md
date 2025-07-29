# Semantic EQ SDK

This package provides a simple Python client for the Semantic EQ API.

## Installation
```bash
pip install semantic-eq
```

## Usage
```python
from semantic_eq_sdk import SemanticEQ

# Initialize the client with your API key
client = SemanticEQ(api_key="YOUR_SEMANTIC_EQ_API_KEY")

# Optimize a prompt
original_prompt = "Your long and detailed prompt..."
result = client.optimize_prompt(original_prompt)

print("Optimized Prompt:", result.optimized_prompt)
```

## Publishing a New Version (for Maintainers)

Publishing the SDK is handled by a script that automates the entire process.

**Prerequisites:**
1.  **PyPI Account:** You need an account on [PyPI](https://pypi.org) and an API token.
2.  **Twine Configuration:** Your local machine must be configured to authenticate with PyPI. You can do this by setting the `TWINE_USERNAME` and `TWINE_PASSWORD` environment variables.

**To publish a new version:**
1.  Navigate to the SDK directory: `cd semantic_eq_sdk`
2.  Run the publishing script. You have two options:
    *   **To automatically bump the patch version** (e.g., `1.0.1` -> `1.0.2`), run the script without arguments:
        ```bash
        ./publish_sdk.sh
        ```
    *   **To specify an exact version** (e.g., for a major release like `2.0.0`), provide it as an argument:
        ```bash
        ./publish_sdk.sh 2.0.0
        ```
3.  The script will handle everything else automatically.