"""GraspTerminal class for terminal interface."""

from ..services.browser import CDPConnection
from ..services.terminal import TerminalService


class GraspTerminal:
    """Terminal interface for Grasp session."""
    
    def __init__(self, connection: CDPConnection):
        """Initialize GraspTerminal.
        
        Args:
            connection: CDP connection instance
        """
        self.connection = connection
    
    def create(self) -> TerminalService:
        """Create a new terminal service instance.
        
        Returns:
            TerminalService instance
            
        Raises:
            RuntimeError: If sandbox is not available
        """
        connection_id = self.connection.id
        from . import _servers
        server = _servers[connection_id]
        if server.sandbox is None:
            raise RuntimeError('Sandbox is not available')
        return TerminalService(server.sandbox, self.connection)