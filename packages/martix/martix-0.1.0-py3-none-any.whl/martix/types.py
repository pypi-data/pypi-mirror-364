"""
Type definitions for Martix library.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

from nio import AsyncClient, MatrixRoom, RoomMessageText


@dataclass
class User:
    """
    Represents a Matrix user.
    
    Attributes:
        user_id: Full Matrix user ID
        display_name: User's display name
        avatar_url: User's avatar URL
        username: Username part of user ID
    """
    user_id: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    
    @property
    def username(self) -> str:
        """Extract username from user ID."""
        return self.user_id.split(':')[0][1:]  # Remove @ and domain


@dataclass 
class Room:
    """
    Represents a Matrix room.
    
    Attributes:
        room_id: Room ID
        name: Room name
        topic: Room topic
        member_count: Number of members
        is_encrypted: Whether room is encrypted
    """
    room_id: str
    name: Optional[str] = None
    topic: Optional[str] = None
    member_count: int = 0
    is_encrypted: bool = False


@dataclass
class File:
    """
    Represents a file attachment.
    
    Attributes:
        url: Matrix content URI
        filename: Original filename
        size: File size in bytes
        mimetype: MIME type
    """
    url: str
    filename: str
    size: Optional[int] = None
    mimetype: Optional[str] = None
    
    async def download(self, client: AsyncClient, save_path: Optional[str] = None) -> bytes:
        """
        Download the file content.
        
        Args:
            client: Matrix client instance
            save_path: Path to save file (optional)
            
        Returns:
            File content as bytes
        """
        response = await client.download(self.url)
        content = response.body
        
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(content)
                
        return content


@dataclass
class Photo(File):
    """
    Represents a photo attachment.
    
    Attributes:
        width: Image width
        height: Image height
    """
    width: Optional[int] = None
    height: Optional[int] = None


@dataclass
class Audio(File):
    """
    Represents an audio attachment.
    
    Attributes:
        duration: Audio duration in milliseconds
    """
    duration: Optional[int] = None


@dataclass
class Document(File):
    """Represents a document attachment."""
    pass


class Message:
    """
    Represents a Matrix message.
    
    This class provides access to message content, sender information,
    room details, and various message properties.
    """
    
    def __init__(self, room: MatrixRoom, event: RoomMessageText, client: AsyncClient):
        """
        Initialize a Message object.
        
        Args:
            room: Matrix room object
            event: Matrix message event
            client: Matrix client instance
        """
        self._room = room
        self._event = event
        self._client = client
        self._user: Optional[User] = None
        self._room_obj: Optional[Room] = None
        
    @property
    def text(self) -> str:
        """Get message text content."""
        return self._event.body
        
    @property
    def event_id(self) -> str:
        """Get message event ID."""
        return self._event.event_id
        
    @property
    def time(self) -> datetime:
        """Get message timestamp."""
        return datetime.fromtimestamp(self._event.server_timestamp / 1000)
        
    @property
    def user(self) -> User:
        """Get message sender information."""
        if not self._user:
            self._user = User(
                user_id=self._event.sender,
                display_name=self._room.user_name(self._event.sender),
                avatar_url=self._room.avatar_url(self._event.sender)
            )
        return self._user
        
    @property
    def room(self) -> Room:
        """Get room information."""
        if not self._room_obj:
            self._room_obj = Room(
                room_id=self._room.room_id,
                name=self._room.display_name,
                topic=self._room.topic,
                member_count=self._room.member_count,
                is_encrypted=self._room.encrypted
            )
        return self._room_obj
        
    @property
    def photo(self) -> Optional[Photo]:
        """Get photo attachment if message contains one."""
        if hasattr(self._event, 'url') and self._event.msgtype == "m.image":
            info = getattr(self._event, 'info', {})
            return Photo(
                url=self._event.url,
                filename=self._event.body,
                size=info.get('size'),
                mimetype=info.get('mimetype'),
                width=info.get('w'),
                height=info.get('h')
            )
        return None
        
    @property
    def audio(self) -> Optional[Audio]:
        """Get audio attachment if message contains one."""
        if hasattr(self._event, 'url') and self._event.msgtype == "m.audio":
            info = getattr(self._event, 'info', {})
            return Audio(
                url=self._event.url,
                filename=self._event.body,
                size=info.get('size'),
                mimetype=info.get('mimetype'),
                duration=info.get('duration')
            )
        return None
        
    @property
    def document(self) -> Optional[Document]:
        """Get document attachment if message contains one."""
        if hasattr(self._event, 'url') and self._event.msgtype == "m.file":
            info = getattr(self._event, 'info', {})
            return Document(
                url=self._event.url,
                filename=self._event.body,
                size=info.get('size'),
                mimetype=info.get('mimetype')
            )
        return None
        
    async def reply(self, text: str) -> None:
        """
        Reply to this message.
        
        Args:
            text: Reply text
        """
        content = {
            "msgtype": "m.text",
            "body": text,
            "m.relates_to": {
                "m.in_reply_to": {
                    "event_id": self.event_id
                }
            }
        }
        await self._client.room_send(self._room.room_id, "m.room.message", content)
        
    async def react(self, emoji: str) -> None:
        """
        React to this message with an emoji.
        
        Args:
            emoji: Emoji to react with
        """
        content = {
            "m.relates_to": {
                "rel_type": "m.annotation",
                "event_id": self.event_id,
                "key": emoji
            }
        }
        await self._client.room_send(self._room.room_id, "m.reaction", content)


class Command(Message):
    """
    Represents a command message.
    
    This class extends Message with command-specific functionality,
    including command name and arguments parsing.
    """
    
    def __init__(self, room: MatrixRoom, event: RoomMessageText, client: AsyncClient, 
                 name: str, args: List[str]):
        """
        Initialize a Command object.
        
        Args:
            room: Matrix room object
            event: Matrix message event
            client: Matrix client instance
            name: Command name
            args: Command arguments
        """
        super().__init__(room, event, client)
        self.name = name
        self.args = args
        
    @property
    def args_string(self) -> str:
        """Get command arguments as a single string."""
        return ' '.join(self.args)