import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ✅ Your default Groq API key (public/testing/demo)
DEFAULT_API_KEY = "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"

def ask(prompt, api_key=None):
    api_key = api_key or os.getenv("GROQ_API_KEY") or DEFAULT_API_KEY

    if not api_key.startswith("gsk_"):
        raise ValueError("No valid API key found. Please provide or set one.")

    client = Groq(api_key=api_key)

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_completion_tokens=4096,
        top_p=0.95,
        stream=True,
        stop=None,
    )

    for chunk in completion:
        print(chunk.choices[0].delta.content or "", end="")
