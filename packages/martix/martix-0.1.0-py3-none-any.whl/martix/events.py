"""
Event handling system for Martix library.
"""

from typing import Callable, Dict, Any, Optional, List
import asyncio

from .types import Message, Command


class EventHandler:
    """
    Manages event handlers and dispatching for the Martix client.
    
    This class provides a decorator-based system for registering
    event handlers and manages their execution.
    """
    
    def __init__(self):
        """Initialize the event handler system."""
        self._ready_handlers: List[Callable] = []
        self._message_handlers: List[Callable] = []
        self._command_handlers: Dict[str, List[Callable]] = {}
        self._invite_handlers: List[Callable] = []
        self._member_join_handlers: List[Callable] = []
        self._member_leave_handlers: List[Callable] = []
        
    def on_ready(self, func: Callable) -> Callable:
        """
        Register a ready event handler.
        
        Args:
            func: Handler function
            
        Returns:
            The original function
        """
        self._ready_handlers.append(func)
        return func
        
    def on_message(self, func: Callable) -> Callable:
        """
        Register a message event handler.
        
        Args:
            func: Handler function that takes a Message parameter
            
        Returns:
            The original function
        """
        self._message_handlers.append(func)
        return func
        
    def on_command(self, command_name: str) -> Callable:
        """
        Register a command event handler.
        
        Args:
            command_name: Name of the command to handle
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            if command_name not in self._command_handlers:
                self._command_handlers[command_name] = []
            self._command_handlers[command_name].append(func)
            return func
        return decorator
        
    def on_invite(self, func: Callable) -> Callable:
        """
        Register an invite event handler.
        
        Args:
            func: Handler function
            
        Returns:
            The original function
        """
        self._invite_handlers.append(func)
        return func
        
    def on_member_join(self, func: Callable) -> Callable:
        """
        Register a member join event handler.
        
        Args:
            func: Handler function
            
        Returns:
            The original function
        """
        self._member_join_handlers.append(func)
        return func
        
    def on_member_leave(self, func: Callable) -> Callable:
        """
        Register a member leave event handler.
        
        Args:
            func: Handler function
            
        Returns:
            The original function
        """
        self._member_leave_handlers.append(func)
        return func
        
    async def trigger_ready(self) -> None:
        """Trigger all ready event handlers."""
        for handler in self._ready_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                print(f"Error in ready handler: {e}")
                
    async def trigger_message(self, message: Message) -> None:
        """
        Trigger all message event handlers.
        
        Args:
            message: Message object
        """
        for handler in self._message_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                print(f"Error in message handler: {e}")
                
    async def trigger_command(self, command_name: str, command: Command) -> None:
        """
        Trigger command event handlers for a specific command.
        
        Args:
            command_name: Name of the command
            command: Command object
        """
        if command_name in self._command_handlers:
            for handler in self._command_handlers[command_name]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(command)
                    else:
                        handler(command)
                except Exception as e:
                    print(f"Error in command handler for '{command_name}': {e}")
                    
    async def trigger_invite(self, room: Any, event: Any) -> None:
        """
        Trigger all invite event handlers.
        
        Args:
            room: Matrix room object
            event: Invite event
        """
        for handler in self._invite_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(room, event)
                else:
                    handler(room, event)
            except Exception as e:
                print(f"Error in invite handler: {e}")
                
    async def trigger_member_join(self, room: Any, event: Any) -> None:
        """
        Trigger all member join event handlers.
        
        Args:
            room: Matrix room object
            event: Member event
        """
        for handler in self._member_join_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(room, event)
                else:
                    handler(room, event)
            except Exception as e:
                print(f"Error in member join handler: {e}")
                
    async def trigger_member_leave(self, room: Any, event: Any) -> None:
        """
        Trigger all member leave event handlers.
        
        Args:
            room: Matrix room object
            event: Member event
        """
        for handler in self._member_leave_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(room, event)
                else:
                    handler(room, event)
            except Exception as e:
                print(f"Error in member leave handler: {e}")