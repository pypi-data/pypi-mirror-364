#!/usr/bin/env python3
"""
Filesystem service for managing file operations in sandbox.

This module provides Python implementation of the filesystem service,
equivalent to the TypeScript version in src/services/filesystem.service.ts
"""

import asyncio
from typing import Optional, Dict, Union
from ..utils.logger import get_logger, Logger
from .sandbox import SandboxService
from .browser import CDPConnection


class FileSystemService:
    """
    Filesystem service for managing file operations in sandbox.
    """
    
    def __init__(self, sandbox: SandboxService, connection: CDPConnection):
        """Initialize filesystem service.
        
        Args:
            sandbox: The sandbox service instance
            connection: The CDP connection for browser integration
        """
        self.sandbox = sandbox
        self.connection = connection
        self.logger = self._get_default_logger()
    
    def _get_default_logger(self) -> Logger:
        """Gets or creates a default logger instance.
        
        Returns:
            Logger instance
        """
        try:
            return get_logger().child('FileSystemService')
        except Exception:
            # If logger is not initialized, create a default one
            from ..utils.logger import Logger
            default_logger = Logger({
                'level': 'debug' if self.sandbox.is_debug else 'info',
                'console': True
            })
            return default_logger.child('FileSystemService')
    
    async def upload_file(self, local_path: str, remote_path: str) -> None:
        """Upload file from local to sandbox.
        
        Args:
            local_path: Local file path
            remote_path: Remote file path in sandbox
        """
        upload_result = await self.sandbox.upload_file_to_sandbox(local_path, remote_path)
        return upload_result
    
    async def download_file(self, remote_path: str, local_path: str) -> None:
        """Download file from sandbox to local.
        
        Args:
            remote_path: Remote file path in sandbox
            local_path: Local file path
        """
        download_result = await self.sandbox.copy_file_from_sandbox(remote_path, local_path)
        return download_result
    
    async def write_file(self, remote_path: str, content: Union[str, bytes]) -> None:
        """Write content to file in sandbox.
        
        Args:
            remote_path: Remote file path in sandbox
            content: File content to write (string or bytes)
        """
        write_result = await self.sandbox.write_file_to_sandbox(remote_path, content)
        return write_result
    
    async def read_file(
        self, 
        remote_path: str, 
        options: Optional[Dict[str, str]] = None
    ) -> Union[str, bytes]:
        """Read content from file in sandbox.
        
        Args:
            remote_path: Remote file path in sandbox
            options: Dictionary with 'encoding' key ('utf8', 'base64', or 'binary')
            
        Returns:
            File content as string or bytes depending on encoding
        """
        read_result = await self.sandbox.read_file_from_sandbox(remote_path, options)
        return read_result