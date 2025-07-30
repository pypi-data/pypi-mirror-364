"""GraspSession class for session management."""

import asyncio
import websockets
from .browser import GraspBrowser
from .terminal import GraspTerminal
from ..services.browser import CDPConnection
from ..services.filesystem import FileSystemService


class GraspSession:
    """Main session interface providing access to browser, terminal, and files."""
    
    def __init__(self, connection: CDPConnection):
        """Initialize GraspSession.
        
        Args:
            connection: CDP connection instance
        """
        self.connection = connection
        self.browser = GraspBrowser(connection)
        self.terminal = GraspTerminal(connection)
        
        # Create files service
        connection_id = connection.id
        try:
            from . import _servers
            server = _servers[connection_id]
            if server.sandbox is None:
                raise RuntimeError('Sandbox is not available for file system service')
            self.files = FileSystemService(server.sandbox, connection)
        except (ImportError, KeyError) as e:
            # In test environment or when server is not available, create a mock files service
            print(f"Warning: Files service not available: {e}")
            raise e
        
        # WebSocket connection for keep-alive
        self._ws = None
        self._keep_alive_task = None
        
        # Initialize WebSocket connection and start keep-alive
        print('create session...')
        asyncio.create_task(self._initialize_websocket())
    
    async def _initialize_websocket(self) -> None:
        """Initialize WebSocket connection and start keep-alive."""
        try:
            self._ws = await websockets.connect(self.connection.ws_url)
            await self._keep_alive()
        except Exception as e:
            print(f"Failed to initialize WebSocket connection: {e}")
    
    async def _keep_alive(self) -> None:
        """Keep WebSocket connection alive with periodic ping."""
        if self._ws is None:
            return
            
        async def ping_loop():
            while self._ws and self._ws.close_code is None:
                try:
                    await self._ws.ping()
                    await asyncio.sleep(10)  # 10 seconds interval, same as TypeScript version
                except Exception as e:
                    print(f"Keep-alive ping failed: {e}")
                    break
        
        self._keep_alive_task = asyncio.create_task(ping_loop())
    
    @property
    def id(self) -> str:
        """Get session ID.
        
        Returns:
            Session ID
        """
        return self.connection.id
    
    async def close(self) -> None:
        """Close the session and cleanup resources."""
        # Stop keep-alive task
        if self._keep_alive_task:
            self._keep_alive_task.cancel()
            try:
                await self._keep_alive_task
            except asyncio.CancelledError:
                pass
        
        # Close WebSocket connection with timeout
        if self._ws and self._ws.close_code is None:
            try:
                # Add timeout to prevent hanging on close
                await asyncio.wait_for(self._ws.close(), timeout=5.0)
                print('✅ WebSocket closed successfully')
            except asyncio.TimeoutError:
                print('⚠️ WebSocket close timeout, forcing termination')
                # Force close if timeout
                if hasattr(self._ws, 'transport') and self._ws.transport:
                    self._ws.transport.close()
            except Exception as e:
                print(f"Failed to close WebSocket connection: {e}")
        
        # Cleanup server resources
        try:
            from . import _servers
            await _servers[self.id].cleanup()
        except (ImportError, KeyError) as e:
            # In test environment or when server is not available, skip cleanup
            print(f"Warning: Server cleanup not available: {e}")