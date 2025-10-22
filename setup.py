import asyncio
import configparser
from pyrogram import Client

async def main():
    print("--- Cloner Userbot Configuration Wizard ---")
    print("First, you need to obtain an api_id and api_hash.")
    print("You can do this on the website my.telegram.org\n")

    api_id = input("Enter your api_id: ").strip()
    api_hash = input("Enter your api_hash: ").strip()

    if not api_id.isdigit():
        print("\n[ERROR] api_id must consist of numbers only. Please restart the configuration.")
        return

    config = configparser.ConfigParser()
    config['pyrogram'] = {
        'api_id': api_id,
        'api_hash': api_hash
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    print("\n[OK] The config.ini configuration file has been successfully saved.")

    print("Now you need to log in to Telegram...")
    try:
        async with Client("cloner", api_id=api_id, api_hash=api_hash) as app:
            me = await app.get_me()
            print(f"\n[SUCCESS] Authorization was successful.")
            print(f"You are logged in as: {me.first_name} (@{me.username})")
            print("The session file ‘cloner.session’ has been created.")

    except Exception as e:
        print(f"\n[ERROR] An error occurred during authorization: {e}")
        print("Please check the information you entered and try again.")
        return

    print("\n--- Setup complete! ---")
    print("Now you can run the main bot with the command: python main.py")

if __name__ == "__main__":
    asyncio.run(main())
