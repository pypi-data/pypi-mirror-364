"""
TuskPHP Tantor - The Real-Time Messenger (Python Edition)
========================================================

🐘 BACKSTORY: Tantor - Tarzan's Anxious but Loyal Friend
-------------------------------------------------------
In Disney's Tarzan, Tantor is a big-hearted elephant with anxiety issues
who becomes one of Tarzan's closest friends. Despite being afraid of
everything (especially piranhas), Tantor always comes through when it
matters. He's known for his excellent hearing, ability to trumpet warnings
across the jungle, and his unwavering loyalty to his friends.

WHY THIS NAME: Like Tantor who could hear danger from afar and trumpet
messages across the jungle, this WebSocket messenger provides real-time
communication across your application. Tantor may have been nervous, but
he never failed to deliver important messages. This system ensures that
notifications, chats, and live updates reach their destination instantly,
with the same reliability Tarzan could count on from his elephant friend.

"He's not just any elephant - he's Tantor, and he delivers messages!"

FEATURES:
- WebSocket server and client management
- Real-time bidirectional communication
- Channel-based messaging (public/private)
- Presence tracking (who's online)
- Message history and persistence
- Automatic reconnection handling
- Event broadcasting system
- Heartbeat monitoring
- Emergency alert system

@package TuskPHP\Elephants
@author  TuskPHP Team
@since   1.0.0
"""

import json
import time
import uuid
import threading
import asyncio
import websockets
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import sqlite3
import logging

# Optional imports for enhanced features
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

# Flask-TSK imports
try:
    from tsk_flask.database import TuskDb
    from tsk_flask.memory import Memory
    from tsk_flask.herd import Herd
    from tsk_flask.utils import PermissionHelper
except ImportError:
    # Fallback for standalone usage
    TuskDb = None
    Memory = None
    Herd = None
    PermissionHelper = None


class MessageType(Enum):
    """Message type enumeration"""
    CHAT = "chat"
    SYSTEM = "system"
    EMERGENCY = "emergency"
    PRESENCE = "presence"
    HEARTBEAT = "heartbeat"


class ChannelType(Enum):
    """Channel type enumeration"""
    PUBLIC = "public"
    PRIVATE = "private"
    EMERGENCY = "emergency"


@dataclass
class Message:
    """Message data structure"""
    id: str
    channel: str
    message: str
    sender: str
    timestamp: float
    message_type: str = MessageType.CHAT.value
    data: Dict = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


@dataclass
class Connection:
    """Connection data structure"""
    client_id: str
    websocket: Any
    handshake_complete: bool
    last_ping: float
    joined_at: float
    channels: List[str] = None
    user_data: Dict = None

    def __post_init__(self):
        if self.channels is None:
            self.channels = []
        if self.user_data is None:
            self.user_data = {}


@dataclass
class Channel:
    """Channel data structure"""
    name: str
    type: str
    subscribers: List[str] = None
    created_at: float = None
    settings: Dict = None

    def __post_init__(self):
        if self.subscribers is None:
            self.subscribers = []
        if self.created_at is None:
            self.created_at = time.time()
        if self.settings is None:
            self.settings = {}


