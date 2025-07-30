#!/usr/bin/env python3
"""
Grasp Terminal Example

This example demonstrates how to use the Grasp Terminal service
to run commands and manage files in a sandbox environment.

Equivalent to the TypeScript version in examples/grasp-terminal.ts
"""

import asyncio
import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grasp_sdk import Grasp

# 加载环境变量
load_dotenv("../.env.grasp")

async def main():
    """Main function demonstrating terminal service usage."""
    print("🚀 Starting Grasp Terminal example...")
    
    try:
        grasp = Grasp()
        session = await grasp.launch({
            'browser': {
                # 'type': 'chrome-stable',
                # 'headless': False,
                # 'adblock': True,
                # 'debug': True,
            },
            'keepAliveMS': 10000,
            'timeout': 3600000,  # 容器最长运行1小时（最大值可以为一天 86400000）
        })

        connection = session.browser.connection
        print(f"✅ Browser launched! Connection ID: {connection.id}")
        
        # Create terminal connection
        print("📡 Creating terminal connection...")
        terminal = session.terminal.create()
        
        print("✅ Terminal connected!")
        
        # Test FFmpeg availability (equivalent to TypeScript version)
        print("🔍 Checking FFmpeg availability...")
        command = await terminal.run_command('ffmpeg')
        result = await command.json()
        print(f"FFmpeg version check result: {result}")
        
        # Create and write a test JavaScript file
        print("📝 Writing test JavaScript file...")
        code = """
(async function() {
  for(let i = 0; i < 10; i++) {
    console.log(i);
    await new Promise(resolve => setTimeout(resolve, 200));
  }
})();
"""
        await session.files.write_file('test.js', code)
        print("✅ File 'test.js' written successfully!")
        
        # Run the Node.js script
        print("🚀 Running Node.js script...")
        command2 = await terminal.run_command('node test.js')
        
        # Handle streaming output (Python equivalent of TypeScript pipe)
        print("📊 Streaming output:")
        
        # Set up stdout streaming
        # Set up event handlers for real-time output (much simpler!)
        def handle_stdout(data):
            print(f"STDOUT: {data}", end='')
        
        def handle_stderr(data):
            print(f"STDERR: {data}", end='', file=sys.stderr)
        
        # Register event handlers - now it works just like Node.js!
        command2.on('stdout', handle_stdout)
        command2.on('stderr', handle_stderr)
        
        # Wait for command completion
        await command2.end()
        
        # Close terminal connection
        # print("🔌 Closing terminal connection...")
        # terminal.close()
        
        # Close the session
        print("🛑 Closing session...")
        await session.close()
        
        print("✅ Example completed successfully!")
        
    except Exception as error:
        print(f"❌ Error occurred: {error}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Run the async main function
    asyncio.run(main())