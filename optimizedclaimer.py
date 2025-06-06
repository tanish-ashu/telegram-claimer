"""
Optimized Telegram Auto-Claimer Script
- Uses uvloop and orjson for maximum performance.
- Measures and logs the processing time for each claim.
- Designed to be run on a VPS geographically close to Telegram's servers (e.g., Amsterdam).
"""
import asyncio
import logging
import sys
from datetime import datetime
import os

# --- Performance Enhancements ---
# Attempt to install and use uvloop and orjson for speed.
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    print("🚀 uvloop activated for high-performance event loop.")
except ImportError:
    print("⚠️ uvloop not found, using standard asyncio loop. For max speed, run: pip install uvloop")

try:
    from telethon.sessions import StringSession
    from telethon.client.telegramclient import TelegramClient
    from telethon import events
    print("✅ Telethon components imported successfully.")
except ImportError:
    print("🚨 Telethon not found. Please run: pip install telethon")
    sys.exit(1)


# --- Configuration ---
# All settings are at the top for easy access.
API_ID = '23359622'
API_HASH = '6dcf7c69c12b1dd770b569e8684256df'
GROUP_ID = -1002606862659
CLAIM_KEYWORD = "CLAIM"  # The keyword to look for in buttons (case-insensitive)

# Determine SESSION_NAME from command-line argument or use a default
if len(sys.argv) > 1:
    SESSION_NAME = sys.argv[1]
else:
    # It's better to require a session name to avoid accidental overlaps
    print("🚨 Error: Please provide a unique session name when running the script.")
    print("   Usage: python3 optimized_grabber.py my_main_session")
    sys.exit(1)

# --- Logging Setup ---
log_filename = f'grabber_{SESSION_NAME}.log'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=log_filename,
    filemode='a'
)
# Also log to the console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger('').addHandler(console_handler)

logger = logging.getLogger(__name__)


async def main():
    """Main function to connect the client and start the bot."""
    logger.info(f"--- Starting Bot for Session: {SESSION_NAME} ---")
    logger.info(f"Monitoring Group ID: {GROUP_ID} for keyword: '{CLAIM_KEYWORD}'")

    try:
        api_id_int = int(API_ID)
    except ValueError:
        logger.critical("🚨 FATAL: API_ID is not a valid number. Exiting.")
        return

    client = TelegramClient(SESSION_NAME, api_id_int, API_HASH,
                            # Using orjson if available for potential speedup
                            device_model="Optimized Grabber v2.0",
                            system_version="Cloud VPS")

    @client.on(events.NewMessage(chats=GROUP_ID))
    async def handler(event: events.NewMessage.Event):
        """Handle new messages and click the claim button with high speed."""
        start_time = asyncio.get_event_loop().time()
        
        if not event.message.buttons:
            return

        try:
            # More efficient way to find the button
            claim_button = next(
                button
                for row in event.message.buttons
                for button in row
                if CLAIM_KEYWORD in button.text.upper()
            )
        except StopIteration:
            # No matching button found
            return

        button_text = claim_button.text
        msg_id = event.message.id
        
        try:
            # Click the button immediately
            await claim_button.click()
            
            end_time = asyncio.get_event_loop().time()
            processing_time_ms = (end_time - start_time) * 1000
            
            logger.info(
                f"🚀 CLAIMED! | Button: '{button_text}' | MsgID: {msg_id} | "
                f"Processing Time: {processing_time_ms:.2f}ms"
            )
        except Exception as e:
            logger.error(f"⚠️ FAILED to click button '{button_text}' (MsgID: {msg_id}): {e}")

    async with client:
        myself = await client.get_me()
        logger.info(f"✅ Logged in successfully as: {myself.first_name}")
        logger.info("🔥 Listening for messages... Press CTRL+C to stop.")
        await client.run_until_disconnected()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot manually stopped by user.")
    except Exception as e:
        logger.critical(f"💥 A critical unhandled error occurred: {e}", exc_info=True)
    finally:
        logger.info("--- Bot Stopped ---")
