from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.raw import functions, types
from pyrogram.errors import FloodWait, PeerIdInvalid, UsernameInvalid, UsernameNotOccupied, SessionPasswordNeeded
import asyncio
import random
import time
import logging
from configs import cfg

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot client
app = Client("bot", api_id=cfg.API_ID, api_hash=cfg.API_HASH, bot_token=cfg.BOT_TOKEN)

# User sessions with improved error handling
session_clients = {}
active_reports = {}  # Track active reporting tasks for cancellation

# Initialize session clients
async def initialize_sessions():
    """Initialize all session clients with proper error handling"""
    for i in range(1, 31):
        session_key = f"session{i}"
        session_string = getattr(cfg, f"SESSION_STRING_{i}", None)
        if session_string and session_string.strip():
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

# Store per-user reporting state
report_data = {}

# ---------- Helper Functions ----------
async def log_to_user(user_id: int, text: str):
    """Send log message to user with error handling"""
    try:
        await app.send_message(user_id, text)
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
@app.on_message(filters.command("start"))
async def start_message(client: Client, message: Message):
    txt = (
        "👋 Hello! I can mass-report Telegram channels, groups, or bots.\n\n"
        "Commands:\n"
        "• /report → Start reporting flow\n"
        "• /stopreport → Cancel current reporting task\n\n"
        "⚠️ Only SUDO users can use this bot."
    )
    await message.reply_text(txt)
    await log_to_user(message.from_user.id, f"✅ Bot started by {message.from_user.mention} (ID: {message.from_user.id})")
        
    except Exception as e:
        logger.error(f"Error in start_message: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@app.on_message(filters.command("status"))
async def status_message(client: Client, message: Message):
    """Handle /status command"""
    try:
        if message.from_user.id not in cfg.SUDO:
            await message.reply_text("❌ Only sudo users can use this command.")
            return
            
        active_sessions = len(session_clients)
        active_reports_count = len(active_reports)
        
        status_text = (
            f"🤖 **Bot Status**\n\n"
            f"📱 **Active Sessions:** {active_sessions}\n"
            f"📊 **Active Reports:** {active_reports_count}\n"
            f"👥 **Total SUDO Users:** {len(cfg.SUDO)}\n\n"
            f"✅ **Bot is running normally**"
        )
        await message.reply_text(status_text)
        
    except Exception as e:
        logger.error(f"Error in status_message: {e}")
        await message.reply_text("❌ An error occurred while checking status.")

@app.on_message(filters.command("report"))
async def report_command(client, message: Message):
    """Handle /report command"""
    try:
        if message.from_user.id not in cfg.SUDO:
            await message.reply_text("❌ Only sudo users can use this command.")
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
        
    except Exception as e:
        logger.error(f"Error in report_command: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

@app.on_message(filters.command("stopreport"))
async def stop_report_command(client, message: Message):
    """Handle /stopreport command"""
    try:
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
        await log_to_user(user_id, "🛑 Reporting task cancelled by user.")
        
    except Exception as e:
        logger.error(f"Error in stop_report_command: {e}")
        await message.reply_text("❌ An error occurred while cancelling the task.")

# ---------- Text Input Handler ----------
@app.on_message(filters.text & ~filters.command(["report", "start", "stopreport", "status"]))
async def handle_text_reply(client: Client, message: Message):
    """Handle text input during reporting flow"""
    try:
        user_id = message.from_user.id
        if user_id not in report_data or "step" not in report_data[user_id]:
            return

        step = report_data[user_id]["step"]

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
            return

        # Step: count
        elif step == "count":
            try:
                count = int(message.text.strip())
                if count <= 0:
                    await message.reply_text("❌ Number must be positive. Please enter a valid number.")
                    return
                if count > 20:  # Reasonable limit
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
            
            # Show summary before starting
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
            
            # Create a task for reporting to avoid blocking
            task = asyncio.create_task(start_reporting(user_id, message))
            active_reports[user_id] = task
            return
            
    except Exception as e:
        logger.error(f"Error in handle_text_reply: {e}")
        await message.reply_text("❌ An error occurred. Please try again.")

# ---------- Callback Query Handler ----------
@app.on_callback_query(filters.regex(r"^reason_"))
async def handle_reason_callback(client: Client, cq: CallbackQuery):
    """Handle reason selection callback"""
    try:
        user_id = cq.from_user.id
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
        
    except Exception as e:
        logger.error(f"Error in handle_reason_callback: {e}")
        await cq.answer("❌ An error occurred.", show_alert=True)

# ---------- Main Reporting Function ----------
async def start_reporting(user_id: int, message: Message):
    """Main reporting function with comprehensive error handling"""
    try:
        data = report_data.get(user_id)
        if not data:
            await log_to_user(user_id, "❌ Report data not found.")
            return

        target = data["username"]
        reason = data["reason"]
        count = data["count"]
        description = data["description"]

        reason_map = {
            "spam": types.InputReportReasonSpam(),
            "child": types.InputReportReasonChildAbuse(),
            "violence": types.InputReportReasonViolence(),
            "porn": types.InputReportReasonPornography(),
            "copyright": types.InputReportReasonCopyright(),
            "other": types.InputReportReasonOther()
        }
        reason_obj = reason_map.get(reason, types.InputReportReasonSpam())

        await log_to_user(user_id,
            f"🚨 **Mass report started**\n"
            f"🎯 **Target:** {target}\n"
            f"⚠️ **Reason:** {reason}\n"
            f"🔢 **Reports per session:** {count}\n"
            f"📱 **Total sessions:** {len(session_clients)}"
        )

        successful_reports = 0
        failed_sessions = 0
        session_results = {}
        
        for session_key, sc in session_clients.items():
            try:
                # Check if task was cancelled
                if user_id not in active_reports:
                    await log_to_user(user_id, "🛑 Reporting cancelled by user.")
                    break
                
                session_reports = 0
                session_results[session_key] = {"status": "processing", "reports": 0, "error": None}
                
                # Try to start the session if not already started
                if not sc.is_connected:
                    await sc.start()
                    await asyncio.sleep(2)
                
                # Validate target exists
                try:
                    chat = await sc.get_chat(target)
                    peer = await sc.resolve_peer(chat.id)
                    await log_to_user(user_id, f"✅ {session_key}: Target validated - {chat.title or chat.first_name or target}")
                except (PeerIdInvalid, UsernameInvalid, UsernameNotOccupied) as e:
                    session_results[session_key] = {"status": "failed", "reports": 0, "error": "Invalid target"}
                    await log_to_user(user_id, f"❌ {session_key}: Invalid target {target}")
                    failed_sessions += 1
                    continue
                except Exception as e:
                    session_results[session_key] = {"status": "failed", "reports": 0, "error": str(e)}
                    await log_to_user(user_id, f"❌ {session_key}: Failed to resolve {target}: {e}")
                    failed_sessions += 1
                    continue

                # Send reports for this session
                for i in range(count):
                    try:
                        # Check if task was cancelled
                        if user_id not in active_reports:
                            break
                            
                        await sc.invoke(functions.account.ReportPeer(
                            peer=peer,
                            reason=reason_obj,
                            message=description
                        ))
                        
                        session_reports += 1
                        successful_reports += 1
                        session_results[session_key]["reports"] = session_reports
                        
                        # Log progress for every report
                        await log_to_user(user_id, f"📤 {session_key}: Report {i+1}/{count} sent")
                        
                        # Random delay between reports (10-30 seconds)
                        delay = random.uniform(10, 30)
                        await asyncio.sleep(delay)
                        
                    except FloodWait as e:
                        await log_to_user(user_id, f"⏳ {session_key}: Rate limited for {e.value} seconds")
                        await asyncio.sleep(e.value + 2)
                        # Retry the report
                        try:
                            await sc.invoke(functions.account.ReportPeer(
                                peer=peer,
                                reason=reason_obj,
                                message=description
                            ))
                            session_reports += 1
                            successful_reports += 1
                            session_results[session_key]["reports"] = session_reports
                        except Exception as retry_e:
                            await log_to_user(user_id, f"❌ {session_key}: Retry failed: {retry_e}")
                            
                    except Exception as e:
                        await log_to_user(user_id, f"❌ {session_key}: Report {i+1} failed: {e}")
                        await asyncio.sleep(5)

                session_results[session_key]["status"] = "completed"
                
                # Delay between sessions (30-60 seconds)
                session_delay = random.uniform(30, 60)
                await log_to_user(user_id, f"⏸️ Waiting {session_delay:.1f}s before next session...")
                await asyncio.sleep(session_delay)

            except Exception as e:
                session_results[session_key] = {"status": "error", "reports": session_reports, "error": str(e)}
                await log_to_user(user_id, f"❌ {session_key}: Unexpected error: {e}")
                failed_sessions += 1

        # Generate final report
        total_expected = len(session_clients) * count
        success_rate = (successful_reports / total_expected * 100) if total_expected > 0 else 0
        
        final_report = (
            f"🏁 **Mass report completed for** `{target}`\n\n"
            f"📊 **Results:**\n"
            f"✅ **Successful reports:** {successful_reports}/{total_expected} ({success_rate:.1f}%)\n"
            f"❌ **Failed sessions:** {failed_sessions}/{len(session_clients)}\n"
            f"⏱️ **Duration:** {time.time() - data['started_at']:.1f} seconds\n\n"
            f"📋 **Session Summary:**\n"
        )
        
        # Add session details
        for session_key, result in session_results.items():
            status_emoji = {"completed": "✅", "failed": "❌", "error": "⚠️", "processing": "🔄"}
            emoji = status_emoji.get(result["status"], "❓")
            final_report += f"{emoji} {session_key}: {result['reports']} reports\n"

        await log_to_user(user_id, final_report)

    except Exception as e:
        logger.error(f"Error in start_reporting: {e}")
        await log_to_user(user_id, f"❌ Critical error in reporting process: {e}")
    
    finally:
        # Clean up
        if user_id in active_reports:
            del active_reports[user_id]
        if user_id in report_data:
            del report_data[user_id]

# ---------- Session Management ----------
async def start_all_sessions():
    """Start all session clients with error handling"""
    logger.info("Starting session clients...")
    
    for session_key, client in session_clients.items():
        try:
            await client.start()
            logger.info(f"✅ {session_key} started successfully")
        except SessionPasswordNeeded:
            logger.error(f"❌ {session_key}: 2FA password required")
        except Exception as e:
            logger.error(f"❌ Failed to start {session_key}: {e}")

async def stop_all_sessions():
    """Stop all session clients"""
    logger.info("Stopping session clients...")
    
    for session_key, client in session_clients.items():
        try:
            if client.is_connected:
                await client.stop()
            logger.info(f"✅ {session_key} stopped successfully")
        except Exception as e:
            logger.error(f"❌ Failed to stop {session_key}: {e}")

# ---------- Error Handlers ----------
@app.on_message()
async def global_message_handler(client, message):
    """Global error handler for all messages"""
    try:
        # This will be triggered for any unhandled message
        pass
    except Exception as e:
        logger.error(f"Global message handler error: {e}")

# ---------- Main Function ----------
async def main():
    """Main function to run the bot"""
    try:
        logger.info("Initializing sessions...")
        await initialize_sessions()
        
        logger.info("Starting session clients...")
        await start_all_sessions()
        
        logger.info("Starting main bot...")
        await app.start()
        
        # Get and display bot info
        me = await app.get_me()
        logger.info(f"Bot started: @{me.username} (ID: {me.id})")
        logger.info(f"Active sessions: {len(session_clients)}")
        logger.info(f"SUDO users: {len(cfg.SUDO)}")
        
        print("✅ Bot is running! Press Ctrl+C to stop.")
        
        # Keep the bot running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("Received stop signal")
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        logger.info("Shutting down...")
        await stop_all_sessions()
        if app.is_connected:
            await app.stop()
        logger.info("Shutdown complete")

# ---------- Entry Point ----------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print("Bot crashed. Check logs for details.")
