#!/usr/bin/env python3
"""Example usage of the new Grasp classes."""

import asyncio
import os
from grasp_sdk import Grasp, GraspSession, launch_browser


async def example_grasp_usage():
    """Example demonstrating how to use the new Grasp classes."""
    print("=== Grasp SDK Python Implementation Example ===")
    
    # Initialize Grasp SDK
    grasp = Grasp({
        'apiKey': os.environ.get('GRASP_KEY', 'your-api-key-here')
    })
    
    print(f"Initialized Grasp SDK with API key: {grasp.key[:8]}...")
    
    # Example 1: Launch a new browser session
    print("\n1. Launching a new browser session...")
    try:
        session = await grasp.launch({
            'browser': {
                'type': 'chromium',
                'headless': True,
                'timeout': 30000
            }
        })
        print(f"✓ Session launched with ID: {session.id}")
        
        # Access browser endpoint
        browser_endpoint = session.browser.get_endpoint()
        print(f"✓ Browser WebSocket endpoint: {browser_endpoint}")
        
        # Create terminal
        terminal = session.terminal.create()
        print("✓ Terminal service created")
        
        # Access file system
        print(f"✓ File system service available: {type(session.files).__name__}")
        
        # Close session
        await session.close()
        print("✓ Session closed successfully")
        
    except Exception as e:
        print(f"❌ Error launching session: {e}")
        print("Note: This requires a valid API key and network access")
    
    # Example 2: Using static method
    print("\n2. Using static launch_browser method...")
    try:
        connection = await launch_browser({
            'type': 'chromium',
            'headless': True
        })
        print(f"✓ Browser launched with connection: {connection.ws_url}")
        
    except Exception as e:
        print(f"❌ Error with static method: {e}")
        print("Note: This requires a valid API key and network access")
    
    # Example 3: Connect to existing session
    print("\n3. Connecting to existing session...")
    try:
        # This would connect to an existing session ID
        # session = await grasp.connect('existing-session-id')
        print("✓ Connection method available (requires existing session ID)")
        
    except Exception as e:
        print(f"❌ Error connecting: {e}")
    
    print("\n=== Example completed ===")
    print("\nFor full functionality, ensure you have:")
    print("- Valid GRASP_KEY environment variable")
    print("- Network access to Grasp services")
    print("- Proper sandbox configuration")


if __name__ == '__main__':
    asyncio.run(example_grasp_usage())