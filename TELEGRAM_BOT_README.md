# Telegram Bot for XO_OS

This bot allows you to forward ICS schedules from external bots (like @Timetable_MAI_bot) to your XO_OS instance for automatic import into Google Calendar.

## Setup

1. Install dependencies:
   ```bash
   python -m pip install -e ".[dev,google,telegram]"
   ```

2. Set environment variables:
   - `TELEGRAM_BOT_TOKEN`: Token from @BotFather
   - `SCHEDULE_ICS_URL`: (Optional) URL to fetch schedule from for `/getschedule` command
   - `APP_URL`: Base URL of your XO_OS app (default: http://localhost:8000)

3. Run the bot:
   ```bash
   xo-os-bot
   ```

## Usage

### Forwarding from external bot
1. In Telegram, chat with @Timetable_MAI_bot (or any other schedule bot) and request the schedule (e.g., send `/today` or `/week`).
2. When the bot sends you an `.ics` file, use the "Forward" option to forward it to this bot.
3. The bot will automatically send the file to your XO_OS instance and report the import result.

### Direct URL fetch (optional)
If you set `SCHEDULE_ICS_URL`, you can use the `/getschedule` command to have the bot fetch the schedule from that URL and import it.

## How it works
- The bot accepts any document message.
- If the document has a `.ics` extension or MIME type `text/calendar`, it is downloaded and sent to the XO_OS `/import-ics` endpoint.
- The endpoint processes the ICS file, updates the local database, and synchronizes with Google Calendar.