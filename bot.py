import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.raw import functions, types
from pyrogram.errors import FloodWait, PeerIdInvalid, UsernameInvalid, UsernameNotOccupied, SessionPasswordNeeded
import asyncio
import random
import time
import logging
from configs import cfg

# Setup logging for Heroku
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot client - DEBUG VERSION
app = Client(
    "bot", 
    api_id=cfg.API_ID, 
    api_hash=cfg.API_HASH, 
    bot_token=cfg.BOT_TOKEN
)

session_clients = {}
active_reports = {}
report_data = {}

# Initialize sessions for Heroku
async def initialize_sessions():
    """Initialize sessions for Heroku"""
    for i in range(1, 31):
        session_key = f"session{i}"
        session_string = getattr(cfg, f"SESSION_STRING_{i}", None)
        if session_string and session_string.strip() and not session_string.startswith("your_session_string"):
            try:
                client = Client(
                    session_key,
                    api_id=cfg.API_ID,
                    api_hash=cfg.API_HASH,
                    session_string=session_string
                )
                session_clients[session_key] = client
                logger.info(f"Initialized {session_key}")
            except Exception as e:
                logger.error(f"Failed to initialize {session_key}: {e}")

# DEBUG: Log all incoming messages
@app.on_message()
async def debug_all_messages(client: Client, message: Message):
    """Debug handler to log all incoming messages"""
    try:
        user_id = message.from_user.id if message.from_user else "None"
        username = message.from_user.username if message.from_user else "None"
        text = message.text if message.text else "No text"
        
        logger.info(f"📨 Received message: User {user_id} (@{username}): {text}")
        print(f"📨 Message from {user_id}: {text}")
        
    except Exception as e:
        logger.error(f"Error in debug handler: {e}")

# ---------- Helper Functions ----------
async def log_to_user(user_id: int, text: str):
    """Send log message to user with error handling"""
    try:
        logger.info(f"Sending to user {user_id}: {text}")
        await app.send_message(user_id, text)
        logger.info(f"✅ Message sent to {user_id}")
    except FloodWait as e:
        logger.warning(f"FloodWait in log_to_user: {e.value} seconds")
        await asyncio.sleep(e.value)
        try:
            await app.send_message(user_id, text)
        except Exception as retry_error:
            logger.error(f"Failed to send log after retry: {retry_error}")
    except Exception as e:
        logger.error(f"Log DM failed: {e}")

def is_valid_target(target: str) -> bool:
    """Validate target username or ID"""
    if not target:
        return False
    # Username format: @username
    if target.startswith('@') and len(target) > 1:
        return True
    # Numeric ID format: -1001234567890 or 1234567890
    if target.lstrip('-').isdigit():
        return True
    return False

# ---------- Command Handlers ----------
@app.on_message(filters.command("start") & filters.private)
async def start_message(client: Client, message: Message):
    """Handle /start command"""
    try:
        logger.info(f"🚀 START command from user {message.from_user.id}")
        
        txt = (
            "👋 **Hello! Bot is working!**\n\n"
            "📋 **Available Commands:**\n"
            "• `/start` → Show this message\n"
            "• `/test` → Test bot functionality\n"
            "• `/ping` → Simple ping test\n"
            "• `/report` → Start reporting (SUDO only)\n"
            "• `/status` → Check status (SUDO only)\n\n"
            "🟢 **Status:** Online and responding!\n"
            f"🆔 **Your ID:** `{message.from_user.id}`"
        )
        
        await message.reply_text(txt)
        logger.info(f"✅ START response sent to {message.from_user.id}")
        
        # Check SUDO status
        if message.from_user.id in cfg.SUDO:
            await message.reply_text("🔓 **You are authorized** to use all commands!")
            logger.info(f"User {message.from_user.id} is SUDO")
        else:
            await message.reply_text("🔒 You have **basic access**. Contact admin for full access.")
            logger.info(f"User {message.from_user.id} is NOT SUDO")
        
    except Exception as e:
        logger.error(f"Error in start_message: {e}")
        try:
            await message.reply_text("❌ An error occurred. Please try again.")
        except:
            pass

