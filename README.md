# ⚡ RaidItBetter

Ein schlankes, sicheres Desktop-Tool für Twitch-Streamer, um schnell und unkompliziert Raids zu starten – inklusive Favoriten-Verwaltung und modernem PKCE-OAuth-Login.

## Features
- **Modernes UI:** Dunkles Design im Twitch-Style (gebaut mit CustomTkinter).
- **Sicherer Login:** Vollständiger OAuth2-Login mit PKCE und CSRF-Schutz.
- **Sichere Token-Speicherung:** Nutzt den betriebssystemeigenen Tresor (`keyring`) statt Klartext-Dateien.
- **Favoriten-Liste:** Speichere häufig geraidete Streamer lokal ab.

## Installation & Start

1. Repository klonen oder herunterladen:
   ```bash
   git clone [https://github.com/DEIN-BENUTZERNAME/twitch-raid-tool.git](https://github.com/DEIN-BENUTZERNAME/twitch-raid-tool.git)
   cd twitch-raid-tool