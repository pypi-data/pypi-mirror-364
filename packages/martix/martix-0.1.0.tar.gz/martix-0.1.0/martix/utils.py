"""
Utility functions for Martix library.
"""

from typing import Optional, List
from nio import AsyncClient, MatrixRoom, RoomMessageText

from .types import Message, Command, User, Room


def parse_command(message: Message, prefix: str) -> Optional[Command]:
    """
    Parse a command from a message.
    
    Args:
        message: Message object
        prefix: Command prefix
        
    Returns:
        Command object if message is a command, None otherwise
    """
    text = message.text.strip()
    if not text.startswith(prefix):
        return None
        
    parts = text[len(prefix):].split()
    if not parts:
        return None
        
    command_name = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    
    return Command(
        message._room,
        message._event, 
        message._client,
        command_name,
        args
    )


def create_message_object(room: MatrixRoom, event: RoomMessageText, client: AsyncClient) -> Message:
    """
    Create a Message object from Matrix room and event.
    
    Args:
        room: Matrix room object
        event: Matrix message event
        client: Matrix client instance
        
    Returns:
        Message object
    """
    return Message(room, event, client)


def create_user_object(user_id: str, client: AsyncClient) -> User:
    """
    Create a User object from user ID.
    
    Args:
        user_id: Matrix user ID
        client: Matrix client instance
        
    Returns:
        User object
    """
    return User(user_id=user_id)


def create_room_object(room: MatrixRoom) -> Room:
    """
    Create a Room object from Matrix room.
    
    Args:
        room: Matrix room object
        
    Returns:
        Room object
    """
    return Room(
        room_id=room.room_id,
        name=room.display_name,
        topic=room.topic,
        member_count=room.member_count,
        is_encrypted=room.encrypted
    )


def format_user_id(username: str, homeserver: str) -> str:
    """
    Format a username and homeserver into a full Matrix user ID.
    
    Args:
        username: Username without @ or domain
        homeserver: Homeserver domain
        
    Returns:
        Full Matrix user ID
    """
    if not username.startswith('@'):
        username = f'@{username}'
    if ':' not in username:
        username = f'{username}:{homeserver}'
    return username


def extract_homeserver(user_id: str) -> str:
    """
    Extract homeserver domain from a Matrix user ID.
    
    Args:
        user_id: Full Matrix user ID
        
    Returns:
        Homeserver domain
    """
    if ':' in user_id:
        return user_id.split(':', 1)[1]
    return ""


def is_valid_room_id(room_id: str) -> bool:
    """
    Check if a string is a valid Matrix room ID.
    
    Args:
        room_id: Room ID to validate
        
    Returns:
        True if valid room ID, False otherwise
    """
    return room_id.startswith('!') and ':' in room_id


def is_valid_user_id(user_id: str) -> bool:
    """
    Check if a string is a valid Matrix user ID.
    
    Args:
        user_id: User ID to validate
        
    Returns:
        True if valid user ID, False otherwise
    """
    return user_id.startswith('@') and ':' in user_id


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe file operations.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import re
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip('. ')
    return filename or 'unnamed_file'