@app.on_message(filters.command("ping") & filters.private)
async def ping_message(client: Client, message: Message):
    """Simple ping test"""
    try:
        logger.info(f"🏓 PING from user {message.from_user.id}")
        await message.reply_text("🏓 **Pong!** Bot is alive and responding!")
        logger.info(f"✅ PONG sent to {message.from_user.id}")
    except Exception as e:
        logger.error(f"Error in ping: {e}")

@app.on_message(filters.command("test") & filters.private)
async def test_message(client: Client, message: Message):
    """Test command with detailed info"""
    try:
        logger.info(f"🧪 TEST command from user {message.from_user.id}")
        
        response = (
            f"🤖 **Bot Test Results:**\n\n"
            f"✅ **Status:** Responding normally\n"
            f"👤 **Your ID:** `{message.from_user.id}`\n"
            f"👤 **Your Username:** @{message.from_user.username or 'None'}\n"
            f"📱 **Sessions loaded:** {len(session_clients)}\n"
            f"🔐 **SUDO status:** {'✅ Authorized' if message.from_user.id in cfg.SUDO else '❌ Not authorized'}\n"
            f"🌐 **Platform:** Heroku\n"
            f"⏰ **Current time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"🆔 **Bot ID:** {(await app.get_me()).id}\n"
            f"📊 **SUDO users:** {len(cfg.SUDO)}"
        )
        
        await message.reply_text(response)
        logger.info(f"✅ TEST response sent to {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in test_message: {e}")
        try:
            await message.reply_text("❌ Test failed. Check logs.")
        except:
            pass

@app.on_message(filters.command("status") & filters.private)
async def status_message(client: Client, message: Message):
    """Handle /status command"""
    try:
        logger.info(f"📊 STATUS command from user {message.from_user.id}")
        
        if message.from_user.id not in cfg.SUDO:
            await message.reply_text("❌ Only sudo users can use this command.")
            return
            
        active_sessions = len(session_clients)
        active_reports_count = len(active_reports)
        
        status_text = (
            f"🤖 **Bot Status Report**\n\n"
            f"📱 **Sessions loaded:** {active_sessions}\n"
            f"📊 **Active reports:** {active_reports_count}\n"
            f"👥 **SUDO users:** {len(cfg.SUDO)}\n"
            f"💾 **Report data entries:** {len(report_data)}\n"
            f"🕐 **Uptime:** Running normally\n\n"
            f"✅ **All systems operational**"
        )
        await message.reply_text(status_text)
        logger.info(f"✅ STATUS sent to {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in status_message: {e}")

@app.on_message(filters.command("report") & filters.private)
async def report_command(client, message: Message):
    """Handle /report command"""
    try:
        logger.info(f"📝 REPORT command from user {message.from_user.id}")
        
        if message.from_user.id not in cfg.SUDO:
            await message.reply_text("❌ Only sudo users can use this command.")
            logger.info(f"User {message.from_user.id} not in SUDO list")
            return

        # Check if user already has an active report
        if message.from_user.id in active_reports:
            await message.reply_text("❌ You already have an active reporting task. Use `/stopreport` to cancel it first.")
            return

        if not session_clients:
            await message.reply_text("❌ No active sessions available. Please check configuration.")
            return

        report_data[message.from_user.id] = {"started_at": time.time()}
        await message.reply_text(
            "✍️ **Send the target details:**\n\n"
            "Format examples:\n"
            "• `@username` (for public channels/groups)\n"
            "• `@botusername` (for bots)\n"
            "• `-1001234567890` (for private groups with ID)"
        )
        report_data[message.from_user.id]["step"] = "username"
        logger.info(f"Report flow started for user {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in report_command: {e}")
        try:
            await message.reply_text("❌ An error occurred. Please try again.")
        except:
            pass

@app.on_message(filters.command("stopreport") & filters.private)
async def stop_report_command(client, message: Message):
    """Handle /stopreport command"""
    try:
        logger.info(f"🛑 STOPREPORT command from user {message.from_user.id}")
        
        user_id = message.from_user.id
        if user_id not in active_reports:
            await message.reply_text("❌ You don't have any active reporting tasks.")
            return
        
        # Cancel the reporting task
        task = active_reports[user_id]
        task.cancel()
        del active_reports[user_id]
        
        # Clean up report data
        if user_id in report_data:
            del report_data[user_id]
        
        await message.reply_text("✅ Reporting task cancelled successfully.")
        logger.info(f"Report cancelled for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in stop_report_command: {e}")

# ---------- Text Input Handler ----------
@app.on_message(filters.text & filters.private & ~filters.command(["report", "start", "stopreport", "status", "test", "ping"]))
async def handle_text_reply(client: Client, message: Message):
    """Handle text input during reporting flow"""
    try:
        user_id = message.from_user.id
        logger.info(f"💬 Text message from {user_id}: {message.text}")
        
        if user_id not in report_data or "step" not in report_data[user_id]:
            # Not in reporting flow, just acknowledge
            await message.reply_text("👋 I received your message! Use /start to see available commands.")
            return

        step = report_data[user_id]["step"]
        logger.info(f"User {user_id} in step: {step}")

        # Step: username
        if step == "username":
            target = message.text.strip()
            
            if not is_valid_target(target):
                await message.reply_text(
                    "❌ **Invalid format!**\n\n"
                    "Please provide:\n"
                    "• Username: `@channel_name`\n"
                    "• Bot username: `@bot_name`\n"
                    "• Group ID: `-1001234567890`"
                )
                return
                
            report_data[user_id]["username"] = target
            report_data[user_id]["step"] = "count"
            await message.reply_text(
                "🔢 **How many reports per session?**\n\n"
                "Recommended: 1-5 (to avoid rate limits)\n"
                "Maximum: 20"
            )
            logger.info(f"User {user_id} set target: {target}")
            return

        # Step: count
        elif step == "count":
            try:
                count = int(message.text.strip())
                if count <= 0:
                    await message.reply_text("❌ Number must be positive. Please enter a valid number.")
                    return
                if count > 20:
                    await message.reply_text("⚠️ Maximum 20 reports per session. Setting to 20.")
                    count = 20
                    
                report_data[user_id]["count"] = count
                report_data[user_id]["step"] = "reason"
                
                buttons = [
                    [InlineKeyboardButton("🚫 Spam", callback_data="reason_spam")],
                    [InlineKeyboardButton("👶 Child Abuse", callback_data="reason_child")],
                    [InlineKeyboardButton("🔪 Violence", callback_data="reason_violence")],
                    [InlineKeyboardButton("🔞 Pornography", callback_data="reason_porn")],
                    [InlineKeyboardButton("💿 Copyright", callback_data="reason_copyright")],
                    [InlineKeyboardButton("❔ Other", callback_data="reason_other")]
                ]
                await message.reply_text(
                    "⚠️ **Select report reason:**", 
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
                logger.info(f"User {user_id} set count: {count}")
                
            except ValueError:
                await message.reply_text("❌ Invalid number. Please send a valid integer.")
            return

        # Step: description
        elif step == "description":
            description = message.text.strip()
            if len(description) < 10:
                await message.reply_text("❌ Description too short. Please provide at least 10 characters.")
                return
            if len(description) > 200:
                await message.reply_text("❌ Description too long. Please keep it under 200 characters.")
                return
                
            report_data[user_id]["description"] = description
            
            # Show summary
            data = report_data[user_id]
            summary = (
                f"📋 **Report Summary:**\n\n"
                f"🎯 **Target:** `{data['username']}`\n"
                f"🔢 **Reports per session:** {data['count']}\n"
                f"⚠️ **Reason:** {data['reason']}\n"
                f"📝 **Description:** {description}\n\n"
                f"🚀 Starting mass reporting..."
            )
            await message.reply_text(summary)
            logger.info(f"Starting report for user {user_id}")
            
            # Create reporting task
            task = asyncio.create_task(start_reporting(user_id, message))
            active_reports[user_id] = task
            return
            
    except Exception as e:
        logger.error(f"Error in handle_text_reply: {e}")
        try:
            await message.reply_text("❌ An error occurred processing your message.")
        except:
            pass

# ---------- Callback Query Handler ----------
@app.on_callback_query(filters.regex(r"^reason_"))
async def handle_reason_callback(client: Client, cq: CallbackQuery):
    """Handle reason selection callback"""
    try:
        user_id = cq.from_user.id
        logger.info(f"🔘 Callback from {user_id}: {cq.data}")
        
        if user_id not in report_data:
            await cq.answer("❌ No active report session.", show_alert=True)
            return

        reason = cq.data.replace("reason_", "")
        report_data[user_id]["reason"] = reason
        report_data[user_id]["step"] = "description"
        
        reason_names = {
            "spam": "Spam",
            "child": "Child Abuse", 
            "violence": "Violence",
            "porn": "Pornography",
            "copyright": "Copyright",
            "other": "Other"
        }
        
        await cq.message.edit_text(
            f"✅ **Reason selected:** {reason_names.get(reason, 'Unknown')}\n\n"
            f"✍️ **Now send a description:**\n"
            f"Provide details about why you're reporting this target."
        )
        await cq.answer()
        logger.info(f"User {user_id} selected reason: {reason}")
        
    except Exception as e:
        logger.error(f"Error in handle_reason_callback: {e}")
        await cq.answer("❌ An error occurred.", show_alert=True)

# Simplified reporting function for testing
async def start_reporting(user_id: int, message: Message):
    """Simplified reporting function"""
    try:
        logger.info(f"🚨 Starting report for user {user_id}")
        data = report_data.get(user_id)
        
        if not data:
            await log_to_user(user_id, "❌ Report data not found.")
            return

        await log_to_user(user_id, f"🚨 Report simulation started for: {data['username']}")
        await asyncio.sleep(2)
        await log_to_user(user_id, "✅ Report simulation completed!")
        
        logger.info(f"Report completed for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error in start_reporting: {e}")
    finally:
        # Clean up
        if user_id in active_reports:
            del active_reports[user_id]
        if user_id in report_data:
            del report_data[user_id]

# ---------- Session Management ----------
async def start_limited_sessions():
    """Start limited sessions for Heroku"""
    logger.info("Starting limited session clients...")
    
    started_count = 0
    max_sessions = 3  # Even more limited for testing
    
    for session_key, client in list(session_clients.items())[:max_sessions]:
        try:
            await client.start()
            started_count += 1
            logger.info(f"✅ {session_key} started")
        except Exception as e:
            logger.error(f"❌ Failed to start {session_key}: {e}")
    
    return started_count

# ---------- Entry Point ----------
if __name__ == "__main__":
    async def main():
        try:
            logger.info("🚀 Starting debug bot for Heroku...")
            
            # Start the app
            await app.start()
            
            # Get bot info
            me = await app.get_me()
            logger.info(f"✅ Bot @{me.username} (ID: {me.id}) started!")
            print(f"✅ Bot @{me.username} is running!")
            
            # Initialize sessions (optional)
            await initialize_sessions()
            started = await start_limited_sessions()
            logger.info(f"📱 Started {started} sessions")
            
            # Send test message to first SUDO user
            if cfg.SUDO:
                try:
                    await app.send_message(
                        cfg.SUDO[0], 
                        f"🟢 **Debug Bot Started!**\n\n"
                        f"🤖 Bot: @{me.username}\n"
                        f"📱 Sessions: {started}\n"
                        f"🆔 Your ID: {cfg.SUDO[0]}\n\n"
                        f"Try these commands:\n"
                        f"• /start\n• /ping\n• /test"
                    )
                    logger.info("✅ Startup message sent to SUDO user")
                except Exception as e:
                    logger.error(f"Failed to send startup message: {e}")
            
            # Keep running
            await asyncio.Event().wait()
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            print(f"Fatal error: {e}")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        print(f"Critical error: {e}")
