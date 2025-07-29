import os
import openai
from semantic_eq_sdk.client import SemanticEQ
from dotenv import load_dotenv

# --- Configuration ---
# Load environment variables from .env file in the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Get API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SEMANTIC_EQ_API_KEY = os.getenv("SEMANTIC_EQ_API_KEY")

if not OPENAI_API_KEY or not SEMANTIC_EQ_API_KEY:
    print("❌ Error: Please set OPENAI_API_KEY and SEMANTIC_EQ_API_KEY environment variables.")
    print("You can create a .env file in this directory with the following format:")
    print("OPENAI_API_KEY='your_openai_key'")
    print("SEMANTIC_EQ_API_KEY='your_semantic_eq_key'")
    exit(1)

# --- Sample Prompt ---
# A detailed prompt that has potential for significant optimization
original_prompt = """
Please act as a senior marketing consultant and write a comprehensive go-to-market strategy
for a new productivity application that is designed for busy professionals. The application
helps users manage their tasks, calendars, and notes all in one place. It has a unique AI
feature that automatically suggests task prioritization based on user behavior and deadlines.
The target audience is project managers, entrepreneurs, and consultants in the tech industry.
The strategy should cover key areas such as target audience analysis, value proposition,
messaging, channel strategy (including digital and content marketing), and key performance
indicators (KPIs) to measure success over the first six months. Please provide a detailed
and actionable plan.
"""

# --- Initialization ---
try:
    # Initialize the OpenAI client
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

    # Initialize the Semantic EQ client
    seq_client = SemanticEQ(api_key=SEMANTIC_EQ_API_KEY)

    print("✅ Clients initialized successfully.")
except Exception as e:
    print(f"❌ Error initializing clients: {e}")
    exit(1)


# --- Optimization and Comparison ---
print("\n" + "="*50)
print("🚀 Optimizing Prompt with Semantic EQ...")
print("="*50)

try:
    # 1. Optimize the prompt using the Semantic EQ SDK
    optimized_prompt_response = seq_client.optimize_prompt(original_prompt)
    optimized_prompt = optimized_prompt_response.optimized_prompt
    
    # 2. Get token counts (approximated by character count as a simple metric)
    original_tokens = len(original_prompt.split())
    optimized_tokens = len(optimized_prompt.split())
    reduction_percentage = ((original_tokens - optimized_tokens) / original_tokens) * 100

    print(f"\n📝 Original Prompt ({original_tokens} words):\n---")
    print(original_prompt)
    
    print(f"\n✨ Optimized Prompt ({optimized_tokens} words):\n---")
    print(optimized_prompt)
    
    print("\n" + "="*50)
    print("📊 Results & Savings")
    print("="*50)
    print(f"Token Reduction: {original_tokens} -> {optimized_tokens} words")
    print(f"Savings: {reduction_percentage:.2f}%")

    print("\n" + "="*50)
    print("📞 Calling OpenAI with Both Prompts...")
    print("="*50)

    # 3. Call OpenAI with the ORIGINAL prompt
    print("\n--- 1. Calling with Original Prompt ---")
    original_response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": original_prompt}],
        max_tokens=250
    )
    print("✅ OpenAI response (Original):\n", original_response.choices[0].message.content)
    print(f"Tokens Used (Original): {original_response.usage.total_tokens}")

    # 4. Call OpenAI with the OPTIMIZED prompt
    print("\n--- 2. Calling with Optimized Prompt ---")
    optimized_response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": optimized_prompt}],
        max_tokens=250
    )
    print("✅ OpenAI response (Optimized):\n", optimized_response.choices[0].message.content)
    print(f"Tokens Used (Optimized): {optimized_response.usage.total_tokens}")

    print("\n" + "="*50)
    print("🎉 Comparison Complete!")
    print(f"Total tokens saved on this call: {original_response.usage.total_tokens - optimized_response.usage.total_tokens}")
    print("="*50)

except Exception as e:
    print(f"\n❌ An error occurred during the process: {e}") 