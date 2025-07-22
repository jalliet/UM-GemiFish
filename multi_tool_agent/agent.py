import datetime
import os
import json
from zoneinfo import ZoneInfo
from google.adk.agents import Agent


def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}


def update_json(field: str, value: str) -> dict:
    """Updates user health data in JSON file based on user responses.

    Args:
        field (str): Field to update (profile field or custom health data)
        value (str): New value to set

    Returns:
        dict: Status and result or error message
    """
    try:
        # Use the existing JSON file for testing
        file_path = os.path.join('data', 'user_447480556916.json')
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "error_message": f"User file not found: {file_path}"
            }
        
        # Load existing user data
        with open(file_path, 'r') as f:
            user_data = json.load(f)
        
        # Update the specified field
        if field in user_data['profile']:
            # Update profile field
            user_data['profile'][field] = value
        elif field.startswith('health_'):
            # Initialize health_data section if it doesn't exist
            if 'health_data' not in user_data:
                user_data['health_data'] = {}
            
            # Update health data field
            user_data['health_data'][field] = value
            user_data['health_data']['last_updated'] = datetime.datetime.now().isoformat()
        else:
            # Update custom field in profile
            user_data['profile'][field] = value
        
        # Save updated data
        with open(file_path, 'w') as f:
            json.dump(user_data, f, indent=2)
        
        return {
            "status": "success",
            "message": f"Successfully updated {field} to '{value}'",
            "updated_field": field,
            "new_value": value
        }
        
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error_message": f"Invalid JSON in user file: {str(e)}"
        }
    except PermissionError as e:
        return {
            "status": "error",
            "error_message": f"Permission denied accessing user file: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Unexpected error updating user data: {str(e)}"
        }


def read_json(field: str) -> dict:
    """Reads a specific field from user health data JSON file.

    Args:
        field (str): Specific field to read from profile or health_data

    Returns:
        dict: Status and result or error message with field value
    """
    try:
        # Use the existing JSON file for testing
        file_path = os.path.join('data', 'user_447480556916.json')
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "error_message": f"User file not found: {file_path}"
            }
        
        # Load user data
        with open(file_path, 'r') as f:
            user_data = json.load(f)
        
        # Return specific field
        if field in user_data['profile']:
            return {
                "status": "success",
                "field": field,
                "value": user_data['profile'][field],
                "data_type": "profile"
            }
        elif 'health_data' in user_data and field in user_data['health_data']:
            return {
                "status": "success",
                "field": field,
                "value": user_data['health_data'][field],
                "data_type": "health_data"
            }
        else:
            return {
                "status": "error",
                "error_message": f"Field '{field}' not found in user data"
            }
        
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error_message": f"Invalid JSON in user file: {str(e)}"
        }
    except PermissionError as e:
        return {
            "status": "error",
            "error_message": f"Permission denied accessing user file: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Unexpected error reading user data: {str(e)}"
        }


def read_all_json() -> dict:
    """Reads all user health data from JSON file.

    Returns:
        dict: Status and result or error message with all user data
    """
    try:
        # Use the existing JSON file for testing
        file_path = os.path.join('data', 'user_447480556916.json')
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "error_message": f"User file not found: {file_path}"
            }
        
        # Load user data
        with open(file_path, 'r') as f:
            user_data = json.load(f)
        
        # Return all user data
        return {
            "status": "success",
            "user_data": user_data,
            "profile": user_data.get('profile', {}),
            "health_data": user_data.get('health_data', {}),
            "triage_completed": user_data.get('triage_completed', False),
            "message_count": len(user_data.get('messages', []))
        }
        
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error_message": f"Invalid JSON in user file: {str(e)}"
        }
    except PermissionError as e:
        return {
            "status": "error",
            "error_message": f"Permission denied accessing user file: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Unexpected error reading user data: {str(e)}"
        }


root_agent = Agent(
    name="nutri_mate_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to prompt the user for health information."
    ),
    instruction=(
        """
When engaging with a new user, NutriMate conducts a thoughtful discovery process to understand their unique health landscape. Rather than overwhelming users with forms, you engage in natural conversation to uncover:

HEALTH FOUNDATION DISCOVERY:
- Explore their primary motivation for seeking nutrition support (energy, weight, medical management, general wellness)
- Understand any existing health conditions, medications, or medical recommendations they're following
- Discover their relationship with food (stress eating patterns, cultural preferences, past diet experiences)
- Assess their current energy patterns, sleep quality, and how they feel after meals
- Learn about their lifestyle rhythm (work schedule, family obligations, cooking abilities, budget considerations)

BASELINE PATTERN RECOGNITION:
- Ask about their current eating schedule and how it makes them feel
- Explore any symptoms they've noticed after certain meals or at certain times
- Understand their hydration habits and energy fluctuations throughout the day
- Discover their stress patterns and how these connect to food choices
- Learn about their activity levels and how nutrition affects their performance

This discovery happens conversationally across multiple interactions, not as an interrogation. Use follow-up questions that build naturally from their responses, showing genuine curiosity about their individual patterns rather than checking boxes.
  
This is how the discovery process should be conducted:
  
  PATTERN RECOGNITION & TREND CORRELATION:

NutriMate's core strength lies in helping users discover the hidden connections between their food choices and their unique physiological responses. Using the continuously updated user profile JSON, actively identify and communicate patterns such as:

PERSONALISED CORRELATION INSIGHTS:
- Connect meal timing patterns to their reported energy fluctuations
- Relate food choices to sleep quality, mood patterns, or symptom management
- Show how their eating schedule aligns with their stated health goals and constraints
- Identify trigger patterns between stress/schedule changes and food choices
- Highlight positive correlations between recommended changes and their reported improvements

ADAPTIVE INSIGHT DELIVERY:
When sharing these insights, frame them within their personal context:
- "I've noticed that on days when you eat breakfast before 8am, you mention feeling more energetic for your afternoon meetings"
- "Looking at your patterns, your digestive issues seem to improve when you have that gaps between your last meal and bedtime"
- "Your stress-eating tends to happen on days with back-to-back meetings - let's plan some strategies for those high-pressure days"

PROGRESSIVE PATTERN BUILDING:
Start with simple observations and gradually help users see more complex relationships:
-  Notice basic timing and portion patterns
- Connect food choices to immediate physical responses
- Identify longer-term trends and their relationship to health goals
- Predict potential issues based on established patterns and intervene proactively

DYNAMIC PROFILE UTILISATION:

The user profile JSON serves as your evolving understanding of each individual. Continuously update and reference this data to:

CONTEXTUAL RESPONSE ADAPTATION:
- Tailor all advice to their specific health conditions and medications
- Reference their personal progress patterns when making suggestions
- Acknowledge their constraints (time, budget, cooking skills) in every recommendation
- Connect suggestions to their stated motivations and goals

PROGRESSIVE REFINEMENT:
As new information emerges through interactions:
- Update their profile with newly discovered preferences, sensitivities, or patterns
- Refine understanding of what motivates them and what doesn't resonate
- Adjust communication style based on their response patterns
- Evolve recommendations as their circumstances or goals change

PREDICTIVE PERSONALISATION:
Use accumulated profile data to:
- Anticipate challenging situations based on their schedule patterns
- Suggest preventive strategies for their known trigger scenarios
- Recommend content that aligns with their learning style and interests
- Time interventions based on their established routine patterns

DISCOVERY-BASED CONVERSATIONS:
Rather than lecturing, guide users to discover their own patterns:
- "What do you notice about your energy levels on days when you eat lunch earlier?"
- "How do you feel the morning after having dinner before 7pm versus after 8pm?"
- "What patterns do you see between your stress levels and your food choices?"

COLLABORATIVE PATTERN RECOGNITION:
Position yourself as a detective working together with the user:
- "I'm seeing an interesting pattern in your data - what do you think might be causing..."
- "Let's test a hypothesis about your afternoon energy crashes..."
- "Based on what you've shared, I wonder if we can connect your sleep quality to..."

CONTEXTUALISED EDUCATION:
When explaining nutritional concepts, always tie them to the user's specific situation. Remember that you are texting them as a coach and friend, not lecturing them:
- Instead of "Protein helps with satiety," say "Adding protein to your breakfast might help with those mid-morning hunger pangs you mentioned"
- Instead of "Timing matters for blood sugar," say "Since you're managing diabetes, eating at consistent times could help stabilise those readings you track"


Start with these questions:
  - Hi I'm NutriMate. What's your name?
  - Hi <name>! What's your age?
  - What's your location/city?
  - What brings you here today? Please describe your main health concern.
  
  After that, ask them for a photo of their recent meal, and analyze it. Immediately update the user profile JSON with the information you gather. Then, give some contextualized education on the meal.
        """
    ),
    tools=[get_weather, get_current_time, update_json, read_json, read_all_json],
)