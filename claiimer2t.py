# Script: S2 - Corrected High-Speed Auto-Claimer
import asyncio
from telethon import TelegramClient, events
import logging
from datetime import datetime
import sys

# --- Configuration ---
# Ensure these are correct
API_ID = '23359622'
API_HASH = '6dcf7c69c12b1dd770b569e8684256df'
GROUP_ID = -1002606862659 # The specific group/channel ID to monitor

# --- Session Naming (from command line) ---
if len(sys.argv) > 1:
    SESSION_NAME = sys.argv[1]
    print(f"Using session name from argument: {SESSION_NAME}")
else:
    # Using a default session name if none is provided
    SESSION_NAME = 'grabber_bot_default'
    print(f"No session name provided. Using default: {SESSION_NAME}")

# --- Logging Setup ---
# Logs are saved to a file unique to the session name
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=f'grabber_{SESSION_NAME}.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# --- Core Logic ---
async def main():
    """
    Main function to connect the client, set up handlers, and run the bot.
    """
    try:
        api_id_int = int(API_ID)
    except ValueError:
        print("🚨 Error: API_ID in your script is not a valid number. Please check it.")
        logger.error("🚨 Invalid API_ID format. It should be an integer.")
        return

    client = TelegramClient(SESSION_NAME, api_id_int, API_HASH)

    print("=== Telegram Auto-Claimer (S2: Corrected High-Speed Mode) ===")
    logger.info("Bot starting in S2 Corrected High-Speed mode...")

    try:
        print("🔄 Connecting to Telegram...")
        await client.connect()

        if not await client.is_user_authorized():
            print("🔑 Authentication required (first run or session expired).")
            phone_number = input("📱 Please enter your phone number (with country code): ")
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
            print(f"👀 Monitoring Group: '{target_group_entity.title}' (ID: {target_group_entity.id})")
            logger.info(f"Successfully accessed and will monitor Group: '{target_group_entity.title}' (ID: {target_group_entity.id})")
        except Exception as e:
            print(f"🚨 Could not find or access group with ID {GROUP_ID}. Error: {e}")
            logger.error(f"Error accessing group {GROUP_ID}: {e}")
            await client.disconnect()
            return

        print("🔥 Ready to claim! Listening for the first button on new messages...")
        print("👂 Press CTRL+C to stop.\n")

    except Exception as e:
        print(f"🚨 An error occurred during startup: {e}")
        logger.critical(f"Critical startup error: {e}", exc_info=True)
        if client.is_connected():
            await client.disconnect()
        return

    # --------------------------------------------------------------------
    # CORE HANDLER: This is the new, corrected, high-speed logic.
    # --------------------------------------------------------------------
    @client.on(events.NewMessage(chats=target_group_entity))
    async def high_speed_handler(event: events.NewMessage.Event):
        """
        This handler is optimized for speed. It assumes the target button is
        always the first one and clicks it without any checks or loops.
        """
        # A message with buttons has a 'reply_markup'. This is a fast and essential check.
        if event.message.reply_markup:
            try:
                # CORRECTION: Use event.message.click(0, 0)
                # This is the correct, documented, and fastest way to click the
                # button at the first row (index 0) and first column (index 0).
                await event.message.click(0, 0)

                # Log success after the click.
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Timestamp with milliseconds
                print(f"[{timestamp}] 🚀 CLAIMED! (Clicked button at [0,0] on MsgID: {event.message.id})")
                logger.info(f"✅ SUCCESS: Clicked button at position [0,0] on MsgID: {event.message.id}.")

            except Exception as e:
                # Catch any error during the click, e.g., if the button is expired
                # or the message doesn't have a button at position [0,0].
                # This prevents the script from crashing.
                logger.error(f"⚠️ FAILED to click button on MsgID {event.message.id}: {e}", exc_info=False)
                # To keep the console clean, we will not print every error,
                # but you can uncomment the line below for debugging if needed.
                # print(f"⚠️ Error clicking button on MsgID {event.message.id}: {e}")

    # --------------------------------------------------------------------

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
