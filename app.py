import os
import json
import requests
import asyncio
import time
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from requests.auth import HTTPBasicAuth
from multi_tool_agent.agent import root_agent

load_dotenv()

app = Flask(__name__)

# Get Twilio credentials from environment
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

# Health service triage questions
TRIAGE_QUESTIONS = [
    "Hi! Welcome to our health service. What's your name?",
    "Hi {name}! What's your age?",
    "What's your location/city?",
    "What brings you here today? Please describe your main health concern."
]

# Response messages
WELCOME_MESSAGE = "Thank you {name}! Your profile is complete. You can now send me images or ask health-related questions."
COMPLETION_MESSAGE = "Thank you for providing your information. How can I help you today?"

class UserManager:
    def __init__(self):
        self.data_dir = 'data'
        self.uploads_dir = 'uploads'
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.uploads_dir, exist_ok=True)
        
    def get_user_file_path(self, phone_number):
        """Get the file path for a user's JSON data."""
        clean_number = phone_number.replace('+', '').replace(':', '').replace('whatsapp', '')
        return os.path.join(self.data_dir, f'user_{clean_number}.json')
    
    def user_exists(self, phone_number):
        """Check if user profile exists."""
        return os.path.exists(self.get_user_file_path(phone_number))
    
    def create_user(self, phone_number):
        """Create a new user profile."""
        user_data = {
            'phone_number': phone_number,
            'created_at': datetime.now().isoformat(),
            'profile': {
                'name': '',
                'age': '',
                'location': '',
                'health_concern': ''
            },
            'triage_completed': False,
            'current_triage_step': 0,
            'messages': [],
            'adk_conversation_id': f"conv_{phone_number}_{int(time.time())}"
        }
        
        file_path = self.get_user_file_path(phone_number)
        with open(file_path, 'w') as f:
            json.dump(user_data, f, indent=2)
        
        return user_data
    
    def load_user(self, phone_number):
        """Load user data from JSON file."""
        file_path = self.get_user_file_path(phone_number)
        if not os.path.exists(file_path):
            return None
            
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def save_user(self, phone_number, user_data):
        """Save user data to JSON file."""
        file_path = self.get_user_file_path(phone_number)
        with open(file_path, 'w') as f:
            json.dump(user_data, f, indent=2)
    
    def add_message(self, phone_number, message_type, content, media_url=None, media_type=None, filename=None):
        """Add a message to user's message history."""
        user_data = self.load_user(phone_number)
        if not user_data:
            return
        
        message_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': message_type,  # 'text', 'image'
            'content': content,
            'media_url': media_url,
            'media_type': media_type,
            'saved_filename': filename
        }
        
        user_data['messages'].append(message_entry)
        self.save_user(phone_number, user_data)
    
    def update_triage_response(self, phone_number, response):
        """Update user profile with triage response."""
        user_data = self.load_user(phone_number)
        if not user_data:
            return None
            
        step = user_data['current_triage_step']
        
        # Store the response based on the current step
        if step == 0:  # Name
            user_data['profile']['name'] = response
        elif step == 1:  # Age
            user_data['profile']['age'] = response
        elif step == 2:  # Location
            user_data['profile']['location'] = response
        elif step == 3:  # Health concern
            user_data['profile']['health_concern'] = response
            user_data['triage_completed'] = True
        
        # Move to next step
        user_data['current_triage_step'] += 1
        
        self.save_user(phone_number, user_data)
        return user_data
    
    def get_adk_conversation_id(self, phone_number):
        """Get or create ADK conversation ID for user."""
        user_data = self.load_user(phone_number)
        if not user_data:
            return None
            
        if 'adk_conversation_id' not in user_data:
            user_data['adk_conversation_id'] = f"conv_{phone_number}_{int(time.time())}"
            self.save_user(phone_number, user_data)
            
        return user_data['adk_conversation_id']

# Initialize user manager
user_manager = UserManager()

def respond(message):
    """Create a TwiML response with the given message."""
    response = MessagingResponse()
    response.message(message)
    return str(response)

def get_clean_phone_number(sender):
    """Extract clean phone number from sender field."""
    return sender.split(':')[1] if ':' in sender else sender

async def process_with_adk_agent(phone_number, message):
    """Process message with ADK agent."""
    try:
        # Get conversation ID
        conv_id = user_manager.get_adk_conversation_id(phone_number)
        if not conv_id:
            return "Sorry, I couldn't find your conversation. Please try again."
        
        # Call the ADK agent
        response = await root_agent.chat(
            conv_id,
            message,
            tools_context={'phone_number': phone_number}
        )
        
        return response.content
        
    except Exception as e:
        print(f"ADK processing error: {e}")
        import traceback
        traceback.print_exc()
        return "I'm having trouble processing that right now. Can you try again?"

