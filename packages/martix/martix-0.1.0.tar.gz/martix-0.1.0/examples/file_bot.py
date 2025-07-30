"""
File handling bot example using Martix library.

This example demonstrates how to handle file uploads and downloads,
including images, documents, and other media types.
"""

import martix
import os
from pathlib import Path

user = "@filebot:example.com"
password = "your_password"
host = "https://matrix.example.com"

client = martix.Client(user, password, host)

downloads_dir = Path("downloads")
downloads_dir.mkdir(exist_ok=True)


@client.on_ready()
async def ready():
    """Called when the bot is ready."""
    print(f"File bot logged in as {client.user.username}")


@client.on_message()
async def handle_files(message: martix.Message):
    """Handle incoming files."""
    if message.photo:
        print(f"Received photo: {message.photo.filename}")
        
        save_path = downloads_dir / f"photo_{message.event_id}_{message.photo.filename}"
        await message.photo.download(client.client, str(save_path))
        
        await message.reply(f"Photo saved as {save_path.name}")
        await message.react("📸")
        
    elif message.document:
        print(f"Received document: {message.document.filename}")
        
        save_path = downloads_dir / f"doc_{message.event_id}_{message.document.filename}"
        await message.document.download(client.client, str(save_path))
        
        await message.reply(f"Document saved as {save_path.name}")
        await message.react("📄")
        
    elif message.audio:
        print(f"Received audio: {message.audio.filename}")
        
        save_path = downloads_dir / f"audio_{message.event_id}_{message.audio.filename}"
        await message.audio.download(client.client, str(save_path))
        
        duration = message.audio.duration or 0
        await message.reply(f"Audio saved as {save_path.name} (Duration: {duration}ms)")
        await message.react("🎵")


@client.on_command("send_image")
async def send_image_command(command: martix.Command):
    """Send a test image."""
    if not command.args:
        await command.reply("Usage: !send_image <path_to_image>")
        return
        
    image_path = command.args[0]
    if not os.path.exists(image_path):
        await command.reply("Image file not found!")
        return
        
    try:
        await client.send_image(command.room.room_id, image_path, "Test image")
        await command.reply("Image sent successfully!")
    except Exception as e:
        await command.reply(f"Failed to send image: {e}")


@client.on_command("send_file")
async def send_file_command(command: martix.Command):
    """Send a test file."""
    if not command.args:
        await command.reply("Usage: !send_file <path_to_file>")
        return
        
    file_path = command.args[0]
    if not os.path.exists(file_path):
        await command.reply("File not found!")
        return
        
    try:
        await client.send_file(command.room.room_id, file_path)
        await command.reply("File sent successfully!")
    except Exception as e:
        await command.reply(f"Failed to send file: {e}")


@client.on_command("list_downloads")
async def list_downloads_command(command: martix.Command):
    """List all downloaded files."""
    files = list(downloads_dir.glob("*"))
    if not files:
        await command.reply("No downloaded files.")
        return
        
    file_list = "\n".join([f"- {f.name}" for f in files])
    await command.reply(f"Downloaded files:\n{file_list}")


if __name__ == "__main__":
    client.run()