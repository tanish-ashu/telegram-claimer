# Script: S1 - High-Speed Auto-Claimer
import asyncio
from telethon import TelegramClient, events, functions
from telethon.tl.types import Message
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

    # Connect the client with a reduced update buffer for potentially faster event handling
    client = TelegramClient(SESSION_NAME, api_id_int, API_HASH,
                            device_model="Pixel 6 Pro",
                            system_version="Android 14",
                            app_version="10.13.2"
                           )

    print("=== Telegram Auto-Claimer (S1: High-Speed Mode) ===")
    logger.info("Bot starting in S1 High-Speed mode...")

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
    # CORE HANDLER: This is the new, high-speed logic.
    # --------------------------------------------------------------------
    @client.on(events.NewMessage(chats=target_group_entity))
    async def high_speed_handler(event: events.NewMessage.Event):
        """
        This handler is optimized for speed. It assumes the target button is
        always the first one and clicks it without any checks or loops.
        """
        # A message with buttons has a 'reply_markup'. This is the only check we do.
        if event.message.reply_markup:
            try:
                # OPTIMIZATION: Directly access the first button object.
                # This avoids all loops and text comparisons for maximum speed.
                # Assumes structure: first row (index 0), first button (index 0).
                first_button = event.message.reply_markup.rows[0].buttons[0]

                # ACTION: Click the button directly using its object.
                # This is the fastest way to interact with a callback button.
                await first_button.click()

                # Log success after the click.
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Timestamp with milliseconds
                print(f"[{timestamp}] 🚀 CLAIMED! (Button: '{first_button.text}' on MsgID: {event.message.id})")
                logger.info(f"✅ SUCCESS: Clicked button '{first_button.text}' on MsgID: {event.message.id}.")

            except (IndexError, TypeError):
                # This might happen if a message has a markup but no buttons, which is rare.
                # We log it but don't print to the console to avoid clutter.
                logger.warning(f"Message {event.message.id} had a reply_markup but no button at position (0,0).")
            except Exception as e:
                # Catch other potential errors during the click, e.g., if the
                # button is expired or the click fails for other reasons.
                # This prevents the script from crashing.
                logger.error(f"⚠️ FAILED to click button on MsgID {event.message.id}: {e}")
                print(f"⚠️ Error clicking button on MsgID {event.message.id}: {e}")
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
