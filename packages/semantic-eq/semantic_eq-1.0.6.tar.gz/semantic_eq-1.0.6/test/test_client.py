from client_lib import SemanticEQ


SEQ_API_KEY = "sk-YZjRIKriNQr-e7cZL4b9thtb3vtlYMRRRd-6XkrPoG-OzdLv"

# Initialize SemanticEQ client, compress your system prompt
seq_client = SemanticEQ(api_key=SEQ_API_KEY, system_prompt="you are a helpful assistant")

# Compress the original user prompt and system prompt
compressed = seq_client.compress_prompt(user_prompt="I want you to tell me about mars")

print(compressed)