import asyncio
import logging
import sys
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import Message
from telethon.tl.custom import Button

# --- Configuration ---
# Your Telegram API credentials
API_ID = '23359622'
API_HASH = '6dcf7c69c12b1dd770b569e8684256df'

# The target group/channel ID
GROUP_ID = -1002606862659

# Determine the session name from command-line arguments or use a default
SESSION_NAME = sys.argv[1] if len(sys.argv) > 1 else 'grabber_bot_default'

# --- Logging Setup ---
# A unique log file will be created for each session name
log_filename = f'grabber_{SESSION_NAME}.log'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=log_filename,
    filemode='a'
)
logger = logging.getLogger(__name__)

# Add a console handler to also print logs to the screen
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


async def main():
    """Main function to connect the client and start the bot."""
    try:
        api_id_int = int(API_ID)
    except ValueError:
        logger.critical("🚨 Error: API_ID in your script is not a valid number. Please check it.")
        return

    client = TelegramClient(SESSION_NAME, api_id_int, API_HASH)

    logger.info("Bot starting in optimized claim mode...")

    try:
        logger.info("🔄 Connecting to Telegram...")
        await client.connect()

        if not await client.is_user_authorized():
            logger.info("🔑 Authentication required.")
            phone_number = input("📱 Please enter your phone number (with country code): ")
            await client.send_code_request(phone_number)
            try:
                await client.sign_in(phone=phone_number, code=input("🔢 Please enter the code you received: "))
            except Exception as auth_err:
                logger.critical(f"🚨 Authentication failed: {auth_err}")
                await client.disconnect()
                return

        myself = await client.get_me()
        logger.info(f"✅ Successfully logged in as: {myself.first_name} (ID: {myself.id})")

        try:
            target_group_entity = await client.get_entity(GROUP_ID)
            logger.info(f"👀 Monitoring Group: '{getattr(target_group_entity, 'title', 'Unknown Title')}' (ID: {target_group_entity.id})")
        except Exception as e:
            logger.critical(f"🚨 Could not find or access group with ID {GROUP_ID}. Error: {e}")
            await client.disconnect()
            return

        logger.info("🔥 Ready to claim! Listening for new messages...")

        @client.on(events.NewMessage(chats=target_group_entity))
        async def handler(event: events.NewMessage.Event):
            """Handle new messages and attempt to click a 'CLAIM' button."""
            message: Message = event.message
            message_id = message.id

            if not message.buttons:
                return

            # Flatten the list of buttons and find the claim button more efficiently
            try:
                claim_button = [
                    button for row in message.buttons for button in row
                    if "CLAIM" in button.text.upper()
                ].pop()
            except IndexError:
                # No "CLAIM" button found in this message
                return

            button_text = claim_button.text
            logger.info(f"🔘 'CLAIM' button found: '{button_text}' on MsgID: {message_id}. Attempting to click...")

            try:
                # Click the button. Telethon is smart enough to use the correct method.
                await claim_button.click()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logger.info(f"[{timestamp}] 🚀 CLAIMED! (Button: '{button_text}' on MsgID: {message_id})")
            except Exception as click_err:
                logger.error(f"⚠️ FAILED to click 'CLAIM' button (MsgID: {message_id}, Text: '{button_text}'): {click_err}", exc_info=True)

        await client.run_until_disconnected()

    except Exception as e:
        logger.critical(f"💥 A critical error occurred during startup or runtime: {e}", exc_info=True)
    finally:
        if client.is_connected():
            logger.info("🔌 Disconnecting client...")
            await client.disconnect()
        logger.info("🔌 Client disconnected.")


if __name__ == '__main__':
    logger.info("🚀 Starting bot script...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot manually stopped by user (Ctrl+C).")
    except Exception as e:
        logger.critical(f"💥 A critical unhandled error occurred in the main execution block: {e}", exc_info=True)
