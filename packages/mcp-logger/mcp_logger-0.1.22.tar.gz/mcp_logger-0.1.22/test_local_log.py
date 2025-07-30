"""Test local logging directly"""
import asyncio
from observee_logger import ObserveeConfig, observee_usage_logger
import os

# Configure to use local storage
ObserveeConfig.set_mcp_server_name("test-server")
ObserveeConfig.set_local_storage(True, "test_log.txt")

# Show current directory
print(f"Current directory: {os.getcwd()}")
print(f"Log file will be saved to: {os.path.abspath('test_log.txt')}")

@observee_usage_logger
async def test_function():
    """Test function"""
    return "Hello, World!"

async def main():
    result = await test_function()
    print(f"Result: {result}")
    
    # Give a moment for async logging to complete
    await asyncio.sleep(0.1)
    
    # Check if file exists
    if os.path.exists("test_log.txt"):
        print("\nLog file created successfully!")
        with open("test_log.txt", "r") as f:
            print("Contents:")
            print(f.read())
    else:
        print("\nLog file was not created")

if __name__ == "__main__":
    asyncio.run(main())