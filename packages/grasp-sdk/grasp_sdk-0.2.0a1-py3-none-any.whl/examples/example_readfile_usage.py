#!/usr/bin/env python3
"""
Example usage of the readFile functionality in Grasp Python SDK.

This example demonstrates:
1. How to create a filesystem service
2. How to write files to sandbox
3. How to read files from sandbox
4. Error handling for file operations
"""

import asyncio
import os
from grasp_sdk import Grasp


async def main():
    """Main example function."""
    print("📚 Grasp SDK readFile Example")
    print("==============================")
    
    session = None
    try:
        # Launch browser and get session
        print("\n🚀 Step 1: Launching browser...")
        grasp = Grasp()
        session = await grasp.launch({
            'browser': {
                'headless': True,
                'debug': False  # Set to True for more detailed logs
            },
            'keepAliveMS': 30000,
            'timeout': 60000
        })
        print(f"✅ Browser launched! Session ID: {session.id}")
        
        # Get filesystem service from session
        print("\n📁 Step 2: Getting filesystem service...")
        filesystem = session.files
        print("✅ Filesystem service ready!")
        
        # Example 1: Write and read a text file
        print("\n📝 Example 1: Text file operations")
        print("-" * 40)
        
        text_file_path = "/home/user/example.txt"
        text_content = """Hello from Grasp SDK!

This is an example text file.
It contains multiple lines and unicode: 你好世界 🌍

Timestamp: $(date)
"""
        
        print(f"Writing content to {text_file_path}...")
        await filesystem.write_file(text_file_path, text_content)
        print("✅ File written successfully!")
        
        print(f"Reading content from {text_file_path}...")
        read_content = await filesystem.read_file(text_file_path)
        print("✅ File read successfully!")
        print(f"📄 Content preview (first 100 chars): {repr(read_content[:100])}...")
        
        # Example 2: Read a configuration file
        print("\n⚙️  Example 2: Configuration file")
        print("-" * 40)
        
        config_path = "/home/user/config.json"
        config_content = '''{
  "app_name": "My Grasp App",
  "version": "1.0.0",
  "settings": {
    "debug": true,
    "max_connections": 100,
    "allowed_origins": ["localhost", "*.example.com"]
  }
}'''
        
        await filesystem.write_file(config_path, config_content)
        config_data = await filesystem.read_file(config_path)
        
        # Parse JSON
        import json
        parsed_config = json.loads(config_data)
        print(f"✅ Config loaded: {parsed_config['app_name']} v{parsed_config['version']}")
        
        # Example 3: Error handling
        print("\n🚨 Example 3: Error handling")
        print("-" * 40)
        
        try:
            await filesystem.read_file("/home/user/nonexistent.txt")
            print("❌ This should not happen!")
        except Exception as e:
            print(f"✅ Correctly caught error: {type(e).__name__}: {e}")
        
        # Example 4: Binary file handling (simulated)
        print("\n🖼️  Example 4: Binary file handling")
        print("-" * 40)
        
        # Create a fake binary file (in real usage, this might be an image)
        binary_path = "/home/user/data.bin"
        binary_content = "This simulates binary data\x00\x01\x02\xFF"
        
        await filesystem.write_file(binary_path, binary_content)
        binary_data = await filesystem.read_file(binary_path)
        
        print(f"✅ Binary file handled (length: {len(binary_data)} chars)")
        print(f"📊 Data preview: {repr(binary_data[:50])}...")
        
        print("\n🎉 All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if session:
            print("\n🧹 Cleaning up...")
            await session.close()
            print("✅ Cleanup completed!")


if __name__ == "__main__":
    print("Starting Grasp SDK readFile example...")
    
    # Check environment
    if not os.getenv('GRASP_KEY'):
        print("\n⚠️  Warning: GRASP_KEY environment variable not set.")
        print("   Please set your Grasp API key to run this example:")
        print("   export GRASP_KEY='your-api-key-here'")
        print("\n   You can get your API key from: https://grasp.dev/dashboard")
        exit(1)
    
    asyncio.run(main())