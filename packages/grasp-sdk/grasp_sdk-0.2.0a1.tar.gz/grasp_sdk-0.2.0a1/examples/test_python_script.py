"""Example demonstrating Python script execution support in Grasp SDK.

This example shows how to use the enhanced run_script method to execute
Python scripts alongside JavaScript in the E2B sandbox environment.
"""

import asyncio
from grasp_sdk.services.sandbox import SandboxService
from grasp_sdk.models import ISandboxConfig


async def main():
    """Main example function demonstrating Python script support."""
    
    # Configure sandbox service
    config: ISandboxConfig = {
        'key': 'your-api-key-here',  # Replace with your actual API key
        'timeout': 30000,
        'workspace': 'your-workspace-id',  # Replace with your workspace ID
        'debug': True
    }
    
    # Create sandbox service
    sandbox = SandboxService(config)
    
    try:
        # Create and start sandbox
        await sandbox.create_sandbox('base')
        print("✅ Sandbox created successfully")
        
        # Example 1: Basic Python script execution
        print("\n🐍 Example 1: Basic Python script")
        python_code = """
print("Hello from Python in E2B sandbox!")
print(f"Python version: {__import__('sys').version}")
"""
        
        result = await sandbox.run_script(python_code, {'type': 'py'})
        print(f"Output: {getattr(result, 'stdout', str(result))}")
        
        # Example 2: Python script with mathematical operations
        print("\n🧮 Example 2: Python mathematical operations")
        math_code = """
import math

# Calculate some mathematical operations
numbers = [1, 2, 3, 4, 5]
print(f"Numbers: {numbers}")
print(f"Sum: {sum(numbers)}")
print(f"Square root of 16: {math.sqrt(16)}")
print(f"Pi: {math.pi:.4f}")
"""
        
        result = await sandbox.run_script(math_code, {'type': 'py'})
        print(f"Output: {getattr(result, 'stdout', str(result))}")
        
        # Example 3: Python script with environment variables
        print("\n🌍 Example 3: Python script with environment variables")
        env_code = """
import os

print(f"Custom variable: {os.environ.get('MY_CUSTOM_VAR', 'Not set')}")
print(f"Python path: {os.environ.get('PYTHONPATH', 'Default')}")
print(f"Current working directory: {os.getcwd()}")
"""
        
        result = await sandbox.run_script(env_code, {
            'type': 'py',
            'envs': {
                'MY_CUSTOM_VAR': 'Hello from environment!',
                'PYTHONPATH': '/custom/python/path'
            }
        })
        print(f"Output: {getattr(result, 'stdout', str(result))}")
        
        # Example 4: Python script with package installation
        print("\n📦 Example 4: Python script with package installation")
        package_code = """
import requests
import json

# Make a simple HTTP request
response = requests.get('https://httpbin.org/json')
data = response.json()
print(f"HTTP Status: {response.status_code}")
print(f"Response data: {json.dumps(data, indent=2)}")
"""
        
        result = await sandbox.run_script(package_code, {
            'type': 'py',
            'preCommand': 'pip install requests && '
        })
        print(f"Output: {getattr(result, 'stdout', str(result))}")
        
        # Example 5: Python script with custom working directory
        print("\n📁 Example 5: Python script with custom working directory")
        file_code = """
import os

# Create a test file
with open('test_file.txt', 'w') as f:
    f.write('Hello from Python file operation!')

# Read the file back
with open('test_file.txt', 'r') as f:
    content = f.read()
    print(f"File content: {content}")

print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")
"""
        
        result = await sandbox.run_script(file_code, {
            'type': 'py',
            'cwd': '/home/user/python_workspace'
        })
        print(f"Output: {getattr(result, 'stdout', str(result))}")
        
        # Example 6: Compare with JavaScript execution
        print("\n🔄 Example 6: JavaScript vs Python comparison")
        
        # JavaScript version
        js_code = """
const numbers = [1, 2, 3, 4, 5];
const sum = numbers.reduce((a, b) => a + b, 0);
console.log(`JavaScript - Numbers: ${numbers}`);
console.log(`JavaScript - Sum: ${sum}`);
console.log(`JavaScript - Node version: ${process.version}`);
"""
        
        js_result = await sandbox.run_script(js_code, {'type': 'cjs'})
        print(f"JavaScript Output: {getattr(js_result, 'stdout', str(js_result))}")
        
        # Python version
        py_code = """
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
print(f"Python - Numbers: {numbers}")
print(f"Python - Sum: {total}")
print(f"Python - Version: {__import__('sys').version.split()[0]}")
"""
        
        py_result = await sandbox.run_script(py_code, {'type': 'py'})
        print(f"Python Output: {getattr(py_result, 'stdout', str(py_result))}")
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as error:
        print(f"❌ Error: {error}")
    
    finally:
        # Clean up sandbox
        await sandbox.destroy()
        print("\n🧹 Sandbox destroyed")


if __name__ == "__main__":
    # Run the example
    print("🚀 Starting Python script execution examples...")
    asyncio.run(main())