import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import UpdateNewChannelMessage, Message, ReplyInlineMarkup, KeyboardButtonCallback
import logging
import sys

# --- Configuration (Filled from your details) ---
API_ID = '23359622'
API_HASH = '6dcf7c69c12b1dd770b569e8684256df'
GROUP_ID = -1002606862659

# --- Session and Logging Setup ---
if len(sys.argv) > 1:
    SESSION_NAME = sys.argv[1]
else:
    SESSION_NAME = 'grabber_bot_low_level' # Default for this new script
print(f"Using session name: {SESSION_NAME}")

LOG_FILE_NAME = f'grabber_{SESSION_NAME}.log'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=LOG_FILE_NAME,
    filemode='a'
)
logger = logging.getLogger(__name__)

# --- Main Application ---
async def main():
    logger.info("Bot starting in LOW-LEVEL, HIGH-PERFORMANCE mode.")
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)

    # --- Low-Level Event Handler ---
    # This is the core of the new, faster approach.
    # It hooks into raw data before Telethon fully processes it.
    @client.on(events.Raw(UpdateNewChannelMessage))
    async def fast_handler(event):
        # The event is UpdateNewChannelMessage
        # Its .message attribute contains a Message object
        message = event.message

        # 1. Quick check: Is this message for our target group?
        # The group ID is in message.peer_id.channel_id
        if not hasattr(message, 'peer_id') or not hasattr(message.peer_id, 'channel_id') or message.peer_id.channel_id != abs(GROUP_ID) - 1000000000000:
            return

        # 2. Quick check: Does the message have an inline keyboard?
        if not isinstance(message.reply_markup, ReplyInlineMarkup):
            return

        # 3. Iterate and click with maximum speed
        for row in message.reply_markup.rows:
            for button in row.buttons:
                # We are looking for a KeyboardButtonCallback which can be clicked
                if isinstance(button, KeyboardButtonCallback) and "CLAIM" in button.text.upper():
                    try:
                        # Request to click the button. We don't wait for the result here,
                        # we just fire and forget to be as fast as possible.
                        await client.request(
                            functions.messages.GetBotCallbackAnswerRequest(
                                peer=message.peer_id,
                                msg_id=message.id,
                                data=button.data
                            )
                        )
                        logger.info(f"🚀 FIRED CLAIM! (Button: '{button.text}', MsgID: {message.id})")
                        return # Exit immediately after firing the claim
                    except Exception as e:
                        logger.error(f"⚠️ FAILED to fire claim for MsgID {message.id}. Reason: {e}")
                        return

    # --- Standard Connection Logic ---
    async with client:
        myself = await client.get_me()
        logger.info(f"✅ Logged in as {myself.first_name}")
        logger.info("🔥 Low-level handler is active. Listening for raw updates...")
        await client.run_until_disconnected()

if __name__ == "__main__":
    # We need to import the functions for the raw request
    from telethon.tl import functions
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot manually stopped.")
    except Exception as e:
        logger.critical(f"💥 A critical error occurred: {e}", exc_info=True)
