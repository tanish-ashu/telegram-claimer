import asyncio
from telethon import TelegramClient, events
import logging
from datetime import datetime
import sys

# --- Configuration ---
API_ID = '23359622'
API_HASH = '6dcf7c69c12b1dd770b569e8684256df'
GROUP_ID = -1002606862659

if len(sys.argv) > 1:
    SESSION_NAME = sys.argv[1]
else:
    SESSION_NAME = 'grabber_bot_default'

# --- Logging Setup ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=f'grabber_{SESSION_NAME}.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

async def main():
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            phone = input("📱 Enter your phone number (with country code): ")
            
            # Send code request and store the phone_code_hash
            sent_code = await client.send_code_request(phone)
            phone_code_hash = sent_code.phone_code_hash
            
            code = input("🔢 Enter the verification code you received: ")
            
            # Sign in with all required parameters
            await client.sign_in(
                phone=phone,
                code=code,
                phone_code_hash=phone_code_hash
            )
        
        myself = await client.get_me()
        logger.info(f"✅ Successfully logged in as: {myself.first_name} (ID: {myself.id})")
        
        @client.on(events.NewMessage(chats=GROUP_ID))
        async def handler(event):
            try:
                await event.message.click(text='CLAIM')
                logger.info(f"🚀 CLAIMED! (MsgID: {event.message.id})")
            except Exception as e:
                logger.error(f"Error claiming message: {e}")

        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
