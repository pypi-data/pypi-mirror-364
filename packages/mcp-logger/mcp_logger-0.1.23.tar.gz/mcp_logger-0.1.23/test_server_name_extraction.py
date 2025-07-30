"""Test automatic server name extraction from function names"""
import asyncio
from observee_logger import observee_usage_logger
import os

# Don't set MCP server name - let it extract from function name

@observee_usage_logger
async def myserver__calculate(a: int, b: int):
    """Tool with server name in function name"""
    return a + b

@observee_usage_logger
async def anotherserver__get_prompt_data():
    """Prompt function with server name"""
    return "This is a prompt response"

async def main():
    print("Testing automatic server name extraction...\n")
    
    # Test tool function
    result1 = await myserver__calculate(5, 3)
    print(f"Calculator result: {result1}")
    print("Expected: server_name='myserver', tool_name='calculate'")
    
    # Test prompt function  
    result2 = await anotherserver__get_prompt_data()
    print(f"\nPrompt result: {result2}")
    print("Expected: server_name='anotherserver', prompt_name='get_prompt_data'")
    
    print("\nCheck the logs to verify server names were extracted correctly!")

if __name__ == "__main__":
    asyncio.run(main())