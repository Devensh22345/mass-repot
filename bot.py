from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.raw import functions, types
import asyncio
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportBotMVP:
    def __init__(self, api_id, api_hash, bot_token, session_string, sudo_users):
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.sudo_users = sudo_users
        
        # Bot client
        self.app = Client("report_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
        
        # Single user session (MVP uses only 1 session)
        self.user_client = None
        if session_string:
            self.user_client = Client("user_session", api_id=api_id, api_hash=api_hash, session_string=session_string)
        
        # Report states
        self.report_states = {}
        
        # Report reasons mapping
        self.reason_map = {
            "spam": types.InputReportReasonSpam(),
            "violence": types.InputReportReasonViolence(),
            "other": types.InputReportReasonOther()
        }
        
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.app.on_message(filters.command("start"))
        async def start_handler(client, message):
            await self.handle_start(message)
        
        @self.app.on_message(filters.command("report"))
        async def report_handler(client, message):
            await self.handle_report_command(message)
        
        @self.app.on_message(filters.command("cancel"))
        async def cancel_handler(client, message):
            await self.handle_cancel(message)
        
        @self.app.on_message(filters.text & ~filters.command(["start", "report", "cancel"]))
        async def text_handler(client, message):
            await self.handle_text_input(message)
        
        @self.app.on_callback_query(filters.regex(r"^reason_"))
        async def callback_handler(client, query):
            await self.handle_reason_callback(query)
    
    async def handle_start(self, message: Message):
        if not self.is_sudo_user(message.from_user.id):
            await message.reply("❌ Access denied.")
            return
        
        welcome_text = (
            "🤖 **Report Bot MVP**\n\n"
            "**Available Commands:**\n"
            "• `/report` - Start report process\n"
            "• `/cancel` - Cancel current operation\n\n"
            "⚠️ **WARNING:** Use only for legitimate moderation purposes."
        )
        await message.reply(welcome_text)
    
    async def handle_report_command(self, message: Message):
        if not self.is_sudo_user(message.from_user.id):
            await message.reply("❌ Access denied.")
            return
        
        if not self.user_client:
            await message.reply("❌ No user session configured.")
            return
        
        user_id = message.from_user.id
        self.report_states[user_id] = {"step": "target"}
        await message.reply("📝 Send the target username or ID (e.g., @channel):")
    
    async def handle_cancel(self, message: Message):
        user_id = message.from_user.id
        if user_id in self.report_states:
            del self.report_states[user_id]
            await message.reply("✅ Operation cancelled.")
        else:
            await message.reply("ℹ️ No active operation to cancel.")
    
    async def handle_text_input(self, message: Message):
        user_id = message.from_user.id
        
        if user_id not in self.report_states:
            return
        
        state = self.report_states[user_id]
        step = state.get("step")
        
        if step == "target":
            target = message.text.strip()
            if not target:
                await message.reply("❌ Please provide a valid target.")
                return
            
            state["target"] = target
            state["step"] = "reason"
            
            # Show reason buttons (simplified for MVP)
            buttons = [
                [InlineKeyboardButton("🚫 Spam", callback_data="reason_spam")],
                [InlineKeyboardButton("🔪 Violence", callback_data="reason_violence")],
                [InlineKeyboardButton("❔ Other", callback_data="reason_other")]
            ]
            await message.reply(
                "⚠️ Select report reason:",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        
        elif step == "description":
            description = message.text.strip()
            state["description"] = description
            
            # Start reporting
            await message.reply("🚀 Processing report...")
            await self.execute_report(user_id, message)
    
    async def handle_reason_callback(self, query: CallbackQuery):
        user_id = query.from_user.id
        
        if user_id not in self.report_states:
            await query.answer("❌ No active report session.")
            return
        
        reason = query.data.replace("reason_", "")
        self.report_states[user_id]["reason"] = reason
        self.report_states[user_id]["step"] = "description"
        
        await query.message.reply("✍️ Send a brief description for the report:")
        await query.answer()
    
    async def execute_report(self, user_id: int, message: Message):
        try:
            state = self.report_states[user_id]
            target = state["target"]
            reason = state["reason"]
            description = state["description"]
            
            # Log the report attempt
            logger.info(f"Report attempt: User {user_id}, Target: {target}, Reason: {reason}")
            
            # Try to resolve the target
            try:
                chat = await self.user_client.get_chat(target)
                peer = await self.user_client.resolve_peer(chat.id)
            except Exception as e:
                await message.reply(f"❌ Failed to find target: {str(e)}")
                return
            
            # Submit report
            reason_obj = self.reason_map.get(reason, types.InputReportReasonOther())
            
            try:
                await self.user_client.invoke(functions.account.ReportPeer(
                    peer=peer,
                    reason=reason_obj,
                    message=description
                ))
                
                await message.reply(
                    f"✅ **Report submitted successfully**\n"
                    f"Target: `{target}`\n"
                    f"Reason: {reason}\n"
                    f"Description: {description}"
                )
                
                # Log successful report
                self.log_report(user_id, target, reason, description, "success")
                
            except Exception as e:
                await message.reply(f"❌ Report failed: {str(e)}")
                self.log_report(user_id, target, reason, description, "failed", str(e))
        
        except Exception as e:
            await message.reply(f"❌ Unexpected error: {str(e)}")
            logger.error(f"Report execution error: {e}")
        
        finally:
            # Clean up state
            if user_id in self.report_states:
                del self.report_states[user_id]
    
    def log_report(self, user_id: int, target: str, reason: str, description: str, status: str, error: str = None):
        """Log report attempts for audit purposes"""
        log_entry = {
            "user_id": user_id,
            "target": target,
            "reason": reason,
            "description": description,
            "status": status,
            "error": error,
            "timestamp": asyncio.get_event_loop().time()
        }
        logger.info(f"Report log: {json.dumps(log_entry)}")
    
    def is_sudo_user(self, user_id: int) -> bool:
        return user_id in self.sudo_users
    
    async def start(self):
        """Start the bot and user client"""
        if self.user_client:
            await self.user_client.start()
        await self.app.start()
        logger.info("Bot started successfully")
    
    async def stop(self):
        """Stop the bot and user client"""
        if self.user_client:
            await self.user_client.stop()
        await self.app.stop()
        logger.info("Bot stopped")

# Usage example (create a separate config file)
if __name__ == "__main__":
    # Configuration (move to separate config.py file)
    CONFIG = {
        "API_ID": 12345,  # Your API ID
        "API_HASH": "your_api_hash",  # Your API Hash
        "BOT_TOKEN": "your_bot_token",  # Your bot token
        "SESSION_STRING": "your_session_string",  # User session string
        "SUDO_USERS": [123456789]  # List of sudo user IDs
    }
    
    bot = ReportBotMVP(
        api_id=CONFIG["API_ID"],
        api_hash=CONFIG["API_HASH"],
        bot_token=CONFIG["BOT_TOKEN"],
        session_string=CONFIG["SESSION_STRING"],
        sudo_users=CONFIG["SUDO_USERS"]
    )
    
    # Run the bot
    import asyncio
    
    async def main():
        await bot.start()
        print("Bot is running... Press Ctrl+C to stop")
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            await bot.stop()
    
    asyncio.run(main())
