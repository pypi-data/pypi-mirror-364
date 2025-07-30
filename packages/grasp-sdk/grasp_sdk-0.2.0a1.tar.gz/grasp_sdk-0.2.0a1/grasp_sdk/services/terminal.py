#!/usr/bin/env python3
"""
Terminal service for managing terminal command operations.

This module provides Python implementation of the terminal service,
equivalent to the TypeScript version in src/services/terminal.service.ts
"""

import asyncio
import io
from typing import Optional, Any, Dict, Callable
from ..models import ICommandOptions
from ..utils.logger import get_logger, Logger
from .sandbox import SandboxService, CommandEventEmitter
from .browser import CDPConnection


class StreamableCommandResult:
    """
    Streamable command result with event-based output streaming and json result.
    """
    
    def __init__(self, emitter: CommandEventEmitter, task):
        self.emitter = emitter
        self._task = task
        # For backward compatibility, provide stdout/stderr as StringIO
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        
        # Set up internal event handlers to populate StringIO streams
        def on_stdout(data: str) -> None:
            self.stdout.write(data)
            self.stdout.flush()
        
        def on_stderr(data: str) -> None:
            self.stderr.write(data)
            self.stderr.flush()
        
        # Register internal handlers
        self.emitter.on('stdout', on_stdout)
        self.emitter.on('stderr', on_stderr)
    
    def on(self, event: str, callback: Callable) -> None:
        """Register event listener for stdout, stderr, or exit events.
        
        Args:
            event: Event name ('stdout', 'stderr', 'exit')
            callback: Callback function to handle the event
        """
        self.emitter.on(event, callback)
    
    def off(self, event: str, callback: Callable) -> None:
        """Remove event listener.
        
        Args:
            event: Event name ('stdout', 'stderr', 'exit')
            callback: Callback function to remove
        """
        self.emitter.off(event, callback)
    
    async def end(self) -> None:
        """Wait until the command finishes."""
        try:
            await self._task
        except Exception as e:
            # Log error but don't raise to avoid breaking cleanup
            pass
    
    async def kill(self) -> None:
        """Kill the running command and cleanup resources."""
        try:
            await self.emitter.kill()
            # Close the streams
            self.stdout.close()
            self.stderr.close()
        except Exception as e:
            # Log error but don't raise to avoid breaking cleanup
            pass
    
    async def json(self) -> Any:
        """Get the final command result as JSON."""
        try:
            return await self._task
        except Exception as e:
            # 如果任务中发生异常，返回异常信息作为结果
            return {
                'error': str(e),
                'exit_code': getattr(e, 'exit_code', -1),
                'stdout': '',
                'stderr': str(e)
            }


class Commands:
    """
    Command execution operations for terminal service.
    """
    
    def __init__(self, sandbox: SandboxService, connection: CDPConnection):
        self.sandbox = sandbox
        self.connection = connection
        self.logger = self._get_default_logger()
    
    def _get_default_logger(self) -> Logger:
        """Gets or creates a default logger instance.
        
        Returns:
            Logger instance
        """
        try:
            return get_logger().child('TerminalService')
        except Exception:
            # If logger is not initialized, create a default one
            from ..utils.logger import Logger
            default_logger = Logger({
                'level': 'debug' if self.sandbox.is_debug else 'info',
                'console': True
            })
            return default_logger.child('TerminalService')
    
    async def run_command(
        self, command: str, options: Optional[ICommandOptions] = None
    ) -> StreamableCommandResult:
        """Run command in sandbox with streaming output.
        
        Args:
            command: Command to execute
            options: Command execution options
            
        Returns:
            StreamableCommandResult with event-based streaming
        """
        ws = None
        try:            
            if options is None:
                options = {}
            
            # Force background execution for streaming
            bg_options: ICommandOptions = {**options, 'inBackground': True, 'nohup': False}
            
            emitter: Optional[CommandEventEmitter] = await self.sandbox.run_command(
                command, bg_options
            )
            
            if emitter is None:
                raise RuntimeError(f"Failed to start command: {command}")
            
            # Create task for final result
            async def get_result():
                result = await emitter.wait()
                return result
            
            task = asyncio.create_task(get_result())
            
            return StreamableCommandResult(emitter, task)
        except Exception as error:
            self.logger.error('Run command failed', {'error': str(error)})
            raise error


class TerminalService(Commands):
    """
    Terminal service for managing terminal command operations.
    """
    
    def __init__(self, sandbox: SandboxService, connection: CDPConnection):
        """Initialize terminal service.
        
        Args:
            sandbox: The sandbox service instance
            connection: The CDP connection for browser integration
        """
        super().__init__(sandbox, connection)
    
    def close(self) -> None:
        """Close terminal service and cleanup resources."""
        self.logger.info('Terminal service closed')