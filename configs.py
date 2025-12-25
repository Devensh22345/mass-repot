import os

class Config:
    # Basic Telegram Bot & User Client Configurations
    API_ID = int(os.getenv("API_ID", "22207976"))
    API_HASH = os.getenv("API_HASH", "5c0ad7c48a86afac87630ba28b42560d")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "7567832185:AAHSsjDbrUicZDUiYg6nTeAC66pCGZzLuXM")
   
    SESSION_STRING_2 = os.getenv("SESSION_STRING_2", "BQHmQHAAlKRIHu5J4Z0uwW8fpsOtyvglk6Oocb49Ge5MsCIrAdHR6Ne1gZ1HBS8LYZFX0wAG4V-cxEuUPNrQbuZ8Y_AmQnnIt62zvdFBGuXKjb_py5aCOz6OXCy9V3fBVn9n-Y7yFczNR9tsnQTTONQi59vXEKJa1rIrTaAh-ECG6ZxC8aE5x2d6ICeB2IGRDn7yMmMzZfkmQLpmkYD2qAQMmCjAL6FeIBF7a9PJDmkaz8AwVNXo5EoVHqwcjim-Go0qECLPKIuth3-9RIPVqm9EPz8Tw2oOjtp65i8NUAqfV_qqV5Jggb9vNn7JjR3XBz-xZ8yxlubpczIdvdD_nwyRrWMM5gAAAAH0Z0XbAA")
    SESSION_STRING_4 = os.getenv("SESSION_STRING_4", "BQHd0fgAK-C0f7zUy8DqhaEaXB0gljCqLxG3-wjNi3SQLJEsetWRR7bFs1ulw9eCFpwtssnqwQOGz3eAcZQ56oJOfIzdw_QSNhGteONx8PClscb6AKNRYhHxs0r8odmoaGW5SN-EfvxJ9fYGBgAEe61Bn7m4PKzM1uqjTqAYYsGnwDF-XYI0DEWrgeMcImgURRNnjKH37rORm7FoDTh3K_CJYMTTtYHyvN_utr7lWrhHGsghdw9b9mvMC3dTKNtvv7CsLtKpjhKkU0Y9m27wGZGVhib6NtZgLJ-I4azS1K_Bk5ODpZX_oImfF-sRtHF51RRAQ53M3ySAPeQwihr87mYxDgLQxwAAAAH0fCbLAA")
    SESSION_STRING_5 = os.getenv("SESSION_STRING_5", "BQI6zlsAq4_KbMyj4N2orGijnWr6Tjv7yrRqNAug4kM_k6zvv8nSa7xjWZAsI2ATCC4IGhoi6wBm-pcFP_Nz072LJiNRcKZwahkgi1CWeseiwbXb3hDadqOrpUtZtWSlVkgkWULTe5jSqEFMyumlv-TnS7rJnRT4-bt6UmgFbtJFnhkTEgWxKWKGk99f1eCX-vVqAnsCv46nGijJTn57JBD81m0Ks5p8_D4qBpD7_BKFZ4AP_8rDKMQRiVK6QaoSmh-E1EqU-oh2Iw8Kngz1S2MkgYtp0k8iAfKhVK06tubiw_7uZ9PNeAAm0lzaAJCqJFPgBXDnHKFXvJ2RcUULUXLrL4dWegAAAAH86vk7AA")
    SESSION_STRING_6 = os.getenv("SESSION_STRING_6", "BQI9XFoADw0azKBgY_bFjv8IXX9bL775VnBGIrDnCdr7tUl9ulCfB3xwmWuAoVCDFpYMllJ_RAcEkzZJu2DiL8gMmV9JEpVi_QakfxXSdqOr3welPvECp_9SX_D_5A6fUeljS5bj33kpIlz8AVp1jh2n2fwpODvoA1yZLXrMUcDMw19ZHA0XT7FEiXdR8BEsvxA4nbZORwJbQnMeAkd1ptYoSzla7n9_37MNbB8tINew5FoIgJ9xmjHMbNJHJIio7Gq2WSg4P-qyphdYBormkl5gErCU7lD3WN45j5WJ1KiJBZzNFtg4vW4DTAOs6WjKKDRAytBGMrqLohMP4LgFaVbn21dCsgAAAAH_IG0xAA")
    SESSION_STRING_7 = os.getenv("SESSION_STRING_7", "BQFVIMYAgm4b_DycyDIF4fBYlRXuZnAUhBiwHdtAWkB9JTWeuXwCXq3aEagL36vZ2t1dNrL2WmiH2lw8McpgAeQRFvROx-G4h-4Nn8PRJUAWjQbjCKkrqfdYTFeyhQLQJzeikTl7fEqv3VvdhAsFu3LMRcIzvcKhvLaX39OwYj7kclUWCFGxxt1-nFVpSjj0R9Wb5Fa19VkkXEuALBWi8QbfehFreQ-Wx0VqeOTnENYPV3DOBlYu7fvYeR0gPt79V1-AJMbNxfAVFDlp8ekaaOwNzTGo1JxT7oG6FnVg_yVr29cVr_-H7gotIdwOrAY44ZqEc-3PiuXuJB0fXKEjYWwb-XN7_AAAAAH8RUx_AA")
    SESSION_STRING_23 = os.getenv("SESSION_STRING_23", "BQHRShcAcenRczz6vmOQSJ-UuOZ7ZvHfitSoBo_l5B65_8HSKHiIlERdVFJ2O_CkmxSsLgymMw2YJP6RhasXYx871oxAtljnn5rh3P9V1qOQddPyABwptYNP0ZXehnxZhjtcQjyArYpGZp2xyTpCYlSjOvamcWz9vvJN0rmXYRQJUt6-UCh3xKd0W0-ERtnEbBaux0jazMUwOfG32dmPKYgsq8yghHnbDfvc0Hzoy7cti30AkqajysFqrJfn3UnTLWsS4ICJskfZOIXAiC9G5ZpS56145vBgbGWLCuhA49Xf-APEPcuo9wT-2gJ2BM-LKa8LtEsYrFJ8eQKKveSbxDaj1ZDm_QAAAAHcPBbqAA")
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
