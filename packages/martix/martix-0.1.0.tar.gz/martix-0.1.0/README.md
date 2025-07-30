# Martix - Simplified Matrix Library for Python

Martix is a high-level Python library that simplifies working with the Matrix protocol. It provides an intuitive, telegram-bot-like API for creating Matrix bots and clients.

## Features

- **Simple API**: Easy-to-use decorators and methods inspired by python-telegram-bot
- **Event Handling**: Comprehensive event system for messages, commands, invites, and more
- **File Support**: Built-in support for sending and receiving files, images, audio, and documents
- **Persistent State**: Automatic sync token management to resume from last position
- **Type Safety**: Full type hints and dataclass-based objects
- **Async/Await**: Built on asyncio for high performance
- **Error Handling**: Comprehensive exception system

## Installation

```bash
pip install martix
```

Or install from source:

```bash
git clone https://github.com/daradege/martix.git
cd martix
pip install -e .
```

## Quick Start

```python
import martix

# Initialize client
user = "@mybot:example.com"
password = "my_password"
host = "https://matrix.example.com"

client = martix.Client(user, password, host)
client.command_prefix = "!"  # Default is "/"

@client.on_ready()
async def ready():
    print(f"Logged in as {client.user.username}")

@client.on_message()
async def on_message(message: martix.Message):
    print(f"Message from {message.user.display_name}: {message.text}")
    
    # Handle different message types
    if message.photo:
        await message.reply("Nice photo!")
    elif message.document:
        content = await message.document.download(client.client)
        await message.reply(f"Downloaded {len(content)} bytes")

@client.on_command("start")
async def start_command(command: martix.Command):
    await command.reply(f"Hello {command.user.display_name}!")

@client.on_command("echo")
async def echo_command(command: martix.Command):
    if command.args:
        await command.reply(f"You said: {command.args_string}")

# Start the bot
client.run()
```

## Message Types

Martix supports all Matrix message types:

```python
@client.on_message()
async def handle_message(message: martix.Message):
    # Text messages
    print(message.text)
    
    # Images
    if message.photo:
        await message.photo.download(client.client, "image.jpg")
    
    # Documents
    if message.document:
        content = await message.document.download(client.client)
    
    # Audio files
    if message.audio:
        print(f"Audio duration: {message.audio.duration}ms")
    
    # Message metadata
    print(f"From: {message.user.display_name}")
    print(f"Room: {message.room.name}")
    print(f"Time: {message.time}")
```

## Sending Messages

```python
# Send text message
await client.send_message(room_id, "Hello World!")

# Send with reply
await message.reply("This is a reply")

# Send files
await client.send_file(room_id, "document.pdf")
await client.send_image(room_id, "photo.jpg", "Caption here")

# React to messages
await message.react("👍")
```

## Room Management

```python
# Join/leave rooms
await client.join_room("!room:example.com")
await client.leave_room("!room:example.com")

# Get room list
rooms = await client.get_rooms()
for room in rooms:
    print(f"Room: {room.name} ({room.member_count} members)")

# Handle invites
@client.on_invite()
async def on_invite(room, event):
    await client.join_room(room.room_id)
    await client.send_message(room.room_id, "Thanks for inviting me!")
```

## Event Handlers

Martix supports various event types:

```python
@client.on_ready()
async def ready():
    """Called when bot is ready"""
    pass

@client.on_message()
async def on_message(message: martix.Message):
    """Handle all messages"""
    pass

@client.on_command("commandname")
async def command_handler(command: martix.Command):
    """Handle specific commands"""
    pass

@client.on_invite()
async def on_invite(room, event):
    """Handle room invitations"""
    pass

@client.on_member_join()
async def on_member_join(room, event):
    """Handle member joins"""
    pass

@client.on_member_leave()
async def on_member_leave(room, event):
    """Handle member leaves"""
    pass
```

## Configuration

```python
client = martix.Client(
    user_id="@bot:example.com",
    password="password",
    homeserver="https://matrix.example.com",
    device_name="My Bot"  # Optional
)

# Set command prefix
client.command_prefix = "!"  # Default is "/"
```

## Error Handling

```python
from martix import MartixError, AuthenticationError, NetworkError

try:
    await client.start()
except AuthenticationError:
    print("Login failed - check credentials")
except NetworkError:
    print("Connection failed - check homeserver URL")
except MartixError as e:
    print(f"Martix error: {e}")
```

## Advanced Usage

### File Downloads

```python
@client.on_message()
async def handle_files(message: martix.Message):
    if message.document:
        # Download to memory
        content = await message.document.download(client.client)
        
        # Download to file
        await message.document.download(client.client, "downloaded_file.pdf")
        
        # Access file metadata
        print(f"Filename: {message.document.filename}")
        print(f"Size: {message.document.size} bytes")
        print(f"MIME type: {message.document.mimetype}")
```

### Custom Event Handling

```python
# Multiple handlers for the same event
@client.on_message()
async def log_message(message: martix.Message):
    print(f"Logged: {message.text}")

@client.on_message()
async def process_message(message: martix.Message):
    # Process the message
    pass

# Multiple command handlers
@client.on_command("help")
async def help_command(command: martix.Command):
    await command.reply("Help text here")

@client.on_command("help")
async def log_help_usage(command: martix.Command):
    print(f"Help command used by {command.user.username}")
```

## Examples

Check the `examples/` directory for complete bot examples:

- `basic_bot.py` - Simple message and command handling
- `file_bot.py` - File upload/download handling

## Requirements

- Python 3.8+
- matrix-nio
- aiofiles
- Pillow (for image handling)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines.

## Support

- GitHub Issues: https://github.com/daradege/martix/issues