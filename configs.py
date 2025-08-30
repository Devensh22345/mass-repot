import os

class Config:
    # Basic Telegram Bot & User Client Configurations
    API_ID = int(os.getenv("API_ID", "22207976"))
    API_HASH = os.getenv("API_HASH", "5c0ad7c48a86afac87630ba28b42560d")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "7686232626:AAFb8LoDG_Ioy-r3pGA9gfJejRm4I60HCnA")
   
    SESSION_STRING_1 = os.getenv("SESSION_STRING_1", "")
    #SESSION_STRING_2 = os.getenv("SESSION_STRING_2", "")
    SESSION_STRING_3 = os.getenv("SESSION_STRING_3", "")
    SESSION_STRING_4 = os.getenv("SESSION_STRING_4", "")
    SESSION_STRING_5 = os.getenv("SESSION_STRING_5", "")
    SESSION_STRING_6 = os.getenv("SESSION_STRING_6", "")
    SESSION_STRING_7 = os.getenv("SESSION_STRING_7", "")
    #SESSION_STRING_23 = os.getenv("SESSION_STRING_23", "")
    #SESSION_STRING_24 = os.getenv("SESSION_STRING_24", "")
    #SESSION_STRING_25 = os.getenv("SESSION_STRING_25", "")
    #SESSION_STRING_26 = os.getenv("SESSION_STRING_26", "")
    #SESSION_STRING_27 = os.getenv("SESSION_STRING_27", "")
    # Sudo Users (Admins)
    SUDO = list(map(int, os.getenv("SUDO", "6872968794").split()))

    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://Test:Test@cluster0.pcpx5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "Test")
    # Log Channel (Add your log channel ID here)
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-1002372592189"))  # Default is a placeholder

cfg = Config()
