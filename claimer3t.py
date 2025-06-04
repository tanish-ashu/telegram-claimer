import asyncio
from telethon import TelegramClient, events
import logging
from datetime import datetime
# import random # If you uncomment any random.sleep

# --- Configuration ---
API_ID = '23359622' # Your API ID
API_HASH = '6dcf7c69c12b1dd770b569e8684256df' # Your API Hash
GROUP_ID = -2606862659 # Your corrected group ID
SESSION_NAME = 'grabber_bot'

# --- Logging Setup ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='grabber.log',
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

    print("=== Telegram Auto-Claimer (Simplified Mode) ===")
    logger.info("Bot starting in simplified claim mode...")

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

        # Simplified logic: if a message has buttons, check for a "CLAIM" button.
        if event.message.reply_markup and hasattr(event.message.reply_markup, 'rows'):
            logger.info(f"Message {message_id} has reply markup. Scanning for 'CLAIM' button...")
            for row_index, row in enumerate(event.message.reply_markup.rows):
                for button_index, current_button in enumerate(row.buttons):
                    # Check for the "CLAIM" button (ensure text matching is precise for "✅ CLAIM")
                    if hasattr(current_button, 'text') and isinstance(current_button.text, str) and "CLAIM" in current_button.text.upper():
                        # The screenshot showed "✅ CLAIM", so we might need to be specific if "CLAIM" alone is too broad.
                        # For now, "CLAIM" in upper case will find "✅ CLAIM", "Claim", "claim order" etc.
                        # If you need exact "✅ CLAIM", change to: current_button.text == "✅ CLAIM"
                        
                        button_text_found = current_button.text
                        logger.info(f"🔘 Potential 'CLAIM' button found: '{button_text_found}' (Type: {type(current_button)}) on MsgID: {message_id}. Attempting to click...")
                        
                        clicked_successfully = False
                        try:
                            # Method 1: Try clicking using the button's 'data' (most common for callback buttons)
                            if hasattr(current_button, 'data') and current_button.data is not None:
                                logger.info(f"Attempting click with button.data: {bytes(current_button.data)!r}")
                                await event.message.click(data=current_button.data)
                                clicked_successfully = True
                            # Method 2: Fallback to clicking by button's exact text if 'data' isn't suitable/available
                            elif hasattr(current_button, 'text') and current_button.text is not None:
                                logger.info(f"Button has no .data or it's None. Attempting click with exact button.text: '{current_button.text}'")
                                await event.message.click(text=current_button.text)
                                clicked_successfully = True
                            else:
                                logger.warning(f"Button '{button_text_found}' on MsgID {message_id} has no suitable .data or .text for clicking.")

                            if clicked_successfully:
                                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                print(f"[{timestamp}] 🚀 CLAIMED! (Button: '{button_text_found}' on MsgID: {message_id})")
                                logger.info(f"✅ SUCCESS: CLAIMED via button '{button_text_found}' (MsgID: {message_id}). Original message: {message_text_preview}...")
                                return # Successfully claimed one button, exit handler for this message
                        
                        except TypeError as te:
                            if "unexpected keyword argument" in str(te).lower():
                                error_detail = str(te)
                                logger.error(f"⚠️ FAILED to click 'CLAIM' button due to 'unexpected keyword argument'. Your Telethon version might not support the specific click method used (e.g., 'data=' or 'text='). Error: {error_detail}", exc_info=True)
                                print(f"⚠️ Error clicking button (MsgID: {message_id}, Text: '{button_text_found}'): Click method not supported by Telethon version: {error_detail}")
                            else: # Other TypeErrors
                                logger.error(f"⚠️ TypeError while clicking 'CLAIM' button (MsgID: {message_id}, Button text: '{button_text_found}'): {te}", exc_info=True)
                                print(f"⚠️ TypeError clicking button (MsgID: {message_id}, Text: '{button_text_found}'): {te}")
                        except Exception as click_err: # Catch other potential errors during click
                            logger.error(f"⚠️ FAILED to click 'CLAIM' button (MsgID: {message_id}, Button text: '{button_text_found}'): {click_err}", exc_info=True)
                            print(f"⚠️ Error clicking button (MsgID: {message_id}, Text: '{button_text_found}'): {click_err}")
            # If loop finishes, no claimable button was actioned in this message.
            # logger.info(f"No 'CLAIM' button found or clicked in message {message_id} with reply markup.")
        # else:
            # logger.debug(f"Message {message_id} has no reply markup or no rows attribute. Skipping.")

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
