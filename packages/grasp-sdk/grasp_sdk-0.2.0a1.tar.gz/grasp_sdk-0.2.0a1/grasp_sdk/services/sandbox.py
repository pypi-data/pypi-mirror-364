#!/usr/bin/env python3
"""
Sandbox service for managing E2B sandbox lifecycle and operations.

This module provides Python implementation of the sandbox service,
equivalent to the TypeScript version in src/services/sandbox.service.ts
"""

import asyncio
import json
import os
import tempfile
import time
from typing import Dict, Any, Optional, Union, List, Callable
from pathlib import Path
from e2b import AsyncSandbox

# Type definitions for E2B SDK
from typing import Any as CommandHandle, Any as CommandResult

from ..models import ISandboxConfig, SandboxStatus, IScriptOptions, ICommandOptions
from ..utils.logger import Logger, get_logger
from ..utils.config import get_config
from ..utils.auth import verify


class CommandEventEmitter:
    """
    Extended event emitter for background command execution.
    Emits 'stdout', 'stderr', and 'exit' events.
    """
    
    def __init__(self, handle: Optional[Any] = None):
        self.handle = handle
        self._callbacks: Dict[str, List[Callable]] = {
            'stdout': [],
            'stderr': [],
            'exit': [],
            'error': []
        }
    
    def set_handle(self, handle: Any) -> None:
        """Set the command handle (used internally)."""
        self.handle = handle
    
    def on(self, event: str, callback: Callable) -> None:
        """Register event listener."""
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)
    
    def off(self, event: str, callback: Callable) -> None:
        """Remove event listener."""
        if event in self._callbacks and callback in self._callbacks[event]:
            self._callbacks[event].remove(callback)
    
    def emit(self, event: Any, *args) -> None:
        """Emit event to all registered listeners."""
        # print(f'🚀 emit ${event}')
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    callback(*args)
                except Exception as e:
                    # Ignore callback errors to prevent breaking the emitter
                    pass
    
    async def wait(self) -> Any:
        """Wait for command to complete.
        
        Returns:
            Command result or exception result if command fails
        """
        while not self.handle:
            await asyncio.sleep(0.1)
        try:
            return await self.handle.wait()
        except Exception as ex:
            # 对于 CommandExitException，提取有用信息并返回结构化结果
            if hasattr(ex, 'exit_code') or 'CommandExitException' in str(type(ex)):
                return {
                    'error': str(ex),
                    'exit_code': getattr(ex, 'exit_code', -1),
                    'stdout': getattr(ex, 'stdout', ''),
                    'stderr': getattr(ex, 'stderr', str(ex))
                }
            # Return exception result if available, similar to TypeScript version
            if hasattr(ex, 'result'):
                # 尝试获取异常的结果属性,如果不存在则返回None
                return getattr(ex, 'result', None)
            # 对于其他异常，返回结构化错误信息
            return {
                'error': str(ex),
                'exit_code': -1,
                'stdout': '',
                'stderr': str(ex)
            }
    
    async def kill(self) -> None:
        """Kill the running command."""
        if not self.handle:
            raise RuntimeError('Command handle not set')
        await self.handle.kill()
    
    def get_handle(self) -> Optional[Any]:
        """Get the original command handle."""
        return self.handle


