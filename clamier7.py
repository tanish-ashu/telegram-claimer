import asyncio
from telethon import TelegramClient, events
import logging
from datetime import datetime
import sys

# --- Configuration ---
API_ID = '23359622'
API_HASH = '6dcf7c69c12b1dd770b569e8684256df'
GROUP_ID = -1002606862659

# Determine SESSION_NAME from command-line argument or use a default
if len(sys.argv) > 1:
    SESSION_NAME = sys.argv[1]
    print(f"Using session name from argument: {SESSION_NAME}")
else:
    SESSION_NAME = 'grabber_bot_default'
    print(f"No session name provided. Using default: {SESSION_NAME}")

# --- Logging Setup ---
LOG_FILE_NAME = f'grabber_{SESSION_NAME}.log'
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=LOG_FILE_NAME,
    filemode='a'
)
# Also log to console for real-time feedback
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger('').addHandler(console_handler)

logger = logging.getLogger(__name__)

async def main():
    try:
        api_id_int = int(API_ID)
    except ValueError:
        logger.error("🚨 FATAL: API_ID in your script is not a valid number. Please check it.")
        return

    client = TelegramClient(SESSION_NAME, api_id_int, API_HASH,
                            connection_retries=5,
                            retry_delay=5)

    logger.info("Bot starting in high-performance claim mode...")

    try:
        logger.info("🔄 Connecting to Telegram...")
        await client.connect()

        if not await client.is_user_authorized():
            logger.info("🔑 Authentication required.")
            phone_number = input("📱 Please enter your phone number (with country code): ")
            await client.send_code_request(phone_number)
            try:
                await client.sign_in(phone=phone_number, code=input("🔢 Please enter the code: "))
            except Exception as auth_err:
                logger.error(f"🚨 Authentication failed: {auth_err}")
                await client.disconnect()
                return

        myself = await client.get_me()
        logger.info(f"✅ Successfully logged in as: {myself.first_name} (ID: {myself.id})")

        try:
            # The Group ID must be an integer
            target_group_entity = await client.get_entity(int(GROUP_ID))
            logger.info(f"👀 Monitoring Group: '{getattr(target_group_entity, 'title', 'Unknown Title')}' (ID: {target_group_entity.id})")
        except Exception as e:
            logger.error(f"🚨 Could not find or access group with ID {GROUP_ID}. Error: {e}")
            await client.disconnect()
            return

        logger.info("🔥 Ready to claim! Listening for new messages...")

    except Exception as e:
        logger.critical(f"🚨 An error occurred during startup: {e}", exc_info=True)
        if client.is_connected():
            await client.disconnect()
        return

    @client.on(events.NewMessage(chats=target_group_entity))
    async def handler(event):
        # High-speed logic: Check for inline keyboard buttons. This is much more robust.
        if event.message.reply_markup and hasattr(event.message.reply_markup, 'rows'):
            for row in event.message.reply_markup.rows:
                for button in row.buttons:
                    # Check for "CLAIM" in the button's visible text.
                    if "CLAIM" in button.text.upper():
                        try:
                            # *** FIX APPLIED HERE ***
                            # Click the button via the MESSAGE object, passing the specific button's data.
                            # This is the correct way to handle 'KeyboardButtonCallback'.
                            await event.message.click(data=button.data)
                            logger.info(f"🚀 CLAIMED! (Button: '{button.text}' on MsgID: {event.message.id})")
                            # Exit the handler for this message after a successful claim.
                            return
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to click button '{button.text}' on MsgID {event.message.id}. Reason: {e}")
                            # Continue to the next button if this one fails for some reason.

    try:
        await client.run_until_disconnected()
    finally:
        if client.is_connected():
            await client.disconnect()
        logger.info("🔌 Bot stopped and client disconnected.")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot manually stopped by user.")
    except Exception as e:
        logger.critical(f"💥 A critical unhandled error occurred: {e}", exc_info=True)
