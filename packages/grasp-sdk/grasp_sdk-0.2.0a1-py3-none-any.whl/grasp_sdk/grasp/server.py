"""GraspServer class for browser automation."""

import os
from typing import Dict, Optional, Any

from ..utils.logger import init_logger, get_logger
from ..utils.config import get_config
from ..services.browser import BrowserService, CDPConnection
from ..services.sandbox import SandboxService
from ..models import (
    ISandboxConfig,
    IBrowserConfig,
    SandboxStatus,
)


class GraspServer:
    """Main Grasp E2B class for browser automation."""
    
    def __init__(self, sandbox_config: Optional[Dict[str, Any]] = None):
        """Initialize GraspServer with configuration.
        
        Args:
            sandbox_config: Optional sandbox configuration overrides
        """
        if sandbox_config is None:
            sandbox_config = {}
        
        # Extract browser-specific options
        browser_type = sandbox_config.pop('type', 'chromium')
        headless = sandbox_config.pop('headless', True)
        adblock = sandbox_config.pop('adblock', False)
        logLevel = sandbox_config.pop('logLevel', '')
        keepAliveMS = sandbox_config.pop('keepAliveMS', 0)

        # Set default log level
        if not logLevel:
            logLevel = 'debug' if sandbox_config.get('debug', False) else 'info'

        self.__browser_type = browser_type
        
        # Create browser task
        self.__browser_config = {
            'headless': headless,
            'envs': {
                'ADBLOCK': 'true' if adblock else 'false',
                'KEEP_ALIVE_MS': str(keepAliveMS),
            }
        }
            
        config = get_config()
        config['sandbox'].update(sandbox_config)
        self.config = config

        logger = config['logger']
        logger['level'] = logLevel
        
        # Initialize logger first
        init_logger(logger)
        self.logger = get_logger().child('GraspServer')
        
        self.browser_service: Optional[BrowserService] = None
        
        self.logger.info('GraspServer initialized')
    
    async def __aenter__(self):
        connection = await self.create_browser_task()
    
        # Register server
        # if connection['id']:
        #    _servers[connection['id']] = self
            
        return connection
    
    async def __aexit__(self, exc_type, exc, tb):
        if self.browser_service and self.browser_service.id:
            service_id = self.browser_service.id
            self.logger.info(f'Closing browser service {service_id}')
            from . import _servers
            await _servers[service_id].cleanup()
    
    @property
    def sandbox(self) -> Optional[SandboxService]:
        """Get the underlying sandbox service.
        
        Returns:
            SandboxService instance or None
        """
        return self.browser_service.get_sandbox() if self.browser_service else None
    
    def get_status(self) -> Optional[SandboxStatus]:
        """Get current sandbox status.
        
        Returns:
            Sandbox status or None
        """
        return self.sandbox.get_status() if self.sandbox else None
    
    def get_sandbox_id(self) -> Optional[str]:
        """Get sandbox ID.
        
        Returns:
            Sandbox ID or None
        """
        return self.sandbox.get_sandbox_id() if self.sandbox else None
    
    async def create_browser_task(
        self, 
    ) -> CDPConnection:
        """Create and launch a browser task.
        
        Args:
            browser_type: Type of browser to launch
            config: Browser configuration overrides
            
        Returns:
            Dictionary containing browser connection info
            
        Raises:
            RuntimeError: If browser service is already initialized
        """
        if self.browser_service:
            raise RuntimeError('Browser service can only be initialized once')
        
        config = self.__browser_config
        browser_type = self.__browser_type

        if config is None:
            config = {}
            
        # Create base browser config
        browser_config: IBrowserConfig = {
            'headless': True,
            'launchTimeout': 30000,
            'args': [
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
            ],
            'envs': {},
        }
        
        # Apply user config overrides with type safety
        if 'headless' in config:
            browser_config['headless'] = config['headless']
        if 'launchTimeout' in config:
            browser_config['launchTimeout'] = config['launchTimeout']
        if 'args' in config:
            browser_config['args'] = config['args']
        if 'envs' in config:
            browser_config['envs'] = config['envs']
        
        self.browser_service = BrowserService(
            self.config['sandbox'],
            browser_config
        )
        await self.browser_service.initialize(browser_type)

        # Register server
        from . import _servers
        _servers[str(self.browser_service.id)] = self
        self.logger.info("🚀 Browser service initialized", {
            'id': self.browser_service.id,
        })
        
        self.logger.info('🌐 Launching Chromium browser with CDP...')
        cdp_connection = await self.browser_service.launch_browser()
        
        self.logger.info('✅ Browser launched successfully!')
        self.logger.debug(
            f'CDP Connection Info (wsUrl: {cdp_connection.ws_url}, httpUrl: {cdp_connection.http_url})'
        )
        
        return cdp_connection
    
    async def connect_browser_task(self, session_id: str) -> CDPConnection:
        """Connect to an existing browser session.
        
        Args:
            session_id: ID of the session to connect to
            
        Returns:
            CDPConnection instance for the existing session
            
        Raises:
            RuntimeError: If browser service is already initialized
        """
        if self.browser_service:
            raise RuntimeError('Browser service can only be initialized once')
        
        config = self.__browser_config
        browser_type = self.__browser_type
        
        if config is None:
            config = {}
        
        # Create base browser config
        browser_config: IBrowserConfig = {
            'headless': True,
            'launchTimeout': 30000,
            'args': [
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
            ],
            'envs': {},
        }
        
        # Apply user config overrides with type safety
        if 'headless' in config:
            browser_config['headless'] = config['headless']
        if 'launchTimeout' in config:
            browser_config['launchTimeout'] = config['launchTimeout']
        if 'args' in config:
            browser_config['args'] = config['args']
        if 'envs' in config:
            browser_config['envs'] = config['envs']
        
        self.browser_service = BrowserService(
            self.config['sandbox'],
            browser_config
        )
        
        # Connect to existing session
        connection = await self.browser_service.connect(session_id)
        
        # Register server
        from . import _servers
        _servers[connection.id] = self
        
        return connection
    
    async def cleanup(self) -> None:
        """Cleanup resources.
        
        Returns:
            Promise that resolves when cleanup is complete
        """
        self.logger.info('Starting cleanup process')
        
        try:
            if self.browser_service:
                id = self.browser_service.id
                await self.browser_service.cleanup()
                if id:
                    from . import _servers
                    del _servers[id]
                
            self.logger.info('Cleanup completed successfully')
        except Exception as error:
            self.logger.error(f'Cleanup failed: {error}')
            raise