# Cloner Userbot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/Library-Pyrogram-orange.svg" alt="Pyrogram">
  <img src="https://img.shields.io/badge/Made%20by-FodiYes-brightgreen" alt="Made by FodiYes">
</p>

**Cloner Userbot** is a standalone Python script for Telegram that allows you to instantly duplicate another user's public information: avatar, first name, last name, profile description (bio), and set a similar username.

## 🚀 Key Features

*   **Full Profile Duplication**: Copies all visible profile elements, including all photos.
*   **Intelligent Username Matching**: Automatically generates and attempts to set an available username similar to the target's.
*   **Backup System**: Automatically saves your original profile on the first run.
*   **Instant Recovery**: The `.revert` command allows you to instantly restore your original profile.
*   **Easy Setup**: An interactive installer will help you quickly set up and run the userbot.

## ⚙️ Installation

The script requires **Python 3.9** or higher.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/FodiYes/Cloner-Userbot.git
    cd Cloner-Userbot
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Complete the initial setup:**
    Run the interactive setup wizard. It will ask for your `api_id` and `api_hash` (which you can get from my.telegram.org) and will authorize your Telegram account.
    ```bash
    python setup.py
    ```

4.  **Run the Userbot:**
    After a successful setup, run the main script.
    ```bash
    python main.py
    ```

## 📋 Commands

All commands are entered in any Telegram chat (e.g., in "Saved Messages").

*   `.clone <Target>`
    - Duplicates the specified user's profile.
    - The **target** can be specified via `@username`, `ID`, or by replying to the user's message.
    - **Example:** `.clone @durov`

*   `.revert`
    - Restores your original profile from the backup.

## ⚠️ Disclaimer

This tool is intended for educational and demonstration purposes only. The author is not responsible for any misuse of this software. By using this script, you assume full responsibility for your actions.

---

Coded by **FodiYes**.