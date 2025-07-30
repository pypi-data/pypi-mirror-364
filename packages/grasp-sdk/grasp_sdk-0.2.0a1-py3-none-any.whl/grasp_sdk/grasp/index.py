"""Main Grasp class for SDK initialization."""

import os
from typing import Dict, Optional, Any

from .server import GraspServer
from .session import GraspSession


class Grasp:
    """Main Grasp SDK class for creating and managing sessions."""
    
    def __init__(self, options: Optional[Dict[str, Any]] = None):
        """Initialize Grasp SDK.
        
        Args:
            options: Configuration options including apiKey
        """
        if options is None:
            options = {}
        
        self.key = options.get('apiKey', os.environ.get('GRASP_KEY', ''))
        self._session: Optional[GraspSession] = None
        self._launch_options: Optional[Dict[str, Any]] = None
    
    async def launch(self, options: Dict[str, Any]) -> GraspSession:
        """Launch a new browser session.
        
        Args:
            options: Launch options containing browser configuration
            
        Returns:
            GraspSession instance
        """
        browser_options = options.get('browser', {})
        browser_options['key'] = self.key
        browser_options['keepAliveMS'] = options.get('keepAliveMS', 10000)
        browser_options['timeout'] = options.get('timeout', 900000)
        browser_options['debug'] = options.get('debug', False)
        browser_options['logLevel'] = options.get('logLevel', 'info')
        
        server = GraspServer(browser_options)
        cdp_connection = await server.create_browser_task()
        return GraspSession(cdp_connection)
    
    async def __aenter__(self) -> GraspSession:
        """异步上下文管理器入口，启动会话。
        
        Returns:
            GraspSession 实例
            
        Raises:
            RuntimeError: 如果已经有活跃的会话
        """
        if self._session is not None:
            raise RuntimeError('Session already active. Close existing session before creating a new one.')
        
        if self._launch_options is None:
            raise RuntimeError('No launch options provided. Use grasp.launch(options) as context manager.')
        
        self._session = await self.launch(self._launch_options)
        return self._session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """异步上下文管理器退出，清理会话。
        
        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常回溯
        """
        if self._session is not None:
            await self._session.close()
            self._session = None
        self._launch_options = None
    
    def launch_context(self, options: Dict[str, Any]) -> 'Grasp':
        """设置启动选项并返回自身，用于上下文管理器。
        
        Args:
            options: 启动选项
            
        Returns:
            自身实例，用于 async with 语法
            
        Example:
            async with grasp.launch_context({
                'browser': {
                    'type': 'chromium',
                    'headless': True,
                    'timeout': 30000
                }
            }) as session:
                # 使用 session
                pass
        """
        self._launch_options = options
        return self
    
    async def connect(self, session_id: str) -> GraspSession:
        """Connect to an existing session.
        
        Args:
            session_id: ID of the session to connect to
            
        Returns:
            GraspSession instance
        """
        # Check if server already exists
        from . import _servers
        server = _servers.get(session_id)
        cdp_connection = None
        
        if server:
            cdp_connection = server.browser_service.get_cdp_connection() if server.browser_service else None
        
        if not cdp_connection:
            # Create new server with no timeout for existing sessions
            server = GraspServer({'timeout': 0})
            cdp_connection = await server.connect_browser_task(session_id)
        
        return GraspSession(cdp_connection)