#!/usr/bin/env python3
import asyncio
import uvloop
from telethon import TelegramClient, events, connection
import logging
from datetime import datetime
import sys
import signal

# --- Configuration ---
API_ID = '23359622'  # Your API ID
API_HASH = '6dcf7c69c12b1dd770b569e8684256df'  # Your API Hash
GROUP_ID = -1002606862659  # Your group ID
SESSION_NAME = sys.argv[1] if len(sys.argv) > 1 else 'default_session'

# --- Performance Optimizations ---
uvloop.install()
signal.signal(signal.SIGALRM, lambda x, y: print("Connection timeout!"))
signal.alarm(30)  # 30-second global timeout

# --- Enhanced Logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f'bot_{SESSION_NAME}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Robust Client Setup ---
client = TelegramClient(
    SESSION_NAME,
    API_ID,
    API_HASH,
    connection=connection.ConnectionTcpFull,
    connection_retries=3,
    timeout=10,
    auto_reconnect=True,
    flood_sleep_threshold=30,
    device_model="UltraClaimer 10X"
)

async def safe_connect():
    """Handles connection with proper error handling"""
    try:
        logger.info("Connecting to Telegram...")
        await client.connect()
        
        if not await client.is_user_authorized():
            logger.warning("No active session - starting interactive login")
            await client.start(
                phone=lambda: input("📱 Enter phone number: "),
                code_callback=lambda: input("🔢 Enter verification code: ")
            )
            
        me = await client.get_me()
        logger.info(f"Successfully connected as {me.first_name} (ID: {me.id})")
        return True
        
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
        await client.disconnect()
        return False

async def handle_claim(event):
    """Optimized claim handler"""
    try:
        if event.message.reply_markup:
            for row in event.message.reply_markup.rows:
                for btn in row.buttons:
                    if "CLAIM" in btn.text.upper():
                        await asyncio.wait_for(
                            event.message.click(data=btn.data if hasattr(btn, 'data') else None),
                            timeout=5
                        )
                        logger.info(f"Claimed message ID: {event.message.id}")
                        return
    except Exception as e:
        logger.warning(f"Claim error: {str(e)[:100]}")

async def main():
    if not await safe_connect():
        return

    try:
        group = await client.get_entity(GROUP_ID)
        logger.info(f"Monitoring group: {group.title}")
        
        client.add_event_handler(
            handle_claim,
            events.NewMessage(chats=group)
        )
        
        logger.info("Bot is now running...")
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.critical(f"Bot crashed: {str(e)}", exc_info=True)
    finally:
        await client.disconnect()
        logger.info("Bot stopped")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
