#!/usr/bin/env python3
"""
Test script for the WhatsApp webhook endpoint.
This simulates a Twilio webhook call to test the application locally.
"""

import requests
import json

def test_webhook():
    """Test the webhook endpoint with sample data."""
    
    # Webhook endpoint
    url = "http://localhost:5002/message"
    
    # Test 1: New user (should trigger triage)
    test_data_new_user = {
        'From': 'whatsapp:+1234567890',
        'Body': '',
        'MediaUrl0': '',
    }
    
    # Test 2: Triage response
    test_data_triage = {
        'From': 'whatsapp:+1234567890',
        'Body': 'John Smith',
        'MediaUrl0': '',
    }
    
    # Test 3: Message with health image
    test_data_image = {
        'From': 'whatsapp:+1234567890',
        'Body': 'skin-rash',
        'MediaUrl0': 'https://picsum.photos/200/300.jpg',
        'MediaContentType0': 'image/jpeg',
    }
    
    print("Testing webhook endpoint...")
    print(f"URL: {url}")
    
    # Test text-only message
    print("\n--- Test 1: Text-only message ---")
    print(f"Data: {test_data_text}")
    
    try:
        response = requests.post(url, data=test_data_text)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Text message test successful!")
        else:
            print("❌ Text message test failed!")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test image message
    print("\n--- Test 2: Message with image ---")
    print(f"Data: {test_data_image}")
    
    try:
        response = requests.post(url, data=test_data_image)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Image message test successful!")
            print("Check uploads/1234567890/ directory for saved image")
        else:
            print("❌ Image message test failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on localhost:5002")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_webhook()