class SandboxService:
    """
    E2B Sandbox service for managing sandbox lifecycle and operations.
    """
    
    def __init__(self, config: ISandboxConfig):
        self.config = config
        self.sandbox: Optional[Any] = None
        self.status: SandboxStatus = SandboxStatus.STOPPED
        self.logger = self._get_default_logger()
        
        # Default working directory
        self.DEFAULT_WORKING_DIRECTORY = '/home/user'
    
    def _get_default_logger(self) -> Logger:
        """Gets or creates a default logger instance."""
        try:
            return get_logger().child('SandboxService')
        except Exception:
            # If logger is not initialized, create a default one
            from ..utils.logger import Logger
            default_logger = Logger({
                'level': 'debug' if self.config.get('debug', False) else 'info',
                'console': True,
            })
            return default_logger.child('SandboxService')
    
    @property
    def id(self) -> Optional[str]:
        """Get sandbox ID."""
        return self.sandbox.sandbox_id if self.sandbox else None
    
    @property
    def workspace(self) -> str:
        """Get workspace ID from API key."""
        return self.config['key'][3:19]
    
    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return bool(self.config.get('debug', False))
    
    @property
    def timeout(self) -> int:
        """Get timeout value."""
        return self.config['timeout']
    
    async def connect_sandbox(self, sandbox_id: str) -> None:
        """
        Connects to an existing sandbox.
        
        Args:
            sandbox_id: ID of the sandbox to connect to
            
        Raises:
            RuntimeError: If sandbox connection fails
        """
        try:
            self.status = SandboxStatus.CREATING
            
            self.logger.info(f'Connection Grasp sandbox: {sandbox_id}')
            
            # Verify authentication
            res = await verify({'key': self.config['key']})
            if not res['success']:
                raise RuntimeError('Authorization failed.')
            
            api_key = res['data']['token']
            
            # Connect to existing sandbox
            self.sandbox = await AsyncSandbox.connect(
                sandbox_id=sandbox_id,
                api_key=api_key
            )
            
            self.status = SandboxStatus.RUNNING
            
            # Read existing config from sandbox
            config_content = await self.sandbox.files.read('/home/user/.grasp-config.json')
            timeout = self.config['timeout']
            self.config = json.loads(config_content)
            
            # Update timeout if different
            if timeout > 0 and timeout != self.config['timeout']:
                # Note: e2b Python SDK may not have setTimeout method
                # This is equivalent to the TypeScript version's setTimeout call
                self.sandbox.set_timeout(timeout)
            
            self.logger.info('Grasp sandbox connected', {
                'sandboxId': getattr(self.sandbox, 'sandbox_id', 'unknown'),
            })
            
        except Exception as error:
            self.status = SandboxStatus.ERROR
            self.logger.error('Failed to connect Grasp sandbox', str(error))
            raise RuntimeError(f'Failed to connect sandbox: {error}')
    
    async def create_sandbox(self, template_id: str, envs: Optional[Dict[str, str]] = None) -> None:
        """
        Creates and starts a new sandbox.
        
        Raises:
            RuntimeError: If sandbox creation fails
        """

        try:
            self.status = SandboxStatus.CREATING
            
            # Verify authentication
            res = await verify({'key': self.config['key']})
            if not res['success']:
                raise RuntimeError('Authorization failed.')
            
            api_key = res['data']['token']
            
            # Create sandbox
            self.logger.info('Creating Grasp sandbox', {
                'templateId': template_id,
            })
            # Use Sandbox constructor directly (e2b SDK 1.5.3+)
            self.sandbox = await AsyncSandbox.create(
                template=template_id,    
                api_key=api_key,
                timeout=self.config['timeout'] // 1000,  # Convert ms to seconds
                envs=envs,
            )
            
            # Write grasp config file
            import json
            config_data = {
                'id': getattr(self.sandbox, 'sandbox_id', 'unknown'),
                **self.config
            }
            await self.sandbox.files.write(
                '/home/user/.grasp-config.json',
                json.dumps(config_data)
            )

            self.status = SandboxStatus.RUNNING
            self.logger.info('Grasp sandbox created successfully', {
                'sandboxId': getattr(self.sandbox, 'sandbox_id', 'unknown'),
            })
            
        except Exception as error:
            self.status = SandboxStatus.ERROR
            self.logger.error('Failed to create Grasp sandbox', str(error))
            raise RuntimeError(f'Failed to create sandbox: {error}')
    
    async def run_command(
        self,
        command: str,
        options: Optional[ICommandOptions] = None,
        quiet: bool = False
    ) -> Union[Any, CommandEventEmitter, None]:
        """
        Runs a command in the sandbox.
        
        Args:
            command: Command to execute
            options: Execution options
            quiet: Suppress error logging
            
        Returns:
            CommandResult for synchronous execution,
            CommandEventEmitter for background execution,
            or None for nohup execution
            
        Raises:
            RuntimeError: If sandbox is not running or command fails
        """
        if not self.sandbox or self.status != SandboxStatus.RUNNING:
            raise RuntimeError('Sandbox is not running. Call create_sandbox() first.')
        
        if options is None:
            options = {}
        
        cwd = options.get('cwd', self.DEFAULT_WORKING_DIRECTORY)
        timeout_ms = options.get('timeout', self.config['timeout'])
        use_nohup = options.get('nohup', False)
        in_background = options.get('inBackground', False)
        envs = options.get('envs', {})

        # print(f'command: {command}')
        # print(f'🚀 options {options}')
        
        try:
            self.logger.debug('Running command in sandbox', {
                'command': command,
                'cwd': cwd,
                'timeout': timeout_ms,
                'nohup': use_nohup,
                'background': in_background
            })
            
            if not in_background:
                # Foreground execution
                final_command = command
                if use_nohup:
                    # Create log directory
                    await self.sandbox.commands.run('mkdir -p ~/logs/grasp')
                    
                    # Generate log file name using sandbox id
                    log_file = f'~/logs/grasp/log-{self.id}.log'
                    final_command = f'nohup {command} > {log_file} 2>&1 &'
                
                if hasattr(self.sandbox, 'commands'):
                    result = await self.sandbox.commands.run(
                        final_command,
                        cwd=cwd,
                        timeout=timeout_ms,
                        envs=envs,
                        background=in_background,
                    )
                else:
                    raise RuntimeError('Sandbox commands interface not available')
                
                if hasattr(result, 'error') and result.error:
                    self.logger.error(result.stderr)
                
                return None if use_nohup else result
            
            else:
                # Background execution
                if use_nohup:
                    # Create log directory
                    await self.sandbox.commands.run('mkdir -p ~/logs/grasp')
                    
                    # Generate log file name using sandbox id
                    log_file = f'~/logs/grasp/log-{self.id}.log'
                    nohup_command = f'nohup {command} > {log_file} 2>&1 &'
                    # print(f"💬 {nohup_command}")
                    await self.sandbox.commands.run(
                        nohup_command,
                        cwd=cwd,
                        timeout=timeout_ms // 1000,
                        envs=envs,
                        background=in_background,
                    )
                    return None

                # Create CommandEventEmitter for background execution
                event_emitter = CommandEventEmitter()
                
                # Schedule background execution
                async def _execute_background():
                    try:
                        if self.sandbox and hasattr(self.sandbox, 'commands'):
                            commands_attr = getattr(self.sandbox, 'commands', None)
                            if not commands_attr:
                                raise RuntimeError("Sandbox commands not available")
                            handle = await commands_attr.run(
                                command,
                                cwd=cwd,
                                timeout=timeout_ms // 1000,
                                background=True,
                                envs=envs,
                                on_stdout=lambda data: event_emitter.emit('stdout', data),
                                on_stderr=lambda data: event_emitter.emit('stderr', data)
                            )
                        
                            event_emitter.set_handle(handle)
                        else:
                            raise RuntimeError("Sandbox or commands not available")
                        
                        # Wait for command completion (for non-nohup commands)
                        if not use_nohup:
                            try:
                                # print(f"⏳ {command}")
                                result = await handle.wait()
                                # print(f"✅ {command} 执行完毕")
                                # event_emitter.emit('stdout', '🎉 ok')
                                event_emitter.emit('exit', result.exit_code)
                            except Exception as error:
                                event_emitter.emit('error', error)
                    
                    except Exception as error:
                        event_emitter.emit('error', error)
                
                # Start background execution
                asyncio.create_task(_execute_background())
                return event_emitter
        
        except Exception as error:
            if not quiet:
                self.logger.error('Command execution failed', str(error))
            
            # Return error result as dict
            return {
                'exit_code': 1,
                'stdout': '',
                'stderr': str(error)
            }
    
    async def run_script(
        self,
        code: str,
        options: Optional[IScriptOptions] = None
    ) -> Union[Any, CommandEventEmitter]:
        """
        Runs JavaScript or Python code in the sandbox.
        
        Args:
            code: JavaScript/Python code to execute, or file path starting with '/home/user/'
            options: Script execution options (type: 'cjs', 'esm', or 'py')
            
        Returns:
            CommandResult for synchronous execution,
            CommandEventEmitter for background execution
            
        Raises:
            RuntimeError: If sandbox is not running or script execution fails
            
        Note:
            If code starts with '/home/user/', it will be treated as a file path.
            Otherwise, it will be treated as code and written to a temporary file.
            For Python scripts, use type='py' and the code will be executed with python3.
        """
        if not self.sandbox or self.status != SandboxStatus.RUNNING:
            raise RuntimeError('Sandbox is not running. Call create_sandbox() first.')
        
        if options is None:
            options = {'type': 'cjs'}
        
        try:
            # Generate temporary file name in working directory
            timestamp = int(time.time() * 1000)
            script_path = code
            
            if not code.startswith('/home/user/'):
                if options['type'] == 'py':
                    extension = 'py'
                elif options['type'] == 'esm':
                    extension = 'mjs'
                else:
                    extension = 'js'
                working_dir = options.get('cwd', self.DEFAULT_WORKING_DIRECTORY)
                script_path = f'{working_dir}/script_{timestamp}.{extension}'
                # Write code to temporary file
                await self.sandbox.files.write(script_path, code)
            
            self.logger.debug('Running script in sandbox', {
                'type': options['type'],
                'scriptPath': script_path,
                'codeLength': len(code),
            })
            
            # Choose execution command based on type
            pre_command = options.get('preCommand', '')
            if options['type'] == 'py':
                command = f'{pre_command}python3 {script_path}'
            else:
                command = f'{pre_command}node {script_path}'
            
            # Set environment variables
            envs = options.get('envs', {})
            envs['PLAYWRIGHT_BROWSERS_PATH'] = '0'

            # Prepare command options
            cmd_options: Optional[Any] = {
                'cwd': options.get('cwd'),
                'timeout': options.get('timeoutMs'),
                'inBackground': options.get('background', False),
                'nohup': options.get('nohup', False),
                'envs': envs,
            }
            
            # Execute the script
            result = await self.run_command(command, cmd_options)
            
            return result
        
        except Exception as error:
            self.logger.error('Script execution failed', str(error))
            raise RuntimeError(f'Failed to execute script: {error}')
    
    def _is_binary_file(self, file_path: str) -> bool:
        """
        Check if a file is binary based on its extension.
        
        Args:
            file_path: File path to check
            
        Returns:
            True if file is binary, false otherwise
        """
        binary_extensions = {
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.ico',
            '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv',
            '.exe', '.dll', '.so', '.dylib',
            '.bin', '.dat', '.db', '.sqlite'
        }
        
        ext = Path(file_path).suffix.lower()
        return ext in binary_extensions
    
    def _encode_content(self, data: bytes, encoding: str) -> Union[str, bytes]:
        """
        Encode content based on specified encoding.
        
        Args:
            data: Raw bytes data
            encoding: Encoding type ('utf8', 'base64', or 'binary')
            
        Returns:
            Encoded content as string or bytes
        """
        if encoding == 'utf8':
            return data.decode('utf-8')
        elif encoding == 'base64':
            import base64
            return base64.b64encode(data).decode('utf-8')
        else:  # binary
            return data
    
    async def read_file_from_sandbox(
        self, 
        remote_path: str, 
        options: Optional[Dict[str, str]] = None
    ) -> Union[str, bytes]:
        """
        Read content from a file in the sandbox.
        
        Args:
            remote_path: File path in sandbox to read from
            options: Dictionary with 'encoding' key ('utf8', 'base64', or 'binary')
            
        Returns:
            File content as string or bytes depending on encoding
            
        Raises:
            RuntimeError: If sandbox is not running or file read fails
        """
        if not self.sandbox or self.status != SandboxStatus.RUNNING:
            raise RuntimeError('Sandbox is not running. Call create_sandbox() first.')
        
        if options is None:
            options = {}
        
        # Determine encoding
        encoding = options.get('encoding')
        if not encoding:
            encoding = 'binary' if self._is_binary_file(remote_path) else 'utf8'
        
        try:
            self.logger.debug('Reading file from sandbox', {
                'remotePath': remote_path,
                'encoding': encoding
            })
            
            # Always read as bytes first
            file_content = await self.sandbox.files.read(remote_path, format='bytes')
            
            # Encode based on requested format
            return self._encode_content(file_content, encoding)
            
        except Exception as error:
            self.logger.error(f'Failed to read file from sandbox: {error}')
            raise RuntimeError(f'Failed to read file: {error}')
    
    async def write_file_to_sandbox(self, remote_path: str, content: Union[str, bytes]) -> None:
        """
        Write content directly to a file in the sandbox.
        
        Args:
            remote_path: File path in sandbox where content will be written
            content: String or bytes content to write to the file
            
        Raises:
            RuntimeError: If sandbox is not running
        """
        if not self.sandbox or self.status != SandboxStatus.RUNNING:
            raise RuntimeError('Sandbox is not running. Call create_sandbox() first.')
        
        return await self.sandbox.files.write(remote_path, content)
    
    async def copy_file_from_sandbox(self, remote_path: str, local_path: str) -> None:
        """
        Copy file from sandbox to local filesystem.
        
        Args:
            remote_path: File path in sandbox
            local_path: Local destination path
            
        Raises:
            RuntimeError: If sandbox is not running or copy fails
        """
        if not self.sandbox or self.status != SandboxStatus.RUNNING:
            raise RuntimeError('Sandbox is not running. Call create_sandbox() first.')
        
        try:
            self.logger.debug('Copying file from sandbox', {
                'remotePath': remote_path,
                'localPath': local_path,
            })
            
            # Check if file is binary
            is_binary = self._is_binary_file(remote_path)
            
            if is_binary:
                # For binary files, read as bytes
                file_content = await self.sandbox.files.read(remote_path, format='bytes')
                with open(local_path, 'wb') as f:
                    f.write(file_content)
            else:
                # For text files, read as string
                file_content = await self.sandbox.files.read(remote_path, format='text')
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
            
            self.logger.debug(f'File copied from sandbox: {remote_path} -> {local_path}')
        
        except Exception as error:
            self.logger.error(f'Failed to copy file: {error}')
            raise
    
    async def upload_file_to_sandbox(self, local_path: str, remote_path: str) -> None:
        """
        Uploads a file to the sandbox.
        
        Args:
            local_path: Local file path
            remote_path: Destination path in sandbox
            
        Raises:
            RuntimeError: If sandbox is not running or upload fails
        """
        if not self.sandbox or self.status != SandboxStatus.RUNNING:
            raise RuntimeError('Sandbox is not running. Call create_sandbox() first.')
        
        try:
            self.logger.debug('Uploading file to sandbox', {
                'localPath': local_path,
                'remotePath': remote_path,
            })
            
            with open(local_path, 'rb') as f:
                file_content = f.read()
            
            await self.sandbox.files.write(remote_path, file_content)
            
            self.logger.debug('File uploaded successfully', {
                'localPath': local_path,
                'remotePath': remote_path,
            })
        
        except Exception as error:
            self.logger.error('Failed to upload file to sandbox', str(error))
            raise RuntimeError(f'Failed to upload file: {error}')
    
    async def list_files(self, path: str) -> List[str]:
        """
        Lists files in a sandbox directory.
        
        Args:
            path: Directory path in sandbox
            
        Returns:
            List of filenames
            
        Raises:
            RuntimeError: If sandbox is not running or listing fails
        """
        if not self.sandbox or self.status != SandboxStatus.RUNNING:
            raise RuntimeError('Sandbox is not running. Call create_sandbox() first.')
        
        try:
            self.logger.debug('Listing files in sandbox', {'path': path})
            
            result = await self.run_command(f'ls -la "{path}"')
            
            if hasattr(result, 'exit_code') and getattr(result, 'exit_code', 0) != 0:
                raise RuntimeError(f'Failed to list files: {getattr(result, "stderr", "")}')
            
            # Parse ls output to extract filenames
            stdout = getattr(result, 'stdout', '') if result else ''
            if stdout:
                lines = stdout.split('\n')
                files = []
                
                for line in lines[1:]:  # Skip first line (total)
                    line = line.strip()
                    if line:
                        parts = line.split()
                        if len(parts) >= 9:  # Valid ls -la output
                            filename = parts[-1]
                            if filename not in ('.', '..'):
                                files.append(filename)
                
                return files
            
            return []
        
        except Exception as error:
            self.logger.error('Failed to list files', str(error))
            raise RuntimeError(f'Failed to list files: {error}')
    
    def _validate_safe_path(self, path: str) -> bool:
        """
        Validate if a path is safe for synchronization.
        
        Args:
            path: Path to validate
            
        Returns:
            True if path is safe, False otherwise
        """
        # Normalize path
        normalized_path = path.replace('//', '/').rstrip('/')
        
        # Check if it's an absolute path under /home/user
        if normalized_path.startswith('/'):
            # Absolute path must be under /home/user/ and not /home/user itself
            return (
                normalized_path.startswith('/home/user/') and
                normalized_path != '/home/user'
            )
        
        # Relative path checks
        # Don't allow .. to access parent directories
        if '..' in normalized_path:
            return False
        
        # Don't allow syncing current directory itself (. or empty string)
        if normalized_path in ('.', '', './'):
            return False
        
        # Relative path must be a subdirectory (starts with ./ or doesn't start with /)
        return normalized_path.startswith('./') or not normalized_path.startswith('/')
    
    async def _is_directory(self, remote_path: str) -> bool:
        """
        Check if a remote path is a directory.
        
        Args:
            remote_path: Remote path to check
            
        Returns:
            True if path is a directory, False otherwise
        """
        if not self.sandbox or self.status != SandboxStatus.RUNNING:
            return False
        
        try:
            result = await self.run_command(f'test -d "{remote_path}" && echo "true" || echo "false"')
            stdout = getattr(result, 'stdout', '').strip() if result else ''
            return stdout == 'true'
        except Exception as error:
            self.logger.debug('Error checking if path is directory', {
                'remotePath': remote_path,
                'error': str(error)
            })
            return False
    
    async def _sync_directory_recursive(
        self, 
        remote_path: str, 
        local_path: str
    ) -> int:
        """
        Recursively sync a directory from sandbox to local filesystem.
        
        Args:
            remote_path: Remote directory path
            local_path: Local directory path
            
        Returns:
            Number of files synced
        """
        synced_count = 0
        
        try:
            # Get all items in the directory
            items = await self.list_files(remote_path)
            
            if len(items) == 0:
                self.logger.debug('No items found in directory', {'remotePath': remote_path})
                return 0
            
            # Ensure local directory exists
            os.makedirs(local_path, exist_ok=True)
            
            # Process each item
            for item in items:
                remote_item_path = f"{remote_path}/{item}"
                local_item_path = os.path.join(local_path, item)
                
                # Check if it's a directory
                is_dir = await self._is_directory(remote_item_path)
                
                if is_dir:
                    self.logger.debug('Syncing subdirectory', {
                        'from': remote_item_path,
                        'to': local_item_path
                    })
                    
                    # Recursively sync subdirectory
                    sub_synced_count = await self._sync_directory_recursive(
                        remote_item_path,
                        local_item_path
                    )
                    synced_count += sub_synced_count
                else:
                    self.logger.debug('Syncing file', {
                        'from': remote_item_path,
                        'to': local_item_path
                    })
                    
                    # Sync file
                    await self.copy_file_from_sandbox(remote_item_path, local_item_path)
                    synced_count += 1
            
            return synced_count
        
        except Exception as error:
            self.logger.error('Error in recursive directory sync', {
                'remotePath': remote_path,
                'localPath': local_path,
                'error': str(error)
            })
            raise
    
    async def sync_downloads_directory(
        self, 
        dist: str = '/tmp/grasp/downloads', 
        src: str = './downloads'
    ) -> str:
        """
        Synchronize sandbox downloads directory to local filesystem (recursive sync of all subdirectories).
        
        Args:
            dist: Local target directory path, defaults to '/tmp/grasp/downloads'
            src: Remote source directory path, defaults to './downloads'
            
        Returns:
            Local sync directory path
            
        Raises:
            RuntimeError: If sandbox is not running or sync fails
            ValueError: If path is unsafe
        """
        # Validate path safety
        if not self._validate_safe_path(src):
            error_msg = f"Unsafe path detected: {src}. Only subdirectories under /home/user are allowed."
            self.logger.error('Path validation failed', {
                'path': src,
                'error': error_msg
            })
            raise ValueError(error_msg)
        
        remote_path = src
        local_path = os.path.join(dist, str(self.id), str(int(time.time() * 1000)))
        
        try:
            self.logger.debug('🗂️ Starting recursive directory sync', {
                'remotePath': remote_path,
                'localPath': local_path
            })
            
            # Check if remote directory exists
            dir_exists = await self._is_directory(remote_path)
            if not dir_exists:
                # Try to handle as file
                parent_dir = os.path.dirname(remote_path)
                file_name = os.path.basename(remote_path)
                
                files = await self.list_files(parent_dir)
                
                if file_name not in files:
                    self.logger.debug('Remote path does not exist', {'remotePath': remote_path})
                    return ''
            
            # Recursively sync directory
            synced_count = await self._sync_directory_recursive(
                remote_path,
                local_path
            )
            
            if synced_count == 0:
                self.logger.debug('No files found to sync')
                return ''
            
            self.logger.info(
                f'🎉 Successfully synced {synced_count} files recursively from {remote_path}'
            )
            
            return local_path
        
        except Exception as error:
            self.logger.error('Error syncing downloads directory:', str(error))
            raise
    
    def get_status(self) -> SandboxStatus:
        """Gets the current sandbox status."""
        return self.status
    
    def get_sandbox_id(self) -> Optional[str]:
        """Gets sandbox ID if available."""
        return getattr(self.sandbox, 'sandbox_id', None) if self.sandbox else None
    
    def get_sandbox_host(self, port: int) -> Optional[str]:
        """
        Gets the external host address for a specific port.
        
        Args:
            port: Port number to get host for
            
        Returns:
            External host address or None if sandbox not available
        """
        if not self.sandbox or self.status != SandboxStatus.RUNNING:
            self.logger.warn('Cannot get sandbox host: sandbox not running')
            return None
        
        try:
            host = self.sandbox.get_host(port)
            self.logger.debug('Got sandbox host for port', {'port': port, 'host': host})
            return host
        except Exception as error:
            self.logger.error('Failed to get sandbox host', {'port': port, 'error': error})
            return None
    
    async def destroy(self) -> None:
        """
        Destroys the sandbox and cleans up resources.
        
        Raises:
            RuntimeError: If sandbox destruction fails
        """
        if self.sandbox:
            try:
                self.logger.info('Destroying Grasp sandbox', {
                    'sandboxId': getattr(self.sandbox, 'sandbox_id', 'unknown'),
                })
                
                if await self.sandbox.is_running():
                    await self.sandbox.kill()
                self.sandbox = None
                self.status = SandboxStatus.STOPPED
                
                self.logger.info('Grasp sandbox destroyed successfully')
            
            except Exception as error:
                self.logger.error('Failed to destroy sandbox', str(error))
                raise RuntimeError(f'Failed to destroy sandbox: {error}')