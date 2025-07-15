import pandas as pd
import re
from datetime import datetime

def preprocess(data):
    """
    Preprocess WhatsApp chat data with robust pattern matching for various formats
    """
    
    # Multiple regex patterns to handle different WhatsApp export formats
    patterns = [
        # Pattern 1: DD/MM/YYYY, HH:MM - (24-hour format)
        r'(\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2})\s*-\s*',
        
        # Pattern 2: DD/MM/YYYY, HH:MM AM/PM - (12-hour format)
        r'(\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}\s*[APap][Mm])\s*-\s*',
        
        # Pattern 3: MM/DD/YYYY, HH:MM AM/PM - (US format)
        r'(\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}\s*[APap][Mm])\s*-\s*',
        
        # Pattern 4: DD.MM.YYYY, HH:MM - (European format with dots)
        r'(\d{1,2}\.\d{1,2}\.\d{2,4},\s*\d{1,2}:\d{2})\s*-\s*',
        
        # Pattern 5: YYYY-MM-DD, HH:MM - (ISO format)
        r'(\d{4}-\d{1,2}-\d{1,2},\s*\d{1,2}:\d{2})\s*-\s*',
        
        # Pattern 6: [DD/MM/YYYY, HH:MM:SS] (with brackets and seconds)
        r'\[(\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}:\d{2})\]\s*'
    ]
    
    messages = []
    dates = []
    used_pattern = None
    
    # Try each pattern until one works
    for i, pattern in enumerate(patterns):
        try:
            temp_messages = re.split(pattern, data)
            temp_dates = re.findall(pattern, data)
            
            # Check if we found valid data
            if len(temp_dates) > 0 and len(temp_messages) > 1:
                # Remove empty first element if exists
                if temp_messages[0] == '':
                    temp_messages = temp_messages[1:]
                
                # Ensure we have matching messages and dates
                if len(temp_messages) >= len(temp_dates):
                    messages = temp_messages[:len(temp_dates)]
                    dates = temp_dates
                    used_pattern = i
                    print(f"Successfully used pattern {i+1}")
                    break
                    
        except Exception as e:
            print(f"Pattern {i+1} failed: {str(e)}")
            continue
    
    # If no pattern worked, return empty DataFrame
    if not dates or not messages:
        print("No valid chat format detected. Showing first 500 characters of data:")
        print(data[:500])
        return pd.DataFrame(columns=[
            'user', 'message', 'date', 'only_date', 'year', 'month_num',
            'month', 'day', 'day_name', 'hour', 'minute', 'period'
        ])
    
    # Create initial DataFrame
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    
    # Parse dates based on the pattern used
    df['date'] = pd.to_datetime(df['message_date'], infer_datetime_format=True, errors='coerce')
    
    # If automatic parsing failed, try manual parsing
    if df['date'].isna().all():
        df['date'] = df['message_date'].apply(parse_date_manually)
    
    # Drop rows where date parsing failed
    df = df.dropna(subset=['date'])
    
    if df.empty:
        print("All dates failed to parse")
        return pd.DataFrame(columns=[
            'user', 'message', 'date', 'only_date', 'year', 'month_num',
            'month', 'day', 'day_name', 'hour', 'minute', 'period'
        ])
    
    # Extract users and messages
    users = []
    messages_content = []
    
    for message in df['user_message']:
        # Clean up the message
        message = message.strip()
        
        # Multiple patterns to extract user and message
        user_patterns = [
            r'^([^:]+):\s*(.*)$',  # Standard format: User: Message
            r'^([^-]+)-\s*(.*)$',  # Alternative format: User- Message
            r'^([^>]+)>\s*(.*)$',  # Another format: User> Message
        ]
        
        user_found = False
        for pattern in user_patterns:
            match = re.match(pattern, message, re.DOTALL)
            if match:
                user = match.group(1).strip()
                msg_content = match.group(2).strip()
                
                # Filter out system messages
                if not is_system_message(user):
                    users.append(user)
                    messages_content.append(msg_content)
                else:
                    users.append('group_notification')
                    messages_content.append(message)
                user_found = True
                break
        
        if not user_found:
            # If no user pattern matched, treat as group notification
            users.append('group_notification')
            messages_content.append(message)
    
    # Update DataFrame
    df['user'] = users
    df['message'] = messages_content
    df = df.drop(columns=['user_message', 'message_date'])
    
    # Extract date components
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    
    # Create time period buckets
    df['period'] = df['hour'].apply(create_time_period)
    
    # Clean up data
    df = df[df['message'].str.strip() != '']  # Remove empty messages
    df = df.reset_index(drop=True)
    
    print(f"Successfully processed {len(df)} messages from {len(df['user'].unique())} users")
    
    return df

def parse_date_manually(date_str):
    """
    Manually parse date strings that pandas couldn't handle
    """
    try:
        # Remove brackets if present
        date_str = date_str.strip('[]')
        
        # Common date formats to try
        formats = [
            '%d/%m/%Y, %H:%M',
            '%d/%m/%y, %H:%M',
            '%m/%d/%Y, %H:%M %p',
            '%m/%d/%y, %H:%M %p',
            '%d/%m/%Y, %I:%M %p',
            '%d/%m/%y, %I:%M %p',
            '%d.%m.%Y, %H:%M',
            '%d.%m.%y, %H:%M',
            '%Y-%m-%d, %H:%M',
            '%d/%m/%Y, %H:%M:%S',
            '%d/%m/%y, %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except:
                continue
        
        # If all formats fail, try pandas inference one more time
        return pd.to_datetime(date_str, infer_datetime_format=True)
        
    except:
        return pd.NaT

def is_system_message(user):
    """
    Check if a user string is actually a system message
    """
    system_indicators = [
        'You created group',
        'created group',
        'added',
        'removed',
        'left',
        'joined',
        'changed the group',
        'changed this group',
        'security code changed',
        'Messages to this group are secured',
        'This message was deleted',
        'You deleted this message',
        'image omitted',
        'video omitted',
        'audio omitted',
        'document omitted',
        'contact omitted',
        'location omitted',
        'sticker omitted',
        'gif omitted'
    ]
    
    user_lower = user.lower()
    return any(indicator in user_lower for indicator in system_indicators)

def create_time_period(hour):
    """
    Create time period buckets for activity analysis
    """
    if hour == 23:
        return "23-00"
    elif hour == 0:
        return "00-01"
    else:
        return f"{hour:02d}-{hour+1:02d}"

def debug_chat_format(data, max_lines=20):
    """
    Debug function to help identify chat format
    """
    lines = data.split('\n')[:max_lines]
    print("First few lines of the chat:")
    for i, line in enumerate(lines):
        print(f"{i+1}: {line}")
    
    # Check for common patterns
    patterns_found = []
    
    # Check for date patterns
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{2,4}',
        r'\d{1,2}\.\d{1,2}\.\d{2,4}',
        r'\d{4}-\d{1,2}-\d{1,2}',
    ]
    
    for pattern in date_patterns:
        if re.search(pattern, data):
            patterns_found.append(f"Date pattern: {pattern}")
    
    # Check for time patterns
    time_patterns = [
        r'\d{1,2}:\d{2}',
        r'\d{1,2}:\d{2}\s*[APap][Mm]',
        r'\d{1,2}:\d{2}:\d{2}',
    ]
    
    for pattern in time_patterns:
        if re.search(pattern, data):
            patterns_found.append(f"Time pattern: {pattern}")
    
    print("\nPatterns found:")
    for pattern in patterns_found:
        print(f"- {pattern}")
    
    return patterns_found

# Test function
def test_preprocessor():
    """
    Test the preprocessor with sample data
    """
    sample_data = """25/12/2023, 10:30 - John: Hello everyone!
25/12/2023, 10:31 - Jane: Hi John! How are you?
25/12/2023, 10:32 - John: I'm good, thanks for asking
25/12/2023, 10:33 - Mike: Good morning all"""
    
    df = preprocess(sample_data)
    print("Test result:")
    print(df.head())
    print(f"Shape: {df.shape}")
    print(f"Users: {df['user'].unique()}")
    
    return df

if __name__ == "__main__":
    test_preprocessor()