import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest

API_ID = '23359622'
API_HASH = '6dcf7c69c12b1dd770b569e8684256df'
SESSION_NAME = 'grabber_bot_temp' # Use a different session name to avoid conflicts

async def get_group_id():
    client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
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
            await client.disconnect()
            return

    print("\nLogged in. Now, let's find the correct ID for your group/channel.")
    print("You can try entering its username (e.g., 'my_group_username') or its current ID (e.g., 2606862659).")

    while True:
        entity_input = input("Enter group/channel username or its current known ID: ")
        try:
            # Try to get entity by username first (if provided) or by the integer ID
            if entity_input.startswith('-100') or entity_input.isdigit(): # If it looks like an ID
                target_entity = await client.get_entity(int(entity_input))
            else: # Assume it's a username
                target_entity = await client.get_entity(entity_input)

            print(f"\nFound Entity:")
            print(f"  Title: {getattr(target_entity, 'title', 'N/A')}")
            print(f"  ID: {target_entity.id}")
            print(f"  Type (Peer): {type(target_entity)}")

            if hasattr(target_entity, 'megagroup') and target_entity.megagroup:
                print(f"  This is a MegaGroup/Channel.")
                print(f"  The correct GROUP_ID for your script should be: {target_entity.id}")
                print("\nPlease update the 'GROUP_ID' variable in your `claimer3t.py` script with this value.")
            elif hasattr(target_entity, 'channel') and target_entity.channel:
                print(f"  This is a Channel.")
                print(f"  The correct GROUP_ID for your script should be: {target_entity.id}")
                print("\nPlease update the 'GROUP_ID' variable in your `claimer3t.py` script with this value.")
            elif hasattr(target_entity, 'chat') and target_entity.chat:
                print(f"  This is a regular Chat.")
                print(f"  The correct GROUP_ID for your script should be: {target_entity.id}")
                print("\nPlease update the 'GROUP_ID' variable in your `claimer3t.py` script with this value.")
            else:
                print(f"  This is an unknown entity type. Its ID is {target_entity.id}.")
                print(f"  If it's a private chat, try sending a message to it first, then check the 'id' in the `PeerUser` or `PeerChat` object.")

            break # Exit loop if entity found
        except ValueError as ve:
            print(f"🚨 Error: {ve}. Please ensure the ID is correct or the username is valid.")
        except Exception as e:
            print(f"🚨 An error occurred: {e}. Please check your input and try again.")

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(get_group_id())
