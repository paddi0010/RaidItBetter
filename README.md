A small, secure desktop app built with Python and CustomTkinter to fire off Twitch raids quickly from your desktop—no browser dashboard gymnastics required.

## Why this exists

Twitch's native dashboard is clunky when you're trying to wrap up a stream and send your community off somewhere else fast. This tool keeps a list of your favorite streamer shortcuts, handles local authentication securely, and triggers the Twitch Helix API directly with a single click.

## What's under the hood

* **GUI:** CustomTkinter for a clean dark-mode interface that doesn't look like it's straight out of 1998.
* **Auth:** OAuth2 Authorization Code Flow with PKCE using a local callback server.
* **Security First:** Access tokens never live in plaintext JSON files; they're stored directly in your OS keychain via `keyring`. Includes CSRF protection (`state`) and basic input regex validation.