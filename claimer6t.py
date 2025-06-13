import asyncio
import uvloop
uvloop.install()  # Replace asyncio event loop for better performance

from telethon import TelegramClient, events
import logging
from datetime import datetime
import sys
import random  # Added for random delays

# --- Configuration ---
API_ID = '23359622'
API_HASH = '6dcf7c69c12b1dd770b569e8684256df'
GROUP_ID = -1002606862659

# Determine SESSION_NAME from command-line argument
if len(sys.argv) > 1:
    SESSION_NAME = sys.argv[1]
    print(f"Using session name from argument: {SESSION_NAME}")
else:
    SESSION_NAME = 'grabber_bot_default'
    print(f"No session name provided. Using default: {SESSION_NAME}")

# --- Logging Setup ---
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

    # Initialize client with IPv4 only and optimized settings
    client = TelegramClient(
        SESSION_NAME,
        api_id_int,
        API_HASH,
        use_ipv6=False,  # Force IPv4 for better routing
        connection_retries=5,
        auto_reconnect=True
    )

    print("=== Telegram Auto-Claimer (Optimized Mode) ===")
    logger.info("Bot starting with uvloop optimization...")

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

        if event.message.reply_markup and hasattr(event.message.reply_markup, 'rows'):
            logger.info(f"Message {message_id} has reply markup. Scanning for 'CLAIM' button...")
            for row_index, row in enumerate(event.message.reply_markup.rows):
                for button_index, current_button in enumerate(row.buttons):
                    if hasattr(current_button, 'text') and isinstance(current_button.text, str) and "CLAIM" in current_button.text.upper():
                        button_text_found = current_button.text
                        logger.info(f"🔘 Potential 'CLAIM' button found: '{button_text_found}' on MsgID: {message_id}. Attempting to click...")
                        
                        clicked_successfully = False
                        try:
                            # Add micro-delay before clicking
                            await asyncio.sleep(random.uniform(0.05, 0.2))  # 50-200ms delay
                            
                            if hasattr(current_button, 'data') and current_button.data is not None:
                                logger.info(f"Attempting click with button.data: {bytes(current_button.data)!r}")
                                await event.message.click(data=current_button.data)
                                clicked_successfully = True
                            elif hasattr(current_button, 'text') and current_button.text is not None:
                                logger.info(f"Button has no .data. Attempting click with exact button.text: '{current_button.text}'")
                                await event.message.click(text=current_button.text)
                                clicked_successfully = True
                            else:
                                logger.warning(f"Button '{button_text_found}' on MsgID {message_id} has no suitable .data or .text.")

                            if clicked_successfully:
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                print(f"[{timestamp}] 🚀 CLAIMED! (Button: '{button_text_found}' on MsgID: {message_id})")
                                logger.info(f"✅ SUCCESS: CLAIMED via button '{button_text_found}' (MsgID: {message_id}).")
                                return
                        
                        except TypeError as te:
                            if "unexpected keyword argument" in str(te).lower():
                                error_detail = str(te)
                                logger.error(f"⚠️ FAILED to click 'CLAIM' button due to 'unexpected keyword argument'. Error: {error_detail}", exc_info=True)
                                print(f"⚠️ Error clicking button (MsgID: {message_id}, Text: '{button_text_found}'): {error_detail}")
                            else:
                                logger.error(f"⚠️ TypeError while clicking 'CLAIM' button: {te}", exc_info=True)
                                print(f"⚠️ TypeError clicking button (MsgID: {message_id}, Text: '{button_text_found}'): {te}")
                        except Exception as click_err:
                            logger.error(f"⚠️ FAILED to click 'CLAIM' button: {click_err}", exc_info=True)
                            print(f"⚠️ Error clicking button (MsgID: {message_id}, Text: '{button_text_found}'): {click_err}")

    try:
        await client.run_until_disconnected()
    finally:
        if client.is_connected():
            print("🔌 Disconnecting client...")
            await client.disconnect()
        logger.info("Bot stopped and client disconnected.")
        print("\n🔌 Client disconnected.")

if __name__ == '__main__':
    print("🚀 Starting bot script with uvloop optimization...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot manually stopped by user (Ctrl+C).")
        logger.info("Bot manually stopped by user via KeyboardInterrupt.")
    except Exception as e:
        print(f"💥 A critical unhandled error occurred: {e}")
        logger.critical(f"Unhandled crash in __main__: {e}", exc_info=True)
