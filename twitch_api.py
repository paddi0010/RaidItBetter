import base64
import hashlib
import os
import secrets
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
import keyring
from config import CLIENT_ID, REDIRECT_URI

SERVICE_NAME = "RaidItBetter"
TOKEN_KEY = "twitch_access_token"

class TwitchOAuthHandler(BaseHTTPRequestHandler):
    auth_code = None
    expected_state = None
    received_state = None

    def do_GET(self):
        if self.path.startswith("/callback"):
            query_components = parse_qs(urlparse(self.path).query)

            if "code" in query_components:
                TwitchOAuthHandler.auth_code = query_components["code"][0]

            if "state" in query_components:
                TwitchOAuthHandler.auth_code = query_components["state"][0]
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = """
            <html>
                <body style="background-color: #121212; color: white; font-family: sans-serif; text-align: center; padding-top: 50px;">
                    <h2>Login erfolgreich!</h2>
                    <p>Du kannst dieses Fenster jetzt schließen und zur App zurückkehren.</p>
                </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
            threading.Thread(target=self.server.shutdown).start()

    def log_message(self, format, *args):
        pass


class TwitchClient:
    def __init__(self):
        self.access_token = self.load_token()
        self.code_verifier = None
        self.current_state = None

    def load_token(self):
        try:
            return keyring.get_password(SERVICE_NAME, TOKEN_KEY)
        except:
            return None

    def save_token(self, token):
        self.access_token = token
        try:
            keyring.set_password(SERVICE_NAME, TOKEN_KEY, token)
        except Exception as e:
            print(f"Fehler beim Speichern im Keyring: {e}")

    def generate_pkce_pairs(self):
        verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('utf-8')
        
        sha256_hash = hashlib.sha256(verifier.encode('utf-8')).digest()
        challenge = base64.urlsafe_b64encode(sha256_hash).rstrip(b'=').decode('utf-8')
        
        return verifier, challenge

    def start_login(self, callback_on_success):
        if CLIENT_ID == "DEINE_CLIENT_ID_HIER":
            return False, "❌ Bitte trage deine Client ID in config.py ein!"

        self.code_verifier, code_challenge = self.generate_pkce_pairs()

        self.current_state = secrets.token_urlsafe(16)
        TwitchOAuthHandler.expected_state = self.current_state

        auth_url = (
            f"https://id.twitch.tv/oauth2/authorize"
            f"?client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&response_type=code"
            f"&scope=channel:manage:raids"
            f"&code_challenge={code_challenge}"
            f"&code_challenge_method=S256"
            f"&state={self.current_state}"
        )
        
        webbrowser.open(auth_url)

        def run_server():
            try:
                server = HTTPServer(("localhost", 3000), TwitchOAuthHandler)
                TwitchOAuthHandler.auth_code = None
                TwitchOAuthHandler.received_state = None
                server.serve_forever()

                if TwitchOAuthHandler.received_state != self.current_state:
                    print("Sicherheitsfehler: State-Wert stimmt nicht überein. (Möglicher CSRF-Angriff)")
                    return
                
                if TwitchOAuthHandler.auth_code:
                    if self.exchange_code_for_token(TwitchOAuthHandler.auth_code):
                        callback_on_success()
            except OSError:
                print("Port 3000 ist bereits belegt.")

        threading.Thread(target=run_server, daemon=True).start()
        return True, "🌐 Browser für Twitch-Login geöffnet..."

    def exchange_code_for_token(self, code):
        token_url = "https://id.twitch.tv/oauth2/token"
        payload = {
            "client_id": CLIENT_ID,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "code_verifier": self.code_verifier
        }

        try:
            response = requests.post(token_url, data=payload, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                if access_token:
                    self.save_token(access_token)
                    return True
            return False
        except:
            return False

    def execute_raid(self, target_name):
        if not self.access_token:
            return False, "❌ Bitte zuerst mit Twitch einloggen!"

        headers = {
            "Client-ID": CLIENT_ID,
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            user_res = requests.get("https://api.twitch.tv/helix/users", headers=headers, timeout=10)
            if user_res.status_code != 200:
                return False, "❌ Token abgelaufen oder ungültig. Bitte neu einloggen."
            
            broadcaster_id = user_res.json()["data"][0]["id"]

            target_res = requests.get(f"https://api.twitch.tv/helix/users?login={target_name}", headers=headers, timeout=10)
            target_json = target_res.json().get("data", [])
            
            if not target_json:
                return False, f"❌ Streamer '{target_name}' nicht gefunden!"
            
            target_id = target_json[0]["id"]

            raid_url = f"https://api.twitch.tv/helix/raids?from_broadcaster_id={broadcaster_id}&to_broadcaster_id={target_id}"
            raid_res = requests.post(raid_url, headers=headers, timeout=10)

            if raid_res.status_code == 200:
                return True, f"🚀 Raid auf {target_name} erfolgreich gestartet!"
            else:
                error_msg = raid_res.json().get("message", "Unbekannter Fehler")
                return False, f"❌ Fehler: {error_msg}"

        except requests.exceptions.Timeout:
            return False, "❌ Zeitüberschreitung bei der Verbindung zu Twitch."
        except Exception:
            return False, "❌ Netzwerkfehler aufgetreten."