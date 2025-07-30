"""
Main client class for Martix library.
"""

import asyncio
import json
import os
from typing import Optional, Callable, Dict, Any, List
from pathlib import Path

from nio import AsyncClient, MatrixRoom, RoomMessageText, LoginResponse, SyncResponse
from nio.events import Event, RoomMessage, InviteEvent, RoomMemberEvent

from .types import Message, Command, User, Room, File
from .events import EventHandler
from .exceptions import AuthenticationError, NetworkError, MartixError
from .utils import parse_command, create_message_object, create_user_object, create_room_object


class Client:
    """
    Main client class for interacting with Matrix homeserver.
    
    This class provides a high-level interface for Matrix operations,
    including authentication, message handling, and event processing.
    """
    
    def __init__(self, user_id: str, password: str, homeserver: str, device_name: str = "Martix Bot"):
        """
        Initialize the Matrix client.
        
        Args:
            user_id: Full Matrix user ID (e.g., @username:example.com)
            password: User password
            homeserver: Matrix homeserver URL
            device_name: Device name for this session
        """
        self.user_id = user_id
        self.password = password
        self.homeserver = homeserver
        self.device_name = device_name
        self.command_prefix = "/"
        
        self._client: Optional[AsyncClient] = None
        self._event_handler = EventHandler()
        self._user: Optional[User] = None
        self._sync_token_file = Path(".martix_sync_token")
        self._next_batch: Optional[str] = None
        
    @property
    def user(self) -> Optional[User]:
        """Get the current authenticated user."""
        return self._user
        
    @property
    def client(self) -> AsyncClient:
        """Get the underlying nio AsyncClient."""
        if not self._client:
            raise MartixError("Client not initialized. Call start() first.")
        return self._client
        
    def on_ready(self) -> Callable:
        """
        Decorator for ready event handler.
        
        Returns:
            Decorator function for ready event
        """
        return self._event_handler.on_ready
        
    def on_message(self) -> Callable:
        """
        Decorator for message event handler.
        
        Returns:
            Decorator function for message events
        """
        return self._event_handler.on_message
        
    def on_command(self, command_name: str) -> Callable:
        """
        Decorator for command event handler.
        
        Args:
            command_name: Name of the command to handle
            
        Returns:
            Decorator function for command events
        """
        return self._event_handler.on_command(command_name)
        
    def on_invite(self) -> Callable:
        """
        Decorator for room invite event handler.
        
        Returns:
            Decorator function for invite events
        """
        return self._event_handler.on_invite
        
    def on_member_join(self) -> Callable:
        """
        Decorator for member join event handler.
        
        Returns:
            Decorator function for member join events
        """
        return self._event_handler.on_member_join
        
    def on_member_leave(self) -> Callable:
        """
        Decorator for member leave event handler.
        
        Returns:
            Decorator function for member leave events
        """
        return self._event_handler.on_member_leave
        
    async def start(self) -> None:
        """
        Start the Matrix client and begin processing events.
        
        Raises:
            AuthenticationError: If login fails
            NetworkError: If connection fails
        """
        self._client = AsyncClient(self.homeserver, self.user_id, device_id=self.device_name)
        
        try:
            response = await self._client.login(self.password, device_name=self.device_name)
            if not isinstance(response, LoginResponse):
                raise AuthenticationError(f"Login failed: {response}")
                
            self._user = create_user_object(self.user_id, self._client)
            
            self._load_sync_token()
            
            self._client.add_event_callback(self._handle_message, RoomMessageText)
            self._client.add_event_callback(self._handle_invite, InviteEvent)
            self._client.add_event_callback(self._handle_member_event, RoomMemberEvent)
            
            await self._event_handler.trigger_ready()
            
            await self._sync_forever()
            
        except Exception as e:
            if isinstance(e, (AuthenticationError, NetworkError)):
                raise
            raise NetworkError(f"Failed to start client: {e}")
            
    def run(self) -> None:
        """
        Synchronous wrapper for start() method.
        
        This method creates an event loop and runs the client.
        """
        asyncio.run(self.start())
        
    async def send_message(self, room_id: str, text: str, reply_to: Optional[str] = None) -> None:
        """
        Send a text message to a room.
        
        Args:
            room_id: Target room ID
            text: Message text
            reply_to: Event ID to reply to (optional)
        """
        content = {"msgtype": "m.text", "body": text}
        
        if reply_to:
            content["m.relates_to"] = {"m.in_reply_to": {"event_id": reply_to}}
            
        await self.client.room_send(room_id, "m.room.message", content)
        
    async def send_file(self, room_id: str, file_path: str, filename: Optional[str] = None) -> None:
        """
        Send a file to a room.
        
        Args:
            room_id: Target room ID
            file_path: Path to the file
            filename: Custom filename (optional)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise MartixError(f"File not found: {file_path}")
            
        with open(file_path, "rb") as f:
            response, _ = await self.client.upload(f, content_type="application/octet-stream")
            
        content = {
            "msgtype": "m.file",
            "body": filename or file_path.name,
            "url": response.content_uri,
            "info": {"size": file_path.stat().st_size}
        }
        
        await self.client.room_send(room_id, "m.room.message", content)
        
    async def send_image(self, room_id: str, image_path: str, caption: Optional[str] = None) -> None:
        """
        Send an image to a room.
        
        Args:
            room_id: Target room ID
            image_path: Path to the image
            caption: Image caption (optional)
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise MartixError(f"Image not found: {image_path}")
            
        with open(image_path, "rb") as f:
            response, _ = await self.client.upload(f, content_type="image/jpeg")
            
        content = {
            "msgtype": "m.image",
            "body": caption or image_path.name,
            "url": response.content_uri,
            "info": {"size": image_path.stat().st_size}
        }
        
        await self.client.room_send(room_id, "m.room.message", content)
        
    async def join_room(self, room_id: str) -> None:
        """
        Join a room.
        
        Args:
            room_id: Room ID to join
        """
        await self.client.join(room_id)
        
    async def leave_room(self, room_id: str) -> None:
        """
        Leave a room.
        
        Args:
            room_id: Room ID to leave
        """
        await self.client.room_leave(room_id)
        
    async def get_rooms(self) -> List[Room]:
        """
        Get list of joined rooms.
        
        Returns:
            List of Room objects
        """
        rooms = []
        for room_id, room in self.client.rooms.items():
            rooms.append(create_room_object(room))
        return rooms
        
    def _load_sync_token(self) -> None:
        """Load the sync token from file to resume from last position."""
        if self._sync_token_file.exists():
            try:
                with open(self._sync_token_file, 'r') as f:
                    data = json.load(f)
                    self._next_batch = data.get('next_batch')
            except (json.JSONDecodeError, KeyError):
                pass
                
    def _save_sync_token(self, token: str) -> None:
        """Save the sync token to file."""
        with open(self._sync_token_file, 'w') as f:
            json.dump({'next_batch': token}, f)
            
    async def _sync_forever(self) -> None:
        """Continuously sync with the homeserver."""
        while True:
            try:
                response = await self.client.sync(since=self._next_batch, timeout=30000)
                if isinstance(response, SyncResponse):
                    self._next_batch = response.next_batch
                    self._save_sync_token(self._next_batch)
            except Exception as e:
                print(f"Sync error: {e}")
                await asyncio.sleep(5)
                
    async def _handle_message(self, room: MatrixRoom, event: RoomMessageText) -> None:
        """Handle incoming message events."""
        if event.sender == self.user_id:
            return
            
        message = create_message_object(room, event, self.client)
        
        if message.text.startswith(self.command_prefix):
            command = parse_command(message, self.command_prefix)
            if command:
                await self._event_handler.trigger_command(command.name, command)
        else:
            await self._event_handler.trigger_message(message)
            
    async def _handle_invite(self, room: MatrixRoom, event: InviteEvent) -> None:
        """Handle room invite events."""
        await self._event_handler.trigger_invite(room, event)
        
    async def _handle_member_event(self, room: MatrixRoom, event: RoomMemberEvent) -> None:
        """Handle room member events."""
        if event.membership == "join":
            await self._event_handler.trigger_member_join(room, event)
        elif event.membership == "leave":
            await self._event_handler.trigger_member_leave(room, event)