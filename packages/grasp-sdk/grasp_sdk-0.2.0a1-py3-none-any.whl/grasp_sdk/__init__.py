"""Grasp Server Python SDK

A Python SDK for Grasp platform providing secure command execution 
and browser automation in isolated cloud environments.
"""

import asyncio
import signal
from typing import Dict, Optional, Any
import warnings

# Import utilities
from .utils.logger import get_logger

# Import all classes from grasp module
from .grasp import (
    GraspServer,
    GraspBrowser,
    GraspTerminal,
    GraspSession,
    Grasp,
    _servers,
    shutdown,
)

# Import CDPConnection for type annotation
from .services.browser import CDPConnection

__version__ = "0.2.0a1"
__author__ = "Grasp Team"
__email__ = "team@grasp.dev"

# Global server registry (re-exported from grasp module)
_servers: Dict[str, GraspServer] = _servers

# Deprecated functions for backward compatibility
async def launch_browser(
    options: Optional[Dict[str, Any]] = None
) -> CDPConnection:
    """Launch a browser instance.
    
    .. deprecated::
        Use grasp.launch() instead. This method will be removed in a future version.
    
    Args:
        options: Launch options including type, headless, adblock settings
        
    Returns:
        Dictionary containing connection information
    """
    import warnings
    warnings.warn(
        "launch_browser() is deprecated. Use grasp.launch() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # Create server instance
    server = GraspServer(options)

    connection = await server.create_browser_task()

    return connection


async def _graceful_shutdown(reason: str = 'SIGTERM') -> None:
    """Gracefully shutdown all servers.
    
    Args:
        reason: Reason for shutdown
    """
    import os
    logger = get_logger().child('shutdown')
    logger.info(f'Graceful shutdown initiated: {reason}')
    
    if not _servers:
        logger.info('No active servers to shutdown')
        # 强制终止进程
        os._exit(0)
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
    
    # 强制终止进程，确保不会被其他异步任务阻塞
    os._exit(0)


def _setup_signal_handlers() -> None:
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signame):
        logger = get_logger().child('signal')
        logger.info(f'Received signal {signame}, initiating graceful shutdown...')
        
        # 创建关闭任务
        asyncio.create_task(_graceful_shutdown(signame))
    
    # 尝试使用 asyncio 的信号处理器（更适合异步环境）
    try:
        loop = asyncio.get_running_loop()
        for sig in [signal.SIGTERM, signal.SIGINT]:
            loop.add_signal_handler(sig, lambda s=sig: signal_handler(signal.Signals(s).name))
    except RuntimeError:
        # 如果没有运行的事件循环，使用传统方式
        def fallback_handler(signum, frame):
            signal_name = signal.Signals(signum).name
            logger = get_logger().child('signal')
            logger.info(f'Received {signal_name}, but no event loop is running')
            import os
            os._exit(1)
            
        signal.signal(signal.SIGTERM, fallback_handler)
        signal.signal(signal.SIGINT, fallback_handler)


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

# Export all public APIs
__all__ = [
    'GraspServer',
    'Grasp',
    'GraspSession',
    'GraspBrowser',
    'GraspTerminal',
    'launch_browser',
    'shutdown',
]

# Default export equivalent
default = {
    'GraspServer': GraspServer,
    'Grasp': Grasp,
    'GraspSession': GraspSession,
    'GraspBrowser': GraspBrowser,
    'GraspTerminal': GraspTerminal,
    'launch_browser': launch_browser,
    'shutdown': shutdown,
}