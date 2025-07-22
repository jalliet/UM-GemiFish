#!/usr/bin/env python3
"""
Admin tool for UM-GemiFish user management
"""

import os
import json
import argparse
from datetime import datetime

def list_users():
    """List all users."""
    data_dir = 'data'
    if not os.path.exists(data_dir):
        print("No users found. Data directory doesn't exist.")
        return
    
    users = []
    for filename in os.listdir(data_dir):
        if filename.startswith('user_') and filename.endswith('.json'):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, 'r') as f:
                user_data = json.load(f)
            users.append(user_data)
    
    if not users:
        print("No users found.")
        return
    
    print(f"\n{'Phone':<20} {'Name':<15} {'Age':<5} {'Location':<15} {'Triage':<8} {'Messages':<8}")
    print("-" * 80)
    
    for user in users:
        phone = user['phone_number'].replace('whatsapp:', '')
        name = user['profile']['name'] or 'N/A'
        age = user['profile']['age'] or 'N/A'
        location = user['profile']['location'] or 'N/A'
        triage = "✅" if user['triage_completed'] else "❌"
        msg_count = len(user['messages'])
        
        print(f"{phone:<20} {name:<15} {age:<5} {location:<15} {triage:<8} {msg_count:<8}")

def view_user(phone):
    """View detailed user information."""
    if not phone.startswith('whatsapp:'):
        phone = f'whatsapp:+{phone}'
    
    clean_number = phone.replace('+', '').replace(':', '')
    filepath = os.path.join('data', f'user_{clean_number}.json')
    
    if not os.path.exists(filepath):
        print(f"User not found: {phone}")
        return
    
    with open(filepath, 'r') as f:
        user_data = json.load(f)
    
    print(f"\n=== User Details ===")
    print(f"Phone: {user_data['phone_number']}")
    print(f"Name: {user_data['profile']['name']}")
    print(f"Age: {user_data['profile']['age']}")
    print(f"Location: {user_data['profile']['location']}")
    print(f"Fishing Type: {user_data['profile']['fishing_type']}")
    print(f"Created: {user_data['created_at']}")
    print(f"Triage Complete: {'Yes' if user_data['triage_completed'] else 'No'}")
    
    print(f"\n=== Message History ({len(user_data['messages'])} messages) ===")
    for i, msg in enumerate(user_data['messages'], 1):
        print(f"{i}. [{msg['timestamp']}] {msg['type'].upper()}: {msg['content']}")
        if msg['type'] == 'image' and msg.get('saved_filename'):
            print(f"   File: {msg['saved_filename']}")

def delete_user(phone):
    """Delete a user."""
    if not phone.startswith('whatsapp:'):
        phone = f'whatsapp:+{phone}'
    
    clean_number = phone.replace('+', '').replace(':', '')
    filepath = os.path.join('data', f'user_{clean_number}.json')
    
    if not os.path.exists(filepath):
        print(f"User not found: {phone}")
        return
    
    # Also delete their uploads directory
    clean_phone = phone.replace('whatsapp:', '').replace('+', '')
    uploads_dir = os.path.join('uploads', clean_phone)
    
    confirm = input(f"Are you sure you want to delete user {phone}? (y/N): ")
    if confirm.lower() == 'y':
        os.remove(filepath)
        if os.path.exists(uploads_dir):
            import shutil
            shutil.rmtree(uploads_dir)
        print(f"User {phone} deleted successfully.")
    else:
        print("Deletion cancelled.")

def reset_triage(phone):
    """Reset user's triage process."""
    if not phone.startswith('whatsapp:'):
        phone = f'whatsapp:+{phone}'
    
    clean_number = phone.replace('+', '').replace(':', '')
    filepath = os.path.join('data', f'user_{clean_number}.json')
    
    if not os.path.exists(filepath):
        print(f"User not found: {phone}")
        return
    
    with open(filepath, 'r') as f:
        user_data = json.load(f)
    
    user_data['triage_completed'] = False
    user_data['current_triage_step'] = 0
    user_data['profile'] = {'name': '', 'age': '', 'location': '', 'fishing_type': ''}
    
    with open(filepath, 'w') as f:
        json.dump(user_data, f, indent=2)
    
    print(f"Triage reset for user {phone}")

def main():
    parser = argparse.ArgumentParser(description='UM-GemiFish Admin Tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List users
    subparsers.add_parser('list', help='List all users')
    
    # View user
    view_parser = subparsers.add_parser('view', help='View user details')
    view_parser.add_argument('phone', help='Phone number (with or without whatsapp: prefix)')
    
    # Delete user
    delete_parser = subparsers.add_parser('delete', help='Delete a user')
    delete_parser.add_argument('phone', help='Phone number (with or without whatsapp: prefix)')
    
    # Reset triage
    reset_parser = subparsers.add_parser('reset-triage', help='Reset user triage process')
    reset_parser.add_argument('phone', help='Phone number (with or without whatsapp: prefix)')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_users()
    elif args.command == 'view':
        view_user(args.phone)
    elif args.command == 'delete':
        delete_user(args.phone)
    elif args.command == 'reset-triage':
        reset_triage(args.phone)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
