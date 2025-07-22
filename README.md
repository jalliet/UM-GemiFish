# UM-GemiFish

A Flask application that receives and saves images sent via WhatsApp using the Twilio WhatsApp Business API.

## Features

- Receive images sent via WhatsApp
- Automatically save images to organized folders by user
- Support for JPEG, PNG, and GIF image formats
- TwiML responses to acknowledge receipt
- Simple web interface for monitoring

## Prerequisites

- Python 3.6 or newer
- A Twilio account with WhatsApp sandbox access
- ngrok for local development tunneling

## Setup Instructions

### 1. Install Dependencies

First, activate your virtual environment and install the required packages:

```bash
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

pip install -r requirements.txt
```

### 2. Configure Environment Variables

Make sure your `.env` file contains the necessary Twilio credentials:

```env
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
```

### 3. Set Up Twilio WhatsApp Sandbox

1. Go to your [Twilio Console](https://www.twilio.com/console)
2. Navigate to Messaging > Try it Out > WhatsApp
3. Follow the instructions to join the WhatsApp sandbox by sending the join code to the provided number

### 4. Run the Application

Start the Flask development server:

```bash
flask run
```

The application will run on `http://localhost:5000`

### 5. Set Up ngrok Tunnel

In a separate terminal, start ngrok to make your local server accessible:

```bash
ngrok http 5000
```

Copy the forwarding URL (e.g., `https://abc123.ngrok.io`)

### 6. Configure Twilio Webhook

1. Go to [WhatsApp Sandbox Settings](https://www.twilio.com/console/sms/whatsapp/sandbox)
2. In the "When a message comes in" field, enter your ngrok URL followed by `/message`
   - Example: `https://abc123.ngrok.io/message`
3. Make sure the HTTP method is set to "POST"
4. Click "Save"

## Usage

1. Send a WhatsApp message with an image to your Twilio sandbox number
2. Include a text message that will be used as the filename
3. The application will:
   - Download the image
   - Save it in `uploads/{phone_number}/{message_text}.{extension}`
   - Send a confirmation message back to WhatsApp

## File Structure

```
UM-GemiFish/
├── app.py              # Main Flask application
├── .flaskenv           # Flask environment configuration
├── requirements.txt    # Python dependencies
├── .env               # Twilio credentials (not in git)
├── uploads/           # Directory for saved images
│   └── {phone_number}/
│       └── {filename}.{ext}
└── README.md          # This file
```

## Supported Image Formats

- JPEG (.jpg)
- PNG (.png)
- GIF (.gif)

## API Endpoints

- `GET /` - Simple status page
- `POST /message` - WhatsApp webhook endpoint for receiving messages

## Development

### Local Testing

1. Ensure Flask and ngrok are running
2. Send test messages to your WhatsApp sandbox number
3. Check the `uploads/` directory for saved images
4. Monitor the Flask console for debug output

### Environment Variables

The application uses the following environment variables:

- `FLASK_APP` - Set to `app.py` (configured in `.flaskenv`)
- `FLASK_ENV` - Set to `development` for debug mode (configured in `.flaskenv`)
- `TWILIO_ACCOUNT_SID` - Your Twilio Account SID (in `.env`)
- `TWILIO_AUTH_TOKEN` - Your Twilio Auth Token (in `.env`)

## Troubleshooting

### Common Issues

1. **Images not saving**: Check that the `uploads/` directory exists and has write permissions
2. **Webhook not receiving messages**: Verify your ngrok URL is correctly configured in Twilio console
3. **Unsupported file type**: Only JPEG, PNG, and GIF images are supported

### Debug Output

The application prints debug information to the console:
- Sender phone number and message content
- Any errors during image processing

## Next Steps

Consider extending this application with:
- Database storage for image metadata
- User authentication and management
- Image processing and analysis
- Integration with cloud storage services
- Support for additional file types

## License

This project is for educational purposes and follows the Twilio tutorial implementation.