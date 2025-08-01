#!/usr/bin/env python3
"""
Simple API tester for the Computer Use Agent Backend.
"""

import asyncio
import json
from typing import Dict, Any

import httpx

from app.config import settings


class APITester:
    """Simple API tester for the backend."""
    
    def __init__(self, base_url: str = None):
        if base_url is None:
            base_url = f"http://{settings.host}:{settings.port}"
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def test_health(self) -> Dict[str, Any]:
        """Test health endpoint."""
        print("Testing health endpoint...")
        response = await self.client.get(f"{self.base_url}/health")
        print(f"Health status: {response.status_code}")
        return response.json()
    
    async def test_api_status(self) -> Dict[str, Any]:
        """Test API status endpoint."""
        print("Testing API status endpoint...")
        response = await self.client.get(f"{self.base_url}/api/v1/status")
        print(f"API status: {response.status_code}")
        return response.json()
    
    async def test_create_session(self) -> Dict[str, Any]:
        """Test session creation."""
        print("Testing session creation...")
        session_data = {
            "title": "Test Session",
            "description": "A test session for API validation",
            "model_name": settings.anthropic_model,
            "max_tokens": settings.default_max_tokens,
            "temperature": settings.default_temperature
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/sessions/",
            json=session_data
        )
        print(f"Session creation: {response.status_code}")
        return response.json()
    
    async def test_get_sessions(self) -> Dict[str, Any]:
        """Test getting sessions."""
        print("Testing get sessions...")
        response = await self.client.get(f"{self.base_url}/api/v1/sessions/")
        print(f"Get sessions: {response.status_code}")
        return response.json()
    
    async def test_send_message(self, session_id: int) -> Dict[str, Any]:
        """Test sending a message."""
        print(f"Testing send message to session {session_id}...")
        message_data = {
            "message": "Hello, this is a test message!",
            "session_id": session_id
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/v1/chat/send",
            json=message_data
        )
        print(f"Send message: {response.status_code}")
        return response.json()
    
    async def test_get_messages(self, session_id: int) -> Dict[str, Any]:
        """Test getting messages for a session."""
        print(f"Testing get messages for session {session_id}...")
        response = await self.client.get(
            f"{self.base_url}/api/v1/chat/{session_id}/messages"
        )
        print(f"Get messages: {response.status_code}")
        return response.json()
    
    async def test_vnc_connection(self, session_id: int) -> Dict[str, Any]:
        """Test VNC connection endpoint."""
        print(f"Testing VNC connection for session {session_id}...")
        response = await self.client.get(
            f"{self.base_url}/api/v1/vnc/connection/{session_id}"
        )
        print(f"VNC connection: {response.status_code}")
        return response.json()
    
    async def run_all_tests(self):
        """Run all tests."""
        print("Starting API tests...\n")
        
        try:
            # Test basic endpoints
            health = await self.test_health()
            print(f"Health response: {json.dumps(health, indent=2)}\n")
            
            api_status = await self.test_api_status()
            print(f"API status response: {json.dumps(api_status, indent=2)}\n")
            
            # Test session management
            sessions = await self.test_get_sessions()
            print(f"Get sessions response: {json.dumps(sessions, indent=2)}\n")
            
            # Create a new session
            new_session = await self.test_create_session()
            print(f"Create session response: {json.dumps(new_session, indent=2)}\n")
            
            # Test with the created session
            if new_session.get("success") and "session" in new_session:
                session_id = new_session["session"]["id"]
                
                # Test message sending
                try:
                    send_result = await self.test_send_message(session_id)
                    print(f"Send message response: {json.dumps(send_result, indent=2)}\n")
                except Exception as e:
                    print(f"Send message failed (expected if no API key): {e}\n")
                
                # Test getting messages
                messages = await self.test_get_messages(session_id)
                print(f"Get messages response: {json.dumps(messages, indent=2)}\n")
                
                # Test VNC connection
                vnc = await self.test_vnc_connection(session_id)
                print(f"VNC connection response: {json.dumps(vnc, indent=2)}\n")
            
        except Exception as e:
            print(f"Test failed: {e}")
        finally:
            await self.client.aclose()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Main function to run tests."""
    tester = APITester()
    try:
        await tester.run_all_tests()
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main()) 