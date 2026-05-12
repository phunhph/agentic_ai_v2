import os
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    try:
        print("Testing Gemini 2.5 Flash via LiteLLM...")
        response = completion(
            model="gemini/gemini-2.5-flash",
            messages=[{"role": "user", "content": "Hello, are you there?"}],
            api_key=os.getenv("GEMINI_API_KEY")
        )
        print("Response:", response.choices[0].message.content)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_gemini()
