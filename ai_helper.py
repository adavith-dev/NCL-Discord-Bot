import os
import openai
import asyncio

openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_response(prompt, model="gpt-3.5-turbo"):
    try:
        response = await asyncio.to_thread(
            lambda: openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI ERROR: {e}"
