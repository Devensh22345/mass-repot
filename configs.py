

class Config:
    # Telegram API Credentials (get from https://my.telegram.org)
    API_ID = 22207976  # Your API ID (integer)
    API_HASH = "5c0ad7c48a86afac87630ba28b42560d"  # Your API Hash (string)
    
    # Bot Token (get from @BotFather)
    BOT_TOKEN = "6298494198:AAHgX8S02VMWFqhxeYlhFocb5Ch8qoIDmic"
    
    # SUDO Users (list of user IDs who can use the bot)
    SUDO = [
        6872968794,
        7809979684,
        1702061654,  # Replace with your Telegram user ID
        # 987654321,  # Add more SUDO users as needed
    ]
    
    # Session Strings (get these from a session string generator)
    # You can add up to 30 session strings
    SESSION_STRING_1 = "BQGn1j0AJ45_Qq4akEKy2kIumwOeXy2Ao-Cc1Gwr-vlBVbLdgJT4TxUu8LCZnvCIWO5-fTKa5tHhLGXQiWFuir20FnyFDXPPqVkFKkz350bGVDsepqzrHqkttIEVDeNr3NLFb5ypNni-VcZLCnbcdBLcmA8kpzAbQu9x8chODkkO2Gzl1PSA2YYCvJjtTsmOouO71ghHD1zS7dYQwLMCHaQW9tIUXe-3uH9jbiSAU9vTthRks3ngsdCYfdFtKPwlZC375xMlVWN3jRQX9tlcQh0O1wPQFSjoBo3gTd6_Kvxj3eHDOa97RMIOGlLjwatfkZ1vl25PHCzaGJadTsJN0d5GSQ54zgAAAAHVtSx1AA"
    SESSION_STRING_2 = "BQHHdF8AoTHiBCgurztdLMixNWwhFIwOWjTPdSyTtTTlM-rsSxbI5Kden97vv07bMGupRp3-N2B-vHmyoeDJAqVgXsD58cDYsEeCLCkI-h3wD1KUT4lt0YiukZvoYefcMpCCO9Ssj8ZKiPegfvIf2tCK-ZmvzhjxVO0crt7y_TQmc_ldDwO-4ZXzRntszBb1MS04ZKxfLeSTc-kAbZHoYc60oYWnfLWst2UfMJpLanAy6juiW9_cmhZtnnT-oR-bRX1gH7FfB-Wg2yt2vj3d30MXEBJ3mAZ4tIT7CHIXcgIr_2blBzdxNzCJtYukXKQqioJ5hYmvIb52dyRagdj5IonSI-v0kgAAAAHLkQIQAA"
    SESSION_STRING_3 = "your_session_string_3_here"
    # SESSION_STRING_4 = "your_session_string_4_here"
    # SESSION_STRING_5 = "your_session_string_5_here"
    # ... add more as needed up to SESSION_STRING_30
    
    # Optional: Database settings (for future use)
    # MONGO_URI = "mongodb+srv://mass:mass@cluster0.4nrgvz8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    # Optional: Logging settings
    LOG_CHANNEL = -1002820705251  # Channel ID for logging (optional)
    
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
