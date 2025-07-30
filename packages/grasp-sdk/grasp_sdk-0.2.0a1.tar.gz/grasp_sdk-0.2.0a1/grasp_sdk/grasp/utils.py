"""Utility functions for Grasp SDK."""

import os
import asyncio
import signal
from typing import Dict, Optional, List
import warnings

from ..utils.logger import get_logger
from .server import GraspServer
from .session import GraspSession

# Global server registry
_servers: Dict[str, GraspServer] = {}

async def _graceful_shutdown(reason: str = 'SIGTERM') -> None:
    """Gracefully shutdown all servers.
    
    Args:
        reason: Reason for shutdown
    """
    logger = get_logger().child('shutdown')
    logger.info(f'Graceful shutdown initiated: {reason}')
    
    if not _servers:
        logger.info('No active servers to shutdown')
        return
    
    logger.info(f'Shutting down {len(_servers)} active servers...')
    
    # Create cleanup tasks for all servers
    cleanup_tasks = []
    for server_id, server in _servers.items():
        logger.info(f'Scheduling cleanup for server {server_id}')
        cleanup_tasks.append(server.cleanup())
    
    # Wait for all cleanups to complete
    try:
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        logger.info('All servers cleaned up successfully')
    except Exception as error:
        logger.error(f'Error during cleanup: {error}')
    
    # Clear the servers registry
    _servers.clear()
    logger.info('Graceful shutdown completed')


def _setup_signal_handlers() -> None:
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        signal_name = signal.Signals(signum).name
        asyncio.create_task(_graceful_shutdown(signal_name))
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


async def shutdown(connection: Optional[str] = None) -> None:
    """Shutdown Grasp servers (deprecated).
    
    Args:
        connection: Optional connection ID to shutdown specific server
        
    Deprecated:
        This function is deprecated. Use server.cleanup() or context managers instead.
    """
    warnings.warn(
        "shutdown() is deprecated. Use server.cleanup() or context managers instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    logger = get_logger().child('shutdown')
    
    if connection:
        # Shutdown specific connection
        if connection in _servers:
            logger.info(f'Shutting down server {connection}')
            await _servers[connection].cleanup()
        else:
            logger.warn(f'Server {connection} not found')
    else:
        # Shutdown all servers
        await _graceful_shutdown('USER_SHUTDOWN')


# Setup signal handlers when module is imported
_setup_signal_handlers()