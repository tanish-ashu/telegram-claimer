import asyncio
import uvloop
from telethon import TelegramClient, events
import logging
from datetime import datetime
import sys

# --- Configuration ---
API_ID = '23359622'
API_HASH = '6dcf7c69c12b1dd770b569e8684256df'
GROUP_ID = -1002606862659

# Session name handling (unchanged)
if len(sys.argv) > 1:
    SESSION_NAME = sys.argv[1]
else:
    SESSION_NAME = 'grabber_bot_default'

# --- Critical Optimizations ---
uvloop.install()  # Faster async I/O (single line addition)

# Initialize client with performance settings
client = TelegramClient(
    SESSION_NAME,
    int(API_ID),
    API_HASH,
    connection_retries=3,
    auto_reconnect=True,
    flood_sleep_threshold=30  # Reduced from default 60s
)

# --- Logging Setup (unchanged) ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=f'grabber_{SESSION_NAME}.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

async def main():
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            phone_number = input("📱 Enter phone number: ")
            await client.send_code_request(phone_number)
            code = input("🔢 Enter verification code: ")
            await client.sign_in(phone=phone_number, code=code)

        myself = await client.get_me()
        target_group_entity = await client.get_entity(GROUP_ID)
        print(f"👂 Listening in '{target_group_entity.title}'...")

        # --- Optimized Handler ---
        @client.on(events.NewMessage(chats=target_group_entity))
        async def handler(event):
            if event.message.reply_markup:
                for row in event.message.reply_markup.rows:
                    for btn in row.buttons:
                        if "CLAIM" in btn.text.upper():
                            try:
                                # Faster click with timeout
                                await asyncio.wait_for(
                                    event.message.click(data=btn.data if hasattr(btn, 'data') else None),
                                    timeout=5
                                )
                                print(f"🚀 CLAIMED at {datetime.now().strftime('%H:%M:%S')}")
                                return  # Exit after first successful claim
                            except Exception as e:
                                logger.warning(f"Click error: {str(e)[:100]}")

        await client.run_until_disconnected()

    finally:
        if client.is_connected():
            await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
