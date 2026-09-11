# XO_OS Web Version

This document describes how to run the web version of XO_OS.

## Prerequisites

- Python 3.9+
- Required Python packages (see [Dependencies](#dependencies))
- A Google Calendar API credentials file (if you want to use Google Calendar synchronization)
- An Obsidian vault path (if you want to use Obsidian export)

## Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, you can install the packages manually:

```bash
pip install fastapi uvicorn python-telegram-bot python-dotenv google-api-python-client google-auth-httplib2 google-auth-oauthlib icalendar sqlalchemy
```

## Running the Web Version

1. Set up environment variables (create a `.env` file or set them in your environment):

   ```bash
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   GOOGLE_CALENDAR_NAME=ВУЗ МАИ  # or your calendar name
   OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
   ```

   For Google Calendar API, you need to place your `credentials.json` and `token.json` in the `secrets/` directory (or adjust the path in `app/google_calendar/auth.py`).

2. Start the server:

   ```bash
   uvicorn app.main:app --reload
   ```

   The server will be available at `http://localhost:8000`.

3. Open your browser and go to `http://localhost:8000` to see the interface.

## API Endpoints

The API is available under the `/api` prefix:

- `GET /api/health` - Health check
- `POST /api/import-ics` - Import an ICS file (multipart/form-data) with optional `calendar` query parameter
- `POST /api/export` - Export lessons to Obsidian vault (optional `vault` query parameter, defaults to `OBSIDIAN_VAULT_PATH` environment variable)

## Project Structure

- `app/web/static/` - Contains the frontend files (HTML, CSS, JavaScript)
- `app/main.py` - The FastAPI application that serves the static files and provides API endpoints
- `app/sync/service.py` - Core synchronization logic
- `app/google_calendar/service.py` - Google Calendar synchronization service
- `app/telegram_bot.py` - Telegram bot (runs separately)

## Development

To modify the interface, edit the files in `app/web/static/`:

- `index.html` - Main HTML structure
- `css/style.css` - Styles
- `js/main.js` - JavaScript functionality

After making changes, reload the page in your browser to see the updates.

## Notes

- The web version does not include the Telegram bot. To run the bot, use `python -m app.telegram_bot` separately.
- The web version uses the same backend logic as the CLI and Telegram bot, ensuring consistency.
- For production, consider using a proper ASGI server like Gunicorn with Uvicorn workers.