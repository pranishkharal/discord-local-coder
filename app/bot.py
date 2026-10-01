import os
import requests
import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "0"))
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3-coder:latest")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def ask_ollama(message):
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful coding assistant. Answer clearly and concisely."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            "stream": False
        },
        timeout=300
    )

    response.raise_for_status()
    return response.json()["message"]["content"]


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print(f"Listening in channel: {CHANNEL_ID}")
    print(f"Authorized user: {AUTHORIZED_USER_ID}")
    print(f"Ollama model: {OLLAMA_MODEL}")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id != CHANNEL_ID:
        return

    if message.author.id != AUTHORIZED_USER_ID:
        return

    print(f"[{message.author}] {message.content}")

    try:
        async with message.channel.typing():
            answer = await client.loop.run_in_executor(
                None,
                ask_ollama,
                message.content
            )

        if len(answer) <= 2000:
            await message.channel.send(answer)
        else:
            for i in range(0, len(answer), 1900):
                await message.channel.send(answer[i:i + 1900])

    except Exception as e:
        print(f"AI error: {e}")
        await message.channel.send(f"AI error: `{type(e).__name__}`")


if not TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN is missing from .env")

client.run(TOKEN)
