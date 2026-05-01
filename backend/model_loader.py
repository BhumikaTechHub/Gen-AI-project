import os
from groq import Groq

client = Groq(
    api_key=""
)

def ask_model(instruction, inp):

    prompt = f"""Instruction:
{instruction}

Input:
{inp}

Output:
"""

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role":"user","content":prompt}
            ],
            temperature=0.2
        )

        return chat.choices[0].message.content
    except Exception as e:
        print(f"Model error: {e}")
        return ""