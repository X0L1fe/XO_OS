#!/usr/bin/env python3
"""
Telegram bot for automating schedule import into XO_OS.

The bot accepts an ICS file sent by the user (including forwarded messages) and processes it directly:
   - Save the file to data/received_ics/
   - Import and sync with Google Calendar using the xo-os import CLI
   - Delete the file on success.

To import a schedule from an external bot like @Timetable_MAI_bot:
   1. In Telegram, open a chat with @Timetable_MAI_bot and request the schedule (e.g., send /today, /week, or similar).
   2. Forward the received .ics file to this bot (or use the bot's "Share" → "Forward").
   3. The bot will process the file and import it into your XO_OS instance.

Environment variables:
    TELEGRAM_BOT_TOKEN: Token for the Telegram bot (required).
    GOOGLE_CALENDAR_NAME: Name of the Google Calendar to sync to (defaults to "ВУЗ МАИ").

The bot loads environment variables from a .env file if present.
"""

import os
import logging
import subprocess
import asyncio
import tempfile
from fastapi import HTTPException
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler,
    )
from dotenv import load_dotenv
from app.database.db import Database
from app.telegram.service import (
    get_user_by_telegram_id,
    link_telegram_account,
)

# No application services needed; we delegate to xo-os import CLI

# Load .env file
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
_token = os.getenv("TELEGRAM_BOT_TOKEN")
if _token is None:
    logger.error("TELEGRAM_BOT_TOKEN environment variable is not set.")
    exit(1)
TELEGRAM_BOT_TOKEN: str = _token
GOOGLE_CALENDAR_NAME = os.getenv("GOOGLE_CALENDAR_NAME", "ТЕСТ")

# Ensure directory for received ICS files exists
RECEIVED_ICS_DIR = os.path.join(os.getcwd(), "data", "received_ics")
os.makedirs(RECEIVED_ICS_DIR, exist_ok=True)
db = Database()

async def handle_link_code(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle Telegram account linking code."""

    if not update.message:
        return

    if not update.effective_user:
        return

    code = (update.message.text or "").strip()

    if not code:
        return

    # Не позволяем обычному тексту случайно запускать проверку.
    if len(code) != 10:
        return

    try:
        telegram_id = update.effective_user.id

        with db.session() as db_session:
            user = link_telegram_account(
                db_session,
                code,
                telegram_id,
            )

        try:
            await update.message.delete()
        except Exception as exc:
            logger.warning(
                "Could not delete Telegram link code message: %s",
                exc,
            )

        await update.message.reply_text(
            "✅ Telegram успешно привязан к вашему аккаунту XO_OS."
        )

        logger.info(
            "Telegram %s linked to XO_OS user %s",
            telegram_id,
            user.id,
        )

    except Exception as exc:
        logger.error(
            "Telegram linking failed: %s",
            exc,
        )

        # Не раскрываем внутренние ошибки пользователю.
        await update.message.reply_text(
            "❌ Не удалось привязать Telegram. "
            "Проверьте код и срок его действия."
        )

async def handle_document(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
    ) -> None:
    """Handle incoming document messages (expected to be ICS files)."""
    if not update.effective_user:
        await update.message.reply_text(
            "Не удалось определить Telegram аккаунт."
        )
        return

    if not update.message:
        return
    document = update.message.document
    if not document:
        await update.message.reply_text("No document found.")
        return

    # Check if the document is an ICS file (by filename or mime type)
    filename = document.file_name or ""
    mime_type = document.mime_type or ""
    if not (filename.lower().endswith('.ics') or mime_type == 'text/calendar'):
        await update.message.reply_text("Please send an ICS file.")
        return
    # Проверка на привязку ТГ id
    telegram_id = update.effective_user.id

    with db.session() as db_session:
        user = get_user_by_telegram_id(
            db_session,
            telegram_id,
        )

    if not user:
        await update.message.reply_text(
            "🔒 Telegram не привязан к XO_OS.\n\n"
            "Сначала откройте XO_OS → Настройки → Telegram "
            "и получите код привязки."
        )
        return
    await update.message.reply_text("Downloading the ICS file...")
    try:
        # Download the file
        tg_file = await document.get_file()
        ics_content = bytes(await tg_file.download_as_bytearray())

        # Save file temporarily
        safe_filename = f"{update.message.message_id}_{filename or 'schedule.ics'}"
        file_path = os.path.join(RECEIVED_ICS_DIR, safe_filename)
        with open(file_path, 'wb') as f:
            f.write(ics_content)

        await update.message.reply_text("Importing schedule into XO_OS...")
        result = await process_ics_content(ics_content, source="Upload", file_path=file_path)
        await update.message.reply_text(f"Import result: {result}")

    except Exception as e:
        logger.error(f"Error processing document: {e}")
        if update.message:
            await update.message.reply_text(f"Failed to process the document: {e}")

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка Telegram deep-link:

        https://t.me/BOT_USERNAME?start=CODE

    Telegram отправляет его боту как:

        /start CODE
    """

    if update.effective_user is None:
        return

    telegram_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "Привет! 👋\n\n"
            "Чтобы привязать Telegram к XO_OS, "
            "откройте ссылку привязки из настроек XO_OS."
        )
        return

    code = context.args[0].strip()

    if not code:
        await update.message.reply_text(
            "Код привязки не указан."
        )
        return

    try:
        from app.database.db import Database
        from app.telegram.service import link_telegram_account

        database = Database()

        with database.session() as db_session:
            user = link_telegram_account(
                db_session,
                code,
                telegram_id,
            )

        await update.message.reply_text(
            "✅ Telegram успешно привязан к XO_OS.\n\n"
            f"Аккаунт: {user.name}\n"
            "Теперь этим ботом можно пользоваться "
            "как дополнительным интерфейсом XO_OS."
        )

    except HTTPException as exc:
        await update.message.reply_text(
            f"❌ {exc.detail}"
        )

    except Exception:
        import logging

        logging.exception(
            "Failed to link Telegram account"
        )

        await update.message.reply_text(
            "❌ Не удалось выполнить привязку. "
            "Попробуйте получить новый код в настройках XO_OS."
        )

async def process_ics_content(ics_content: bytes, source: str, file_path: str | None = None) -> str:
    """
    Process ICS content by delegating to the working xo-os import CLI.
    Optionally delete the file if it was saved temporarily.
    Returns a human-readable result string.
    """
    temp_file_path: str | None = None
    try:
        # Save file temporarily if no path provided (ics_content is always bytes)
        if file_path is None:
            temp_fd, temp_file_path = tempfile.mkstemp(suffix='.ics', dir=RECEIVED_ICS_DIR)
            try:
                with os.fdopen(temp_fd, 'wb') as f:
                    f.write(ics_content)
                file_path = temp_file_path
            except Exception:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                raise

        # Run xo-os import command with calendar argument
        process = await asyncio.create_subprocess_exec(
            "xo-os", "import", "--calendar", GOOGLE_CALENDAR_NAME, file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode('utf-8', errors='replace')
            logger.error(f"xo-os import failed: {error_msg}")
            raise RuntimeError(f"Import failed: {error_msg}")

        result_msg = stdout.decode('utf-8', errors='replace').strip()
        logger.info(f"xo-os import successful ({source}): {result_msg}")

        # Delete the temporary file if we saved it
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Deleted temporary ICS file: {file_path}")

        return result_msg or "Import completed successfully"

    except Exception as e:
        logger.exception(f"Error during ICS import from {source}")
        # Clean up temp file if needed
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass
        raise e


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)


def main() -> None:
    """Start the bot."""
    # Create the Application
    application = (
        Application
        .builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", handle_start)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_link_code,
        )
    )
    # Add handlers
    application.add_handler(
        MessageHandler(
            filters.Document.ALL,
            handle_document)
        )

    # Add error handler
    application.add_error_handler(error_handler)

    # Start the Bot
    logger.info("Starting Telegram bot...")
    application.run_polling()


if __name__ == "__main__":
    main()