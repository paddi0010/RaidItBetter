<<<<<<< HEAD
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
=======
# ⚡ RaidItBetter *(Alpha)*

> ⚠️ **Heads up:** This project is currently in early **alpha**. Core features work, but expect a few rough edges or minor bugs while things are still actively being built.

A small, secure desktop app built with Python and CustomTkinter to fire off Twitch raids quickly from your desktop—no browser dashboard gymnastics required.

## Why this exists

Twitch's native dashboard is clunky when you're trying to wrap up a stream and send your community off somewhere else fast. This tool keeps a list of your favorite streamer shortcuts, handles local authentication securely, and triggers the Twitch Helix API directly with a single click.

## What's under the hood

* **GUI:** CustomTkinter for a clean dark-mode interface that doesn't look like it's straight out of 1998.
* **Auth:** OAuth2 Authorization Code Flow with PKCE using a local callback server.
* **Security First:** Access tokens never live in plaintext JSON files; they're stored directly in your OS keychain via `keyring`. Includes CSRF protection (`state`) and basic input regex validation.
>>>>>>> dev
