import asyncio
from telethon import TelegramClient, events
import logging
from datetime import datetime
import sys

# --- Configuration (UNCHANGED) ---
API_ID = '23359622'
API_HASH = '6dcf7c69c12b1dd770b569e8684256df'
GROUP_ID = -1002606862659

if len(sys.argv) > 1:
    SESSION_NAME = sys.argv[1]
else:
    SESSION_NAME = 'grabber_bot_default'

# --- Simplified Logging (UNCHANGED) ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=f'grabber_{SESSION_NAME}.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

async def main():
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    
    # --- Original Auth Flow (UNCHANGED) ---
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(input("📱 Phone: "))
        await client.sign_in(phone=input("📱 Phone: "), code=input("🔢 Code: "))
    
    myself = await client.get_me()
    logger.info(f"Logged in as {myself.first_name}")

    # --- Critical Optimization: Direct Click ---
    @client.on(events.NewMessage(chats=GROUP_ID))
    async def handler(event):
        try:
            # IMMEDIATE CLICK - No button scanning
            await event.message.click(text='CLAIM')
            logger.info(f"🚀 CLAIMED! (MsgID: {event.message.id})")
        except Exception:
            pass  # Silent fail if no CLAIM button (shouldn't happen in your case)

    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
