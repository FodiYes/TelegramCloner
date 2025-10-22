import asyncio
import configparser
import os
import json
import logging
from pyrogram import Client, idle

from modules.cloner_module import clone_handler, revert_handler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONFIG_FILE = "config.ini"
SESSION_NAME = "cloner"
BACKUP_PROFILE_FILE = "profile_backup.json"
BACKUP_AVATAR_FILE = "backup_avatar.jpg"

async def create_backup(app: Client):
    try:
        me = await app.get_me()

        if not os.path.exists(BACKUP_PROFILE_FILE):
            logger.info("Backing up profile text data...")
            full_user = await app.get_chat(me.id) # get_chat | bio

            backup_data = {
                "first_name": me.first_name or "",
                "last_name": me.last_name or "",
                "username": me.username,
                "bio": full_user.bio or ""
            }

            with open(BACKUP_PROFILE_FILE, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Profile data saved in {BACKUP_PROFILE_FILE}")
            print("[INFO] A backup copy of your profile text data has been successfully created.")
        else:
            logger.info("The text data backup file already exists. Skip.")

        if me.photo and not os.path.exists(BACKUP_AVATAR_FILE):
            logger.info("Profile avatar found, but backup file is missing. Creating...")
            try:
                await app.download_media(me.photo.big_file_id, file_name=BACKUP_AVATAR_FILE)
                logger.info(f"Avatar saved in {BACKUP_AVATAR_FILE}")
                print("[INFO] A backup copy of your avatar has been successfully created.")
            except Exception as e:
                logger.error(f"Error creating avatar backup: {e}")
        elif not me.photo:
            logger.info("No avatar is set in your profile. No avatar backup is required.")
        else:
            logger.info("The avatar backup file already exists. Skipping.")

    except Exception as e:
        logger.error(f"Critical error while creating backup: {e}")
        print(f"[ERROR] Failed to create backup: {e}")

async def display_startup_warning():
    """Displays a warning message in the console on startup and waits for user confirmation."""
    warning_box = """
=========================================================================
|                                                                       |
|                          !!! WARNING !!!                              |
|                                                                       |
|  Using .clone and .revert more than 10 times per hour in total        |
|  may result in a temporary 1-hour block on changing your username     |
|  by Telegram. Please use these commands responsibly.                  |
|  To confirm you have read this carefully, type 'sey' (yes backwards)  |
|  and press Enter.                                                     |
|                                                                       |
=========================================================================
"""
    print(warning_box)
    while True:
        raw_confirmation = await asyncio.to_thread(input, "Enter confirmation: ")
        confirmation = raw_confirmation.strip().lower()
        if confirmation == "sey":
            print("Confirmation received. Starting userbot...\n")
            break
        else:
            print("Incorrect confirmation.")

async def main():
    await display_startup_warning()
    if not os.path.exists(CONFIG_FILE):
        print(f"[ERROR] Configuration file '{CONFIG_FILE}' not found.")
        print("Please start first 'python setup.py' for configuration.")
        return

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    api_id = config.get('pyrogram', 'api_id')
    api_hash = config.get('pyrogram', 'api_hash')

    app = Client(
        name=SESSION_NAME,
        api_id=api_id,
        api_hash=api_hash
    )

    app.add_handler(clone_handler)
    app.add_handler(revert_handler)

    async with app:
        await create_backup(app)
        
        me = await app.get_me()
        print("=========================================")
        print(f"Cloner Userbot Started Successfully!")
        print(f"Account: {me.first_name} (@{me.username})")
        print("Available commands:")
        print("  .clone <@username/ID> - clone profile")
        print("  .revert - restore your profile")
        print("=========================================")
        
        await idle()

    print("Userbot stoped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (ValueError, TypeError) as e:
        logger.error(f"Error during startup, possibly due to incorrect configuration: {e}")
        print("\n[ERROR] Unable to start the bot. The session file may be corrupted or the configuration may be incorrect.")
        print("Try deleting the ‘cloner.session’ and ‘config.ini’ files and running ‘setup.py’ again.")
    except Exception as e:
        logger.critical(f"Critical error in the main loop: {e}")
