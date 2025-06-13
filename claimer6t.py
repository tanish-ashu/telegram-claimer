import asyncio
import random
import logging
import sys
from datetime import datetime
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

# --- CONFIGURATION (YOUR SETTINGS) ---
API_ID = '23359622'  # From my.telegram.org
API_HASH = '6dcf7c69c12b1dd770b569e8684256df'
GROUP_ID = -1002606862659  # Your target group ID

# Safety Parameters
MIN_DELAY = 0.8  # Minimum delay in seconds (800ms)
MAX_DELAY = 2.5  # Maximum delay in seconds (2500ms)
MAX_RETRIES = 3  # Max attempts per claim
FLOOD_WAIT_BUFFER = 10  # Extra seconds after FloodWait

# --- SESSION SETUP ---
SESSION_NAME = sys.argv[1] if len(sys.argv) > 1 else 'grabber_bot_default'
print(f"Using session: {SESSION_NAME}")

# --- LOGGING ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=f'grabber_{SESSION_NAME}.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# --- SAFETY FUNCTIONS ---
async def random_delay():
    """Randomized delay between actions"""
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    logger.info(f"Safety delay: {delay:.2f}s")
    await asyncio.sleep(delay)

async def safe_click(event, button_text, max_retries=MAX_RETRIES):
    """Click button with retries and delays"""
    for attempt in range(max_retries):
        try:
            await random_delay()
            
            # Try both click methods
            if hasattr(button_text, 'data'):
                await event.click(data=button_text.data)
            else:
                await event.click(text=button_text)
                
            logger.info(f"✅ Claimed: {button_text}")
            return True
            
        except FloodWaitError as e:
            wait_time = e.seconds + FLOOD_WAIT_BUFFER
            logger.warning(f"⏳ FloodWait: Pausing for {wait_time}s")
            await asyncio.sleep(wait_time)
        except Exception as e:
            logger.error(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
    return False

# --- MAIN BOT ---
async def main():
    try:
        client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
        
        # Connect and authenticate
        await client.connect()
        if not await client.is_user_authorized():
            print("🔑 First-run authentication required")
            phone = input("📱 Enter phone (e.g., +1234567890): ")
            await client.send_code_request(phone)
            code = input("🔢 Enter verification code: ")
            await client.sign_in(phone, code)
        
        myself = await client.get_me()
        print(f"✅ Logged in as: {myself.first_name} (ID: {myself.id})")
        
        # Verify group access
        try:
            group = await client.get_entity(GROUP_ID)
            print(f"👀 Monitoring: {group.title}")
        except Exception as e:
            logger.error(f"❌ Group access failed: {e}")
            raise

        # --- EVENT HANDLER ---
        @client.on(events.NewMessage(chats=group))
        async def claim_handler(event):
            if not event.message.reply_markup:
                return
                
            for row in event.message.reply_markup.rows:
                for button in row.buttons:
                    if "CLAIM" in button.text.upper():
                        logger.info(f"🔍 Found claim button: {button.text}")
                        if await safe_click(event, button):
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            print(f"[{timestamp}] 🚀 CLAIMED: {button.text}")
                        else:
                            logger.warning("❌ Failed after retries")
                        return  # Exit after first claim attempt

        print("🔥 Ready - Listening for claims... (Ctrl+C to stop)")
        await client.run_until_disconnected()

    except Exception as e:
        logger.critical(f"💥 CRASH: {str(e)}", exc_info=True)
        print(f"❌ Critical error: {e}")
    finally:
        if client.is_connected():
            await client.disconnect()
        logger.info("Bot stopped")

if __name__ == '__main__':
    print("🚀 Starting Telegram Auto-Claimer")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        logger.info("Manual stop")