@app.route('/message', methods=['POST'])
def reply():
    """Handle incoming WhatsApp messages and images."""
    sender = request.form.get('From')
    message = request.form.get('Body', '').strip()
    media_url = request.form.get('MediaUrl0')
    media_content_type = request.form.get('MediaContentType0')
    
    print(f'{sender} sent: "{message}"')
    print(f'Media URL: {media_url}')
    print(f'Media Content Type: {media_content_type}')
    
    # Get clean phone number
    phone_number = get_clean_phone_number(sender)
    
    # Check if user exists
    if not user_manager.user_exists(sender):
        # Create new user and start triage
        print(f"New user detected: {phone_number}")
        user_manager.create_user(sender)
        return respond(TRIAGE_QUESTIONS[0])
    
    # Load existing user
    user_data = user_manager.load_user(sender)
    
    # Handle triage process
    if not user_data['triage_completed']:
        if message:  # Only process text responses during triage
            user_data = user_manager.update_triage_response(sender, message)
            
            # Add triage response to message history
            user_manager.add_message(sender, 'text', message)
            
            step = user_data['current_triage_step']
            if step < len(TRIAGE_QUESTIONS):
                # Format next question with user's name if available
                next_question = TRIAGE_QUESTIONS[step]
                if '{name}' in next_question and user_data['profile']['name']:
                    next_question = next_question.format(name=user_data['profile']['name'])
                return respond(next_question)
            else:
                # Triage completed
                name = user_data['profile']['name']
                return respond(WELCOME_MESSAGE.format(name=name))
        else:
            return respond("Please complete your profile setup by answering the question above.")
    
    # Handle regular messages after triage is complete
    if media_url:
        return handle_image_message(sender, message, media_url, media_content_type, phone_number)
    elif message:
        return handle_text_message(sender, message, phone_number)
    else:
        return respond("Hello! Send me an image or describe your health concern.")

def handle_text_message(sender, message, phone_number):
    """Handle regular text messages with ADK agent."""
    # Add message to user history
    user_manager.add_message(sender, 'text', message)
    
    # Process with ADK agent
    try:
        adk_response = asyncio.run(process_with_adk_agent(sender, message))
        return respond(adk_response)
    except Exception as e:
        print(f"Error in handle_text_message: {e}")
        return respond("I'm having trouble processing your message. Please try again.")

def handle_image_message(sender, message, media_url, media_content_type, phone_number):
    """Handle image messages."""
    try:
        # Download image with Twilio authentication
        r = requests.get(media_url, auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        r.raise_for_status()
        
        # Use filename from message, or default with timestamp
        if message:
            filename_base = message
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_base = f"health_image_{timestamp}"
        
        # Determine file extension based on Twilio's MediaContentType0
        if media_content_type == 'image/jpeg':
            filename = f'{filename_base}.jpg'
        elif media_content_type == 'image/png':
            filename = f'{filename_base}.png'
        elif media_content_type == 'image/gif':
            filename = f'{filename_base}.gif'
        else:
            return respond(f'The file type "{media_content_type}" is not supported. Please send JPEG, PNG, or GIF images.')
        
        # Create directory if it doesn't exist
        user_dir = f'uploads/{phone_number}'
        if not os.path.exists(user_dir):
            os.makedirs(user_dir, exist_ok=True)
        
        # Save the image
        full_filename = os.path.join(user_dir, filename)
        with open(full_filename, 'wb') as f:
            f.write(r.content)
        
        # Add image message to user history
        user_manager.add_message(
            sender, 
            'image', 
            message if message else 'Image received',
            media_url=media_url,
            media_type=media_content_type,
            filename=filename
        )
        
        # Get user data for personalized response
        user_data = user_manager.load_user(sender)
        name = user_data['profile']['name'] if user_data and user_data['profile']['name'] else 'there'
        
        # If there's text with the image, process it with ADK agent
        if message.strip():
            try:
                adk_response = asyncio.run(process_with_adk_agent(sender, f"Image saved: {message}"))
                return respond(f"Thank you {name}! I've received your image. {adk_response}")
            except Exception as e:
                print(f"Error processing image with ADK: {e}")
                return respond(f"Thank you {name}! I've received your image ({filename_base}). Can you describe what you're showing me?")
        else:
            return respond(f"Thank you {name}! I've received your image ({filename_base}). Can you describe what you're showing me?")
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error downloading image: {e}")
        print(f"Response content: {r.text if 'r' in locals() else 'No response'}")
        return respond('Sorry, there was an authentication error accessing your image.')
    except Exception as e:
        print(f"Error processing image: {e}")
        return respond('Sorry, there was an error processing your image.')

@app.route('/', methods=['GET'])
def index():
    """Simple index page to verify the app is running."""
    return """
    <h1>NutriMate WhatsApp Bot with ADK Agent</h1>
    <p>A health assistance service that uses Google ADK agent for intelligent conversations and receives images via WhatsApp.</p>
    <h3>Features:</h3>
    <ul>
        <li>Initial triage questionnaire for new users</li>
        <li>Google ADK agent for intelligent health conversations</li>
        <li>Image storage for health-related photos</li>
        <li>Message history tracking per patient</li>
        <li>Health-focused conversation handling</li>
    </ul>
    <p>Send a message to your configured WhatsApp number to get started!</p>
    """

if __name__ == '__main__':
    app.run(debug=True, port=5002)
