import asyncio
from telethon import TelegramClient, events
import logging
from datetime import datetime
import sys

# --- Configuration --- (UNCHANGED)
API_ID = '23359622'
API_HASH = '6dcf7c69c12b1dd770b569e8684256df'
GROUP_ID = -1002606862659

if len(sys.argv) > 1:
    SESSION_NAME = sys.argv[1]
    print(f"Using session name from argument: {SESSION_NAME}")
else:
    SESSION_NAME = 'grabber_bot_default'
    print(f"No session name provided. Using default: {SESSION_NAME}")

# --- Logging Setup --- (UNCHANGED)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=f'grabber_{SESSION_NAME}.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

async def main():
    try:
        api_id_int = int(API_ID)
    except ValueError:
        print("🚨 Error: API_ID in your script is not a valid number. Please check it.")
        logger.error("🚨 Invalid API_ID format. It should be an integer.")
        return

    client = TelegramClient(SESSION_NAME, api_id_int, API_HASH)

    print("=== Telegram Auto-Claimer (Optimized Button Click) ===")
    logger.info("Bot starting with optimized button click...")

    try:
        print("🔄 Connecting to Telegram...")
        await client.connect()

        if not await client.is_user_authorized():
            print("🔑 Authentication required (first run or session expired).")
            phone_number = input("📱 Please enter your phone number (with country code, e.g., +12345678900): ")
            await client.send_code_request(phone_number)
            try:
                code = input("🔢 Please enter the verification code you received: ")
                await client.sign_in(phone=phone_number, code=code)
            except Exception as auth_err:
                print(f"🚨 Authentication failed: {auth_err}")
                logger.error(f"Authentication failed: {auth_err}")
                await client.disconnect()
                return
        
        myself = await client.get_me()
        print(f"\n✅ Successfully logged in as: {myself.first_name} (ID: {myself.id})")
        logger.info(f"Logged in as {myself.first_name} (ID: {myself.id})")
        
        try:
            print(f"🔍 Verifying access to Group ID: {GROUP_ID}...")
            target_group_entity = await client.get_entity(GROUP_ID)
            if not hasattr(target_group_entity, 'title'):
                    raise ValueError(f"ID {GROUP_ID} does not appear to be a group or channel.")
            print(f"👀 Monitoring Group: '{target_group_entity.title}' (Resolved ID: {target_group_entity.id})")
            logger.info(f"Successfully accessed and will monitor Group: '{target_group_entity.title}' (ID: {target_group_entity.id})")
        except ValueError as ve:
            print(f"🚨 Error with Group ID {GROUP_ID}: {ve}")
            logger.error(f"ValueError accessing group {GROUP_ID}: {ve}")
            await client.disconnect()
            return
        except Exception as e:
            print(f"🚨 Could not find or access group with ID {GROUP_ID}. Error: {e}")
            logger.error(f"Error accessing group {GROUP_ID}: {e}")
            await client.disconnect()
            return

        print("🔥 Ready to claim any 'CLAIM' button automatically!")
        print("👂 Listening for new messages... Press CTRL+C to stop.\n")

    except Exception as e:
        print(f"🚨 An error occurred during startup: {e}")
        logger.critical(f"Critical startup error: {e}", exc_info=True)
        if client.is_connected():
            await client.disconnect()
        return

    @client.on(events.NewMessage(chats=target_group_entity))
    async def handler(event):
        message_id = event.message.id
        message_text_preview = event.message.text[:70] if event.message.text else "N/A"

        # OPTIMIZED BUTTON CLICK - Only change made to original script
        if event.message.reply_markup:
            try:
                # Directly click the CLAIM button without scanning all buttons
                await event.message.click(text='CLAIM')
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] 🚀 CLAIMED! (MsgID: {message_id})")
                logger.info(f"✅ SUCCESS: CLAIMED (MsgID: {message_id}). Original message: {message_text_preview}...")
            except Exception as click_err:
                logger.error(f"⚠️ FAILED to click CLAIM button (MsgID: {message_id}): {click_err}")

    try:
        await client.run_until_disconnected()
    finally:
        if client.is_connected():
            print("🔌 Disconnecting client...")
            await client.disconnect()
        logger.info("Bot stopped and client disconnected.")
        print("\n🔌 Client disconnected.")

if __name__ == '__main__':
    print("🚀 Starting bot script...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot manually stopped by user (Ctrl+C).")
        logger.info("Bot manually stopped by user via KeyboardInterrupt.")
    except Exception as e:
        print(f"💥 A critical unhandled error occurred in the main execution block: {e}")
        logger.critical(f"Unhandled crash in __main__: {e}", exc_info=True)
