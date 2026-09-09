# ⚡ RaidItBetter *(Alpha)*

> ⚠️ **Heads up:** This project is currently in early **alpha**. Core features work, but expect a few rough edges or minor bugs while things are still actively being built.

A small, secure desktop app built with Python and CustomTkinter to fire off Twitch raids quickly from your desktop—no browser dashboard gymnastics required.

## Why this exists

Twitch's native dashboard is clunky when you're trying to wrap up a stream and send your community off somewhere else fast. This tool keeps a list of your favorite streamer shortcuts, handles local authentication securely, and triggers the Twitch Helix API directly with a single click.

## What's under the hood

* **GUI:** CustomTkinter for a clean dark-mode interface that doesn't look like it's straight out of 1998.
* **Auth:** OAuth2 Authorization Code Flow with PKCE using a local callback server.
* **Security First:** Access tokens never live in plaintext JSON files; they're stored directly in your OS keychain via `keyring`. Includes CSRF protection (`state`) and basic input regex validation.

## 🚀 Installation & Getting Started

### Option 1: Running from Source (Recommended & Stable)
The most reliable way to run the application without encountering Windows security blocks is directly via the source code:

1. **Install Python**: Download and install Python from the official [Python website](https://www.python.org/downloads/)[cite: 1]. Make sure to check the box **"Add Python to PATH"** during installation.
2. **Download the Project**: Go to the top of this GitHub repository, click the green **Code** button, and select **Download ZIP**. Extract the ZIP file to a folder of your choice.
3. **Get your Twitch API Credentials**:
   * Go to the [Twitch Developer Console](https://dev.twitch.tv/console) and log in with your Twitch account.
   * Navigate to **Applications** and click **Register Your Application**.
   * Give it a name (e.g., `RaidItBetter`), set the OAuth Redirect URL to `http://localhost:3000`, and select **Chat Bot** or **Website** as the category. Click **Create**.
   * Copy your generated **Client ID**. Then, click **New Secret** to generate and copy your **Client Secret**.
4. **Configure API Access**: 
   * Find the file named `config.example.py` inside the extracted project folder.
   * Make a copy of it and rename the copy to **`config.py`**.
   * Open `config.py` with any text editor (like Notepad), paste your Twitch `CLIENT_ID` and `CLIENT_SECRET`, and save the file.
5. **Open the Terminal**: Open the extracted project folder in Windows Explorer, click into the address bar at the top, type **`cmd`**, and press **Enter**.
6. **Install Dependencies**: Run the following command in the terminal window that opens:
   ```cmd
   pip install -r requirements.txt
7. Launch the Application: Start the app by running
   ```cmd
   python main.py
