"""
Configuration file for the Mass Report Bot
Fill in your actual values below
"""

class Config:
    # Telegram API Credentials (get from https://my.telegram.org)
    API_ID = 12345678  # Your API ID (integer)
    API_HASH = "your_api_hash_here"  # Your API Hash (string)
    
    # Bot Token (get from @BotFather)
    BOT_TOKEN = "1234567890:your_bot_token_here"
    
    # SUDO Users (list of user IDs who can use the bot)
    SUDO = [
        123456789,  # Replace with your Telegram user ID
        # 987654321,  # Add more SUDO users as needed
    ]
    
    # Session Strings (get these from a session string generator)
    # You can add up to 30 session strings
    SESSION_STRING_1 = "your_session_string_1_here"
    SESSION_STRING_2 = "your_session_string_2_here"
    SESSION_STRING_3 = "your_session_string_3_here"
    # SESSION_STRING_4 = "your_session_string_4_here"
    # SESSION_STRING_5 = "your_session_string_5_here"
    # ... add more as needed up to SESSION_STRING_30
    
    # Optional: Database settings (for future use)
    # MONGO_URI = "mongodb://localhost:27017/mass_report_bot"
    
    # Optional: Logging settings
    LOG_CHANNEL = None  # Channel ID for logging (optional)
    
    # Optional: Rate limiting settings
    MAX_REPORTS_PER_SESSION = 20
    DELAY_BETWEEN_REPORTS = (10, 30)  # Random delay range in seconds
    DELAY_BETWEEN_SESSIONS = (30, 60)  # Random delay range in seconds

# Create config instance
cfg = Config()

# Validation
if not cfg.API_ID or cfg.API_ID == 12345678:
    raise ValueError("Please set your API_ID in configs.py")

if not cfg.API_HASH or cfg.API_HASH == "your_api_hash_here":
    raise ValueError("Please set your API_HASH in configs.py")

if not cfg.BOT_TOKEN or cfg.BOT_TOKEN == "1234567890:your_bot_token_here":
    raise ValueError("Please set your BOT_TOKEN in configs.py")

if not cfg.SUDO or cfg.SUDO == [123456789]:
    print("WARNING: Please set your SUDO user IDs in configs.py")

# Count valid session strings
session_count = 0
for i in range(1, 31):
    session_string = getattr(cfg, f"SESSION_STRING_{i}", None)
    if session_string and session_string.strip() and not session_string.startswith("your_session_string"):
        session_count += 1

if session_count == 0:
    print("WARNING: No valid session strings found. Please add session strings in configs.py")
else:
    print(f"Found {session_count} valid session strings")
