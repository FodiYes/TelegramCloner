import logging
import os
import json
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.errors import UsernameNotOccupied, UsernameInvalid, UsernameOccupied

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BACKUP_PROFILE_FILE = "profile_backup.json"
BACKUP_AVATAR_FILE = "downloads/backup_avatar.jpg"
SIGNATURE = "\n\nCoded by [FodiYes](https://github.com/FodiYes)"

async def edit_message_with_signature(message, text):
    """
    Edits a message and adds a signature.
    """
    await message.edit_text(text + SIGNATURE, disable_web_page_preview=True)

def homonimize_username(username: str) -> list:
    if not username:
        return []

    variants = []

    homoglyphs = {
        'l': 'I',
        'I': 'l',
        'o': '0',
        '0': 'o',
        '1' : 'I',
        'S' : '5',
        '5' : 'S',       
    }
    for original, replacement in homoglyphs.items():
        if original in username:
            variant = username.replace(original, replacement, 1)
            if variant not in variants:
                variants.append(variant)
            break

    variants.append(f"{username}1")
    variants.append(f"{username}0")

    if '_' in username:
        variants.append(username.replace('_', '', 1))

    return list(dict.fromkeys(variants))


async def get_target_user(client: Client, message):
    if message.reply_to_message and message.reply_to_message.from_user:
        return await client.get_users(message.reply_to_message.from_user.id)
    
    if len(message.command) > 1:
        target_identifier = message.command[1]
        try:
            return await client.get_users(target_identifier)
        except Exception as e:
            logger.error(f"Can't find user{target_identifier}: {e}")
            await edit_message_with_signature(message, f"❌ User not found: `{target_identifier}`")
            return None
    
    await edit_message_with_signature(message, "❌ Specify the purpose: reply to the message or enter `@username`/`ID` after the command.")
    return None

async def set_profile_photos_and_clear_old(client: Client, photo_paths: list):
    try:
        current_photos = [p.file_id async for p in client.get_chat_photos("me")]
        if current_photos:
            await client.delete_profile_photos(current_photos)
        for photo_path in photo_paths:
            await client.set_profile_photo(photo=photo_path)
            
    except Exception as e:
        logger.error(f"Error when setting a new avatar: {e}")

async def clone_profile(client: Client, message):
    await edit_message_with_signature(message, "🔄 `Starting the cloning process...`")
    
    target_user = await get_target_user(client, message)
    if not target_user:
        return

    first_name = target_user.first_name or ""
    last_name = target_user.last_name or ""
    bio = (await client.get_chat(target_user.id)).bio or ""
    target_username = target_user.username
    
    await edit_message_with_signature(message, f"🎯 **target:** {first_name} {last_name}\n`Downloading avatar...`")

    avatar_paths = []
    if target_user.photo:
        try:
            photos = client.get_chat_photos(target_user.id)
            async for photo in photos:
                path = await client.download_media(photo.file_id)
                avatar_paths.append(path)
            avatar_paths.reverse()
        except Exception as e:
            logger.error(f"Error downloading avatars: {e}")
            await edit_message_with_signature(message, "⚠️ `Unable to download target avatar. Proceeding without it.`")

    new_username = None
    username_changed = False
    if target_username:
        username_variants = homonimize_username(target_username)
        await edit_message_with_signature(message, f"🕹️ `I'm trying to find a similar username...`\nVariants: `{'`, `'.join(username_variants)}`")
        
        for variant in username_variants:
            try:
                await client.set_username(variant)
                new_username = variant
                username_changed = True
                logger.info(f"Username Succesfully changed to {variant}")
                break
            except UsernameOccupied:
                logger.warning(f"Username {variant} is busy.")
                continue
            except (UsernameInvalid, UsernameNotOccupied) as e:
                logger.error(f"Error when changing username to {variant}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error when changing username: {e}")
                break
    
    await client.update_profile(first_name=first_name, last_name=last_name, bio=bio)
    
    if avatar_paths:
        await set_profile_photos_and_clear_old(client, avatar_paths)

    report = f"✅ **The clone is activated.**\n\n"
    report += f"**name:** `{first_name} {last_name}`\n"
    report += f"**bio:** `{bio}`\n"
    if username_changed:
        report += f"**UserName:** `@{new_username}`"
    else:
        report += "**UserName:** `can't be changed`"
        
    await edit_message_with_signature(message, report)


async def revert_profile(client: Client, message):
    await edit_message_with_signature(message, "🔄 `Starting profile recovery...`")
    
    try:
        with open(BACKUP_PROFILE_FILE, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
    except FileNotFoundError:
        await edit_message_with_signature(message, "❌ `The backup file was not found. There is nothing to restore.`")
        return
    
    original_first_name = backup_data.get("first_name", "")
    original_last_name = backup_data.get("last_name", "")
    original_bio = backup_data.get("bio", "")
    original_username = backup_data.get("username")

    await client.update_profile(
        first_name=original_first_name,
        last_name=original_last_name,
        bio=original_bio
    )
    
    username_reverted = False
    if original_username:
        try:
            await client.set_username(original_username)
            username_reverted = True
        except Exception as e:
            logger.error(f"Unable to restore username {original_username}: {e}")
    else:
        try:
            await client.set_username(None)
            username_reverted = True
        except UsernameNotOccupied:
            username_reverted = True
        except Exception as e:
            logger.error(f"Unable to delete username: {e}")

    if os.path.exists(BACKUP_AVATAR_FILE):
        try:
            await set_profile_photos_and_clear_old(client, [BACKUP_AVATAR_FILE])
        except Exception as e:
            logger.error(f"Unable to restore avatar: {e}")
    else:
        logger.warning("Avatar backup file not found, skip recovery.")

    report = "🔄 **Profile successfully restored.**\n\n"
    report += f"**Name:** `{original_first_name} {original_last_name}`\n"
    if username_reverted:
        report += f"**Username:** `@{original_username}`" if original_username else "`deleted`"
    else:
        report += f"**Username:** `can't be restored`"
        
    await edit_message_with_signature(message, report)

clone_handler = MessageHandler(clone_profile, filters.command("clone", prefixes=".") & filters.me)
revert_handler = MessageHandler(revert_profile, filters.command("revert", prefixes=".") & filters.me)
