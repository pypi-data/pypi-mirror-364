#!/usr/bin/env python3
"""
Example demonstrating binary file support in Grasp SDK.

This example shows how to:
1. Read files with different encoding options (utf8, base64, binary)
2. Write binary content to files
3. Handle different file types automatically
"""

import asyncio
import base64
from grasp_sdk import Grasp


async def main():
    """Demonstrate binary file support."""
    
    # Initialize Grasp
    grasp = Grasp()
    
    try:
        # Launch browser session
        session = await grasp.launch({
            'browser': {
                'type': 'chromium',
                'headless': True
            }
        })
        
        print("✅ Browser session launched successfully")
        
        # Get filesystem service
        fs = session.files
        
        # Example 1: Write and read text file with different encodings
        print("\n📝 Example 1: Text file with different encodings")
        
        text_content = "Hello, World! 你好世界! 🌍"
        await fs.write_file("/tmp/test.txt", text_content)
        
        # Read as UTF-8 (default for text files)
        content_utf8 = await fs.read_file("/tmp/test.txt", {'encoding': 'utf8'})
        print(f"UTF-8: {content_utf8}")
        
        # Read as base64
        content_base64 = await fs.read_file("/tmp/test.txt", {'encoding': 'base64'})
        print(f"Base64: {content_base64}")
        
        # Read as binary
        content_binary = await fs.read_file("/tmp/test.txt", {'encoding': 'binary'})
        print(f"Binary: {content_binary}")
        
        # Example 2: Write and read binary content
        print("\n🔢 Example 2: Binary content")
        
        # Create some binary data (a simple PNG-like header)
        binary_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        
        # Write binary data
        await fs.write_file("/tmp/test.png", binary_data)
        print("✅ Binary data written to /tmp/test.png")
        
        # Read binary file (will auto-detect as binary based on extension)
        content_auto = await fs.read_file("/tmp/test.png")
        print(f"Auto-detected binary: {type(content_auto)} - {len(content_auto)} bytes")
        
        # Read explicitly as base64
        content_b64 = await fs.read_file("/tmp/test.png", {'encoding': 'base64'})
        print(f"Base64 encoded: {content_b64}")
        
        # Example 3: Working with base64 encoded data
        print("\n📋 Example 3: Base64 workflow")
        
        # Encode some data to base64
        original_data = b"This is some binary data with special chars: \x00\x01\x02\xFF"
        b64_encoded = base64.b64encode(original_data).decode('utf-8')
        
        # Write the base64 string as text
        await fs.write_file("/tmp/encoded.txt", b64_encoded)
        
        # Read it back and decode
        read_b64 = await fs.read_file("/tmp/encoded.txt", {'encoding': 'utf8'})
        decoded_data = base64.b64decode(read_b64)
        
        print(f"Original: {original_data}")
        print(f"Encoded: {b64_encoded}")
        print(f"Decoded: {decoded_data}")
        print(f"Match: {original_data == decoded_data}")
        
        # Example 4: File type detection
        print("\n🔍 Example 4: File type detection")
        
        test_files = [
            ("/tmp/text.txt", "Plain text content"),
            ("/tmp/image.jpg", b"\xFF\xD8\xFF\xE0"),  # JPEG header
            ("/tmp/document.pdf", b"%PDF-1.4"),      # PDF header
            ("/tmp/archive.zip", b"PK\x03\x04"),     # ZIP header
        ]
        
        for filepath, content in test_files:
            await fs.write_file(filepath, content)
            
            # Read without specifying encoding (auto-detect)
            result = await fs.read_file(filepath)
            
            if isinstance(result, str):
                print(f"{filepath}: Detected as text - {result[:50]}...")
            else:
                print(f"{filepath}: Detected as binary - {len(result)} bytes")
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Clean up
        try:
            await session.close()
            print("🧹 Cleanup completed")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")


if __name__ == "__main__":
    asyncio.run(main())