import os
import requests
from dotenv import load_dotenv
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from requests.auth import HTTPBasicAuth

load_dotenv()

app = Flask(__name__)

# Get Twilio credentials from environment
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

def respond(message):
    """Create a TwiML response with the given message."""
    response = MessagingResponse()
    response.message(message)
    return str(response)

@app.route('/message', methods=['POST'])
def reply():
    """Handle incoming WhatsApp messages and images."""
    sender = request.form.get('From')
    message = request.form.get('Body')
    media_url = request.form.get('MediaUrl0')
    media_content_type = request.form.get('MediaContentType0')
    
    print(f'{sender} sent {message}')
    print(f'Media URL: {media_url}')
    print(f'Media Content Type: {media_content_type}')
    
    if media_url:
        # Download and save the image
        try:
            # Download image with Twilio authentication
            r = requests.get(media_url, auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
            r.raise_for_status()  # Raise an exception for bad status codes
            
            # Extract phone number from sender (remove whatsapp: prefix)
            username = sender.split(':')[1] if ':' in sender else sender
            
            # Use filename from message, or default if empty
            filename_base = message if message and message.strip() else 'image'
            
            # Determine file extension based on Twilio's MediaContentType0
            if media_content_type == 'image/jpeg':
                filename = f'uploads/{username}/{filename_base}.jpg'
            elif media_content_type == 'image/png':
                filename = f'uploads/{username}/{filename_base}.png'
            elif media_content_type == 'image/gif':
                filename = f'uploads/{username}/{filename_base}.gif'
            else:
                return respond(f'The file type "{media_content_type}" is not supported. Please send JPEG, PNG, or GIF images.')
            
            # Create directory if it doesn't exist
            user_dir = f'uploads/{username}'
            if not os.path.exists(user_dir):
                os.makedirs(user_dir, exist_ok=True)
            
            # Save the image
            with open(filename, 'wb') as f:
                f.write(r.content)
            
            return respond(f'Thank you! Your image was saved as {filename_base} successfully.')
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error downloading image: {e}")
            print(f"Response content: {r.text if 'r' in locals() else 'No response'}")
            return respond('Sorry, there was an authentication error accessing your image.')
        except Exception as e:
            print(f"Error processing image: {e}")
            return respond('Sorry, there was an error processing your image.')
    else:
        return respond('Please send an image!')

@app.route('/', methods=['GET'])
def index():
    """Simple index page to verify the app is running."""
    return """
    <h1>WhatsApp Image Receiver</h1>
    <p>This is a Flask application that receives images sent via WhatsApp using Twilio.</p>
    <p>Send a message with an image to your configured WhatsApp number to test the service.</p>
    """

if __name__ == '__main__':
    app.run(debug=True, port=5002)
