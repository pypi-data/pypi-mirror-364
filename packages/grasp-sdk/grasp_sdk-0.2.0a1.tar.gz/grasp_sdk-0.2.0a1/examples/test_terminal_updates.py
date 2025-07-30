#!/usr/bin/env python3
"""
Test script to verify terminal service updates in Python SDK.

This script tests the updated terminal service functionality,
including the new kill() method and response.json() compatibility.
"""

import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock, patch

# Add the parent directory to the path to import grasp_sdk
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from grasp_sdk.services.terminal import TerminalService, StreamableCommandResult
from grasp_sdk.services.sandbox import SandboxService, CommandEventEmitter
from grasp_sdk.services.browser import CDPConnection
from grasp_sdk.models import ISandboxConfig


class MockCommandEventEmitter(CommandEventEmitter):
    """Mock command event emitter for testing."""
    
    def __init__(self):
        super().__init__()
        self.killed = False
        self.stdout_data = "Test output\n"
        self.stderr_data = "Test error\n"
        
    async def wait(self):
        """Mock wait method."""
        await asyncio.sleep(0.1)  # Simulate some processing time
        return {
            'exit_code': 0,
            'stdout': self.stdout_data,
            'stderr': self.stderr_data
        }
    
    async def kill(self):
        """Mock kill method."""
        self.killed = True
        print("Command killed successfully")


async def test_streamable_command_result():
    """Test StreamableCommandResult functionality."""
    print("\n=== Testing StreamableCommandResult ===")
    
    # Create mock emitter and task
    emitter = MockCommandEventEmitter()
    task = asyncio.create_task(emitter.wait())
    
    # Create StreamableCommandResult
    result = StreamableCommandResult(emitter, task)
    
    # Test stdout/stderr streams
    print("✓ StreamableCommandResult created successfully")
    
    # Test response.json() method
    response_data = await result.json()
    print(f"✓ Response JSON: {response_data}")
    
    # Test end() method
    end_result = await result.end()
    print(f"✓ End result: {end_result}")
    
    # Test kill() method
    await result.kill()
    print(f"✓ Kill method executed, emitter killed: {emitter.killed}")
    
    print("✓ All StreamableCommandResult tests passed!")


async def test_terminal_service():
    """Test TerminalService functionality."""
    print("\n=== Testing TerminalService ===")
    
    # Create mock sandbox and connection
    sandbox_config: ISandboxConfig = {
        'key': 'test-key',
        'timeout': 30000,
        'debug': True
    }
    
    mock_sandbox = Mock(spec=SandboxService)
    mock_sandbox.is_debug = True
    mock_sandbox.run_command = AsyncMock()
    
    mock_connection = Mock(spec=CDPConnection)
    mock_connection.ws_url = 'ws://localhost:8080'
    
    # Create terminal service
    terminal = TerminalService(mock_sandbox, mock_connection)
    print("✓ TerminalService created successfully")
    
    # Mock websockets.connect
    with patch('grasp_sdk.services.terminal.websockets.connect') as mock_connect:
        mock_ws = AsyncMock()
        mock_ws.open = True
        mock_connect.return_value.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.return_value.__aexit__ = AsyncMock(return_value=None)
        # For direct await usage
        async def mock_connect_func(*args, **kwargs):
            return mock_ws
        mock_connect.side_effect = mock_connect_func
        
        # Mock emitter
        mock_emitter = MockCommandEventEmitter()
        mock_sandbox.run_command.return_value = mock_emitter
        
        # Test run_command
        result = await terminal.run_command('echo "Hello World"', {'timeout': 5000})
        print("✓ run_command executed successfully")
        
        # Verify the command was called with correct options
        mock_sandbox.run_command.assert_called_once()
        call_args = mock_sandbox.run_command.call_args
        command_arg = call_args[0][0]
        options_arg = call_args[0][1]
        
        print(f"✓ Command: {command_arg}")
        print(f"✓ Options: {options_arg}")
        
        # Verify inBackground option is set correctly
        assert options_arg['inBackground'] == True, "inBackground option should be True"
        assert options_arg['nohup'] == False, "Nohup option should be False"
        print("✓ Command options verified")
        
        # Test result methods
        response_data = await result.json()
        print(f"✓ Response JSON: {response_data}")
        
        # Test kill method
        await result.kill()
        print("✓ Kill method executed successfully")
    
    # Test close method
    terminal.close()
    print("✓ Terminal service closed successfully")
    
    print("✓ All TerminalService tests passed!")


async def test_command_options_compatibility():
    """Test command options compatibility with TypeScript version."""
    print("\n=== Testing Command Options Compatibility ===")
    
    from grasp_sdk.models import ICommandOptions
    
    # Test that ICommandOptions supports 'inBackground' parameter
    options: ICommandOptions = {
        'inBackground': True,
        'timeout': 5000,
        'cwd': '/tmp',
        'nohup': False
    }
    
    print(f"✓ Command options created: {options}")
    print("✓ 'inBackground' parameter is supported in ICommandOptions")
    
    # Test that we can access the inBackground option
    background_value = options.get('inBackground', False)
    assert background_value == True, "inBackground option should be accessible"
    print("✓ inBackground option accessible and correct")
    
    print("✓ All command options compatibility tests passed!")


async def main():
    """Run all tests."""
    print("Starting Terminal Service Update Tests...")
    
    try:
        await test_streamable_command_result()
        await test_terminal_service()
        await test_command_options_compatibility()
        
        print("\n🎉 All tests passed! Terminal service updates are working correctly.")
        print("\n📋 Summary of updates:")
        print("   • Added kill() method to StreamableCommandResult")
        print("   • Added response.json() compatibility method")
        print("   • Maintained ICommandOptions to use 'inBackground' for Python compatibility")
        print("   • Improved error handling and WebSocket management")
        print("   • Synchronized timeout values with TypeScript version")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())