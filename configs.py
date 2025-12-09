import os

class Config:
    # Basic Telegram Bot & User Client Configurations
    API_ID = int(os.getenv("API_ID", "22207976"))
    API_HASH = os.getenv("API_HASH", "5c0ad7c48a86afac87630ba28b42560d")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "7567832185:AAErNpedjqTPpYJ_NjFEOb42EFJyfSeKjpw")
   
    SESSION_STRING_1 = os.getenv("SESSION_STRING_1", "BQI9RncAmhZC2VN5gDyUTBLytD3xo8CvZneZm2SEelQtc8C0l40sVqQ7TS9vEoavmy_zlEOLk76iFLFCPGMthErSnMdTDNF7ViGnFcOm5EXiAettQT0l6okMq0UmgWoK_hf6hoDOR8z3D713Vb72iajyNhSVbz4UodgJhdpTWr9Rumbk41tqjebg3yWkoV083O8CYXk-8ghDiGqCUclvkOs3nI44PBkRKavf0gGaKFGSLcY5EL78q97tZx2d2_JOnhuC67llvdSxQjIMhUTcDAFn1620UFfwyPV-_L5jHKCMTv7Lt0KehgJGT8OYsoBFGwdelp0UqO9DUhhkVpNEYGBDe7CgQAAAAAH7Y19bAA")
    #SESSION_STRING_2 = os.getenv("SESSION_STRING_2", "")
    #SESSION_STRING_3 = os.getenv("SESSION_STRING_3", "BQHHdF8AoTHiBCgurztdLMixNWwhFIwOWjTPdSyTtTTlM-rsSxbI5Kden97vv07bMGupRp3-N2B-vHmyoeDJAqVgXsD58cDYsEeCLCkI-h3wD1KUT4lt0YiukZvoYefcMpCCO9Ssj8ZKiPegfvIf2tCK-ZmvzhjxVO0crt7y_TQmc_ldDwO-4ZXzRntszBb1MS04ZKxfLeSTc-kAbZHoYc60oYWnfLWst2UfMJpLanAy6juiW9_cmhZtnnT-oR-bRX1gH7FfB-Wg2yt2vj3d30MXEBJ3mAZ4tIT7CHIXcgIr_2blBzdxNzCJtYukXKQqioJ5hYmvIb52dyRagdj5IonSI-v0kgAAAAHLkQIQAA")
    #SESSION_STRING_4 = os.getenv("SESSION_STRING_4", "")
    #SESSION_STRING_5 = os.getenv("SESSION_STRING_5", "")
    #SESSION_STRING_6 = os.getenv("SESSION_STRING_6", "")
    #SESSION_STRING_7 = os.getenv("SESSION_STRING_7", "")
    #SESSION_STRING_23 = os.getenv("SESSION_STRING_23", "")
    #SESSION_STRING_24 = os.getenv("SESSION_STRING_24", "")
    #SESSION_STRING_25 = os.getenv("SESSION_STRING_25", "")
    #SESSION_STRING_26 = os.getenv("SESSION_STRING_26", "")
    #SESSION_STRING_27 = os.getenv("SESSION_STRING_27", "")
    # Sudo Users (Admins)
    SUDO = list(map(int, os.getenv("SUDO", "6872968794,7809979684,1702061654").split(",")))


    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://mass:mass@cluster0.4nrgvz8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "Test")
    # Log Channel (Add your log channel ID here)
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-1002820705251"))  # Default is a placeholder

cfg = Config()