class Tantor:
    """
    Tantor - The Real-Time Messenger
    
    Tantor provides real-time WebSocket communication with the same reliability
    and loyalty that Tarzan could count on from his elephant friend. Despite
    being nervous, Tantor never fails to deliver important messages.
    """
    
    def __init__(self, port: int = 8080, host: str = "0.0.0.0"):
        """Initialize Tantor - The messenger prepares to listen"""
        self.port = port
        self.host = host
        self.connections: Dict[str, Connection] = {}
        self.channels: Dict[str, Channel] = {}
        self.message_queue: List[Dict] = []
        self.is_running = False
        self.server = None
        
        # Initialize default channels
        self.channels = {
            'jungle': Channel('jungle', ChannelType.PUBLIC.value),
            'treehouse': Channel('treehouse', ChannelType.PRIVATE.value),
            'emergency': Channel('emergency', ChannelType.EMERGENCY.value)
        }
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Statistics
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'connections_total': 0,
            'start_time': time.time()
        }
        
        print(f"🐘 Tantor is preparing to listen on {host}:{port}...")
        print("Despite his nervousness, he won't miss a message!")
    
    async def start(self):
        """Start the WebSocket server - Tantor begins listening"""
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets library is required. Install with: pip install websockets")
        
        self.is_running = True
        
        print(f"🐘 Tantor is listening on {self.host}:{self.port}...")
        print("Despite his nervousness, he won't miss a message!\n")
        
        # Start WebSocket server
        async with websockets.serve(self._handle_client, self.host, self.port):
            print(f"🎯 Tantor's server created on port {self.port}")
            
            # Start background tasks
            asyncio.create_task(self._process_message_queue())
            asyncio.create_task(self._check_heartbeats())
            
            # Keep server running
            await asyncio.Future()  # Run forever
    
    async def _handle_client(self, websocket, path):
        """Handle new client connection"""
        client_id = f"client_{uuid.uuid4().hex[:8]}"
        
        # Create connection
        connection = Connection(
            client_id=client_id,
            websocket=websocket,
            handshake_complete=True,  # websockets library handles handshake
            last_ping=time.time(),
            joined_at=time.time()
        )
        
        self.connections[client_id] = connection
        self.stats['connections_total'] += 1
        
        print(f"👋 New friend joined Tantor's jungle: {client_id}")
        
        # Auto-subscribe to jungle channel
        await self.subscribe(client_id, 'jungle')
        
        # Send welcome message
        await self.send(client_id, {
            'event': 'welcome',
            'message': 'Welcome to Tantor\'s jungle! 🐘',
            'client_id': client_id
        }, 'system')
        
        try:
            # Handle client messages
            async for message in websocket:
                await self._handle_client_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            print(f"💔 Tantor lost contact with {client_id}")
        except Exception as e:
            print(f"❌ Error handling client {client_id}: {e}")
        finally:
            # Clean up connection
            await self._handle_disconnect(client_id)
    
    async def _handle_client_message(self, client_id: str, message: str):
        """Handle incoming client messages - Tantor processes jungle chatter"""
        try:
            decoded = json.loads(message)
        except json.JSONDecodeError:
            print(f"🤔 Tantor doesn't understand: {message}")
            return
        
        action = decoded.get('action', 'chat')
        
        if action == 'join_channel':
            channel = decoded.get('channel', 'jungle')
            await self.subscribe(client_id, channel)
            
        elif action == 'leave_channel':
            channel = decoded.get('channel', 'jungle')
            await self.unsubscribe(client_id, channel)
            
        elif action == 'broadcast':
            channel = decoded.get('channel', 'jungle')
            event = decoded.get('event', 'message')
            data = decoded.get('data', {})
            await self.broadcast(channel, event, data)
            
        elif action == 'ping':
            self.connections[client_id].last_ping = time.time()
            await self.send(client_id, {'pong': True}, 'system')
            
        else:
            print(f"🐘 Tantor heard: {message} from {client_id}")
            self.stats['messages_received'] += 1
    
    async def send(self, client_id: str, message: Union[str, Dict], channel: str = 'jungle') -> str:
        """
        Send message - Tantor trumpets across the jungle
        
        Args:
            client_id: Target client identifier
            message: Message content (string or dict)
            channel: Channel name
            
        Returns:
            Message ID
        """
        if client_id not in self.connections:
            # Tantor is worried - where did the friend go?
            raise Exception(f"Oh no! I can't find that client! *nervous trumpet*")
        
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        
        if isinstance(message, str):
            payload = {
                'id': message_id,
                'channel': channel,
                'message': message,
                'timestamp': time.time(),
                'sender': 'tantor'
            }
        else:
            payload = {
                'id': message_id,
                'channel': channel,
                'timestamp': time.time(),
                'sender': 'tantor',
                **message
            }
        
        # Queue message for delivery
        self.message_queue.append({
            'to': client_id,
            'payload': payload
        })
        
        # Tantor's reliability - persist important messages
        if Memory:
            Memory.remember(f"tantor_msg_{message_id}", payload, 3600)
        
        self.stats['messages_sent'] += 1
        return message_id
    
    async def broadcast(self, channel: str, event: str, data: Dict = None) -> int:
        """
        Broadcast to channel - Jungle-wide announcement
        
        Args:
            channel: Channel name
            event: Event type
            data: Event data
            
        Returns:
            Number of recipients
        """
        if channel not in self.channels:
            # Tantor creates new channels as needed
            self.channels[channel] = Channel(channel, ChannelType.PUBLIC.value)
        
        if data is None:
            data = {}
        
        message = {
            'event': event,
            'data': data,
            'channel': channel,
            'timestamp': time.time(),
            'trumpeted_by': 'tantor'
        }
        
        # Send to all subscribers in the channel
        recipients = 0
        for client_id in self.channels[channel].subscribers:
            if client_id in self.connections:
                try:
                    await self.send(client_id, message, channel)
                    recipients += 1
                except Exception as e:
                    print(f"⚠️ Failed to send to {client_id}: {e}")
        
        print(f"📢 Tantor broadcasts to {channel}: {event} ({recipients} recipients)")
        return recipients
    
    async def subscribe(self, client_id: str, channel: str) -> bool:
        """
        Subscribe client to channel - Join Tantor's friend circle
        
        Args:
            client_id: Client identifier
            channel: Channel name
            
        Returns:
            Success status
        """
        if channel not in self.channels:
            self.channels[channel] = Channel(channel, ChannelType.PUBLIC.value)
        
        if client_id not in self.channels[channel].subscribers:
            self.channels[channel].subscribers.append(client_id)
            
            # Add to connection's channel list
            if client_id in self.connections:
                self.connections[client_id].channels.append(channel)
            
            # Notify others - "New friend in the jungle!"
            await self.broadcast(channel, 'user_joined', {
                'client_id': client_id,
                'total_users': len(self.channels[channel].subscribers)
            })
        
        return True
    
    async def unsubscribe(self, client_id: str, channel: str) -> bool:
        """
        Unsubscribe from channel - Leave Tantor's friend group
        
        Args:
            client_id: Client identifier
            channel: Channel name
            
        Returns:
            Success status
        """
        if channel in self.channels and client_id in self.channels[channel].subscribers:
            self.channels[channel].subscribers.remove(client_id)
            
            # Remove from connection's channel list
            if client_id in self.connections:
                if channel in self.connections[client_id].channels:
                    self.connections[client_id].channels.remove(channel)
            
            # Notify others
            await self.broadcast(channel, 'user_left', {
                'client_id': client_id,
                'total_users': len(self.channels[channel].subscribers)
            })
        
        return True
    
    def get_presence(self, channel: str = None) -> Dict:
        """
        Handle presence - Who's in the jungle with Tantor?
        
        Args:
            channel: Specific channel (optional)
            
        Returns:
            Presence information
        """
        if channel:
            if channel not in self.channels:
                return {
                    'channel': channel,
                    'online': 0,
                    'users': []
                }
            
            return {
                'channel': channel,
                'online': len(self.channels[channel].subscribers),
                'users': self.channels[channel].subscribers
            }
        
        # Tantor's full jungle census
        presence = {}
        for ch_name, ch in self.channels.items():
            presence[ch_name] = len(ch.subscribers)
        
        return presence
    
    async def emergency(self, message: str) -> int:
        """
        Emergency alert - Tantor's loudest trumpet!
        
        Args:
            message: Emergency message
            
        Returns:
            Number of recipients
        """
        # When Tantor panics, EVERYONE hears about it
        print(f"🚨 TANTOR'S EMERGENCY TRUMPET: {message}")
        
        # Broadcast to all channels
        total_recipients = 0
        for channel_name in self.channels:
            recipients = await self.broadcast(channel_name, 'emergency_alert', {
                'message': message,
                'severity': 'critical',
                'source': 'tantor_emergency_system'
            })
            total_recipients += recipients
        
        # Log for posterity - even anxious elephants keep records
        if Memory:
            Memory.remember(f'tantor_emergency_{int(time.time())}', {
                'message': message,
                'timestamp': time.time(),
                'recipients': total_recipients
            }, 86400)
        
        return total_recipients
    
    async def _handle_disconnect(self, client_id: str):
        """Handle disconnection - When friends leave the jungle"""
        if client_id not in self.connections:
            return
        
        # Remove from all channels - Tantor is sad to see them go
        for channel_name, channel in self.channels.items():
            if client_id in channel.subscribers:
                channel.subscribers.remove(client_id)
                
                # Notify others
                if channel.subscribers:
                    await self.broadcast(channel_name, 'user_left', {
                        'client_id': client_id
                    })
        
        # Remove connection
        del self.connections[client_id]
        print(f"👋 Friend left Tantor's jungle: {client_id}")
    
    async def _process_message_queue(self):
        """Process message queue - Tantor delivers all his messages"""
        while self.is_running:
            if self.message_queue:
                queued_message = self.message_queue.pop(0)
                client_id = queued_message['to']
                payload = queued_message['payload']
                
                if client_id in self.connections:
                    await self._deliver_message(client_id, payload)
                else:
                    print(f"⚠️ Tantor lost a friend: {client_id} - message dropped")
            
            await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
    
    async def _deliver_message(self, client_id: str, payload: Dict):
        """Deliver message to specific client - Tantor's careful delivery"""
        if client_id not in self.connections:
            return
        
        connection = self.connections[client_id]
        
        try:
            await connection.websocket.send(json.dumps(payload))
            print(f"📨 Tantor delivered message to {client_id}")
        except Exception as e:
            print(f"💔 Tantor couldn't deliver to {client_id} - connection lost: {e}")
            await self._handle_disconnect(client_id)
    
    async def _check_heartbeats(self):
        """Check heartbeats - Tantor's wellness checks"""
        while self.is_running:
            current_time = time.time()
            timeout = 30  # 30 seconds
            
            # Check for stale connections
            disconnected_clients = []
            for client_id, connection in self.connections.items():
                if (current_time - connection.last_ping) > timeout:
                    print(f"💔 Tantor lost contact with {client_id} - removing")
                    disconnected_clients.append(client_id)
            
            # Remove disconnected clients
            for client_id in disconnected_clients:
                await self._handle_disconnect(client_id)
            
            # Send ping to all connected clients every 10 seconds
            if int(current_time) % 10 == 0:
                for client_id, connection in self.connections.items():
                    try:
                        await self.send(client_id, {'ping': True}, 'system')
                    except Exception as e:
                        print(f"⚠️ Failed to ping {client_id}: {e}")
            
            await asyncio.sleep(1)  # Check every second
    
    def stats(self) -> Dict:
        """Get statistics - Tantor's nervous monitoring"""
        return {
            'total_connections': len(self.connections),
            'channels': {name: len(ch.subscribers) for name, ch in self.channels.items()},
            'queued_messages': len(self.message_queue),
            'uptime': time.time() - self.stats['start_time'],
            'status': 'listening' if self.is_running else 'sleeping',
            'mood': 'anxious' if len(self.connections) > 10 else 'calm',
            'messages_sent': self.stats['messages_sent'],
            'messages_received': self.stats['messages_received'],
            'connections_total': self.stats['connections_total']
        }
    
    def get_client_info(self, client_id: str) -> Optional[Dict]:
        """
        Get client info - Tantor remembers his friends
        
        Args:
            client_id: Client identifier
            
        Returns:
            Client information or None
        """
        if client_id not in self.connections:
            return None
        
        connection = self.connections[client_id]
        
        return {
            'client_id': client_id,
            'connected_at': connection.joined_at,
            'last_ping': connection.last_ping,
            'channels': connection.channels.copy(),
            'uptime': time.time() - connection.joined_at,
            'user_data': connection.user_data.copy()
        }
    
    async def stop(self):
        """Stop the server - Tantor needs a rest"""
        self.is_running = False
        
        # Notify all clients
        for client_id in list(self.connections.keys()):
            try:
                await self.send(client_id, {
                    'event': 'server_shutdown',
                    'message': 'Tantor is going to sleep. Goodbye! 🐘💤'
                }, 'system')
            except Exception:
                pass  # Client might already be disconnected
        
        print("💤 Tantor is going to sleep...")
    
    def on_event(self, event: str, handler: Callable):
        """
        Register event handler
        
        Args:
            event: Event name
            handler: Event handler function
        """
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        
        self.event_handlers[event].append(handler)
    
    async def _trigger_event(self, event: str, data: Dict):
        """Trigger event handlers"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    print(f"❌ Event handler error for {event}: {e}")
    
    def create_test_client_html(self, port: int = 8080) -> str:
        """
        Create a simple WebSocket client for testing - Tantor's practice buddy
        
        Args:
            port: Server port
            
        Returns:
            Path to test client HTML file
        """
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>🐘 Tantor WebSocket Test Client</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f0f8ff; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .messages {{ border: 1px solid #ddd; height: 300px; overflow-y: auto; padding: 10px; background: white; margin: 10px 0; }}
        .controls {{ margin: 10px 0; }}
        input, button {{ padding: 8px; margin: 5px; }}
        .elephant {{ font-size: 2em; text-align: center; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="elephant">🐘 Tantor's Jungle Chat</div>
        
        <div class="controls">
            <button onclick="connect()">Connect to Tantor</button>
            <button onclick="disconnect()">Disconnect</button>
            <span id="status">Disconnected</span>
        </div>
        
        <div class="controls">
            <input type="text" id="messageInput" placeholder="Type your message..." onkeypress="if(event.key==='Enter')sendMessage()">
            <button onclick="sendMessage()">Send Message</button>
        </div>
        
        <div class="controls">
            <select id="channelSelect">
                <option value="jungle">🌿 Jungle (Public)</option>
                <option value="treehouse">🏠 Treehouse (Private)</option>
                <option value="emergency">🚨 Emergency</option>
            </select>
            <button onclick="joinChannel()">Join Channel</button>
        </div>
        
        <div id="messages" class="messages">
            <div><em>🐘 Tantor is waiting for you to connect...</em></div>
        </div>
    </div>

    <script>
        let ws = null;
        let clientId = null;
        
        function connect() {{
            ws = new WebSocket('ws://localhost:{port}');
            
            ws.onopen = function() {{
                document.getElementById('status').textContent = 'Connected to Tantor! 🐘';
                addMessage('🎉 Connected to Tantor\\'s jungle!');
            }};
            
            ws.onmessage = function(event) {{
                const data = JSON.parse(event.data);
                if (data.client_id) clientId = data.client_id;
                addMessage('📨 ' + JSON.stringify(data, null, 2));
            }};
            
            ws.onclose = function() {{
                document.getElementById('status').textContent = 'Disconnected';
                addMessage('👋 Disconnected from Tantor');
            }};
            
            ws.onerror = function(error) {{
                addMessage('❌ Error: ' + error);
            }};
        }}
        
        function disconnect() {{
            if (ws) {{
                ws.close();
                ws = null;
            }}
        }}
        
        function sendMessage() {{
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (message && ws && ws.readyState === WebSocket.OPEN) {{
                ws.send(JSON.stringify({{
                    action: 'broadcast',
                    channel: document.getElementById('channelSelect').value,
                    event: 'chat_message',
                    data: {{ message: message, from: clientId || 'unknown' }}
                }}));
                
                input.value = '';
                addMessage('📤 Sent: ' + message);
            }}
        }}
        
        function joinChannel() {{
            const channel = document.getElementById('channelSelect').value;
            
            if (ws && ws.readyState === WebSocket.OPEN) {{
                ws.send(JSON.stringify({{
                    action: 'join_channel',
                    channel: channel
                }}));
                
                addMessage('🚪 Joining channel: ' + channel);
            }}
        }}
        
        function addMessage(message) {{
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.innerHTML = '<small>' + new Date().toLocaleTimeString() + '</small> ' + message;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }}
    </script>
</body>
</html>"""
        
        file_path = Path('tantor-test-client.html')
        file_path.write_text(html_content)
        
        print(f"🧪 Test client created: {file_path}")
        print("📂 Open in browser to test Tantor's WebSocket server!")
        
        return str(file_path)


def init_tantor(app, port: int = 8080, host: str = "0.0.0.0"):
    """Initialize Tantor with Flask app"""
    tantor = Tantor(port, host)
    app.tantor = tantor
    return tantor


def get_tantor():
    """Get Tantor instance"""
    from flask import current_app
    return getattr(current_app, 'tantor', None)


# Async helper for running Tantor
async def run_tantor(port: int = 8080, host: str = "0.0.0.0"):
    """Run Tantor WebSocket server"""
    tantor = Tantor(port, host)
    await tantor.start()


def run_tantor_sync(port: int = 8080, host: str = "0.0.0.0"):
    """Run Tantor WebSocket server synchronously"""
    asyncio.run(run_tantor(port, host))


if __name__ == "__main__":
    # Create test client and run server
    tantor = Tantor(8080)
    tantor.create_test_client_html(8080)
    
    print("🚀 Starting Tantor WebSocket server...")
    print("📱 Test client available at: tantor-test-client.html")
    
    try:
        run_tantor_sync(8080)
    except KeyboardInterrupt:
        print("\n💤 Tantor stopped by user")
    except Exception as e:
        print(f"❌ Tantor error: {e}") 