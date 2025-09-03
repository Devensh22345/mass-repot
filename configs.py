import os

class Config:
    # Basic Telegram Bot & User Client Configurations
    API_ID = int(os.getenv("API_ID", "22207976"))
    API_HASH = os.getenv("API_HASH", "5c0ad7c48a86afac87630ba28b42560d")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "7567832185:AAErNpedjqTPpYJ_NjFEOb42EFJyfSeKjpw")
   
    SESSION_STRING_1 = os.getenv("SESSION_STRING_1", "BQGn1j0AJ45_Qq4akEKy2kIumwOeXy2Ao-Cc1Gwr-vlBVbLdgJT4TxUu8LCZnvCIWO5-fTKa5tHhLGXQiWFuir20FnyFDXPPqVkFKkz350bGVDsepqzrHqkttIEVDeNr3NLFb5ypNni-VcZLCnbcdBLcmA8kpzAbQu9x8chODkkO2Gzl1PSA2YYCvJjtTsmOouO71ghHD1zS7dYQwLMCHaQW9tIUXe-3uH9jbiSAU9vTthRks3ngsdCYfdFtKPwlZC375xMlVWN3jRQX9tlcQh0O1wPQFSjoBo3gTd6_Kvxj3eHDOa97RMIOGlLjwatfkZ1vl25PHCzaGJadTsJN0d5GSQ54zgAAAAHVtSx1AA")
    #SESSION_STRING_2 = os.getenv("SESSION_STRING_2", "")
    SESSION_STRING_3 = os.getenv("SESSION_STRING_3", "BQHHdF8AoTHiBCgurztdLMixNWwhFIwOWjTPdSyTtTTlM-rsSxbI5Kden97vv07bMGupRp3-N2B-vHmyoeDJAqVgXsD58cDYsEeCLCkI-h3wD1KUT4lt0YiukZvoYefcMpCCO9Ssj8ZKiPegfvIf2tCK-ZmvzhjxVO0crt7y_TQmc_ldDwO-4ZXzRntszBb1MS04ZKxfLeSTc-kAbZHoYc60oYWnfLWst2UfMJpLanAy6juiW9_cmhZtnnT-oR-bRX1gH7FfB-Wg2yt2vj3d30MXEBJ3mAZ4tIT7CHIXcgIr_2blBzdxNzCJtYukXKQqioJ5hYmvIb52dyRagdj5IonSI-v0kgAAAAHLkQIQAA")
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
