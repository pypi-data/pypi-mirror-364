"""
Basic bot example using Martix library.

This example demonstrates how to create a simple Matrix bot
that responds to messages and commands.
"""

import martix

user = "@filebot:example.com"
password = "your_password"
host = "https://matrix.example.com"

client = martix.Client(user, password, host)
client.command_prefix = "!"


@client.on_ready()
async def ready():
    """Called when the bot is ready and logged in."""
    print(f"Logged in as {client.user.username}")
    print("Bot is ready!")

@client.on_message()
async def on_message(message: martix.Message):
    if message.text == "/start":
        await message.reply("hi")

if __name__ == "__main__":
    client.run()