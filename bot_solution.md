## Решение проблемы дублирования в Telegram боте

### Анализ проблемы
Вы сообщили, что:
1. `xo-os import` работает корректно без дублирования событий в Google Calendar
2. Telegram бот при отправке .ics файлов вызывает дублирование событий
3. Вы хотите упростить обработку, просто вызвав core импорт-функцию без лишних оберток

### Причина проблемы
Различие в поведении между `xo-os import` и ботом указывает на то, что проблема lies in how the import functionality is being invoked or initialized in the bot's context, not in the core import logic itself.

### Предлагаемое решение
Вместо того чтобы бот непосредственно вызывал сервисные функции (как сейчас делает через `SyncService.import_ics`), будем делегировать всю работу импорта проверенному `xo-os import` CLIcommand. Это гарантируетidentical execution context и поведение как у рабочего `xo-os import`.

### Изменения в `app/telegram_bot.py`

Замените функцию `process_ics_content` на версию, которая использует subprocess для вызова `xo-os import`:

```python
import subprocess
import asyncio

async def process_ics_content(ics_content: bytes, source: str, file_path: str | None = None) -> str:
    """
    Process ICS content by delegating to the working xo-os import CLI.
    Optionally delete the file after success.
    Returns a human-readable result string.
    """
    try:
        # Save file temporarily if we have a file_path
        temp_file_path = None
        if file_path is None and ics_content is not None:
            # Generate a temporary file name
            import tempfile
            import os
            temp_fd, temp_file_path = tempfile.mkstemp(suffix='.ics', dir=RECEIVED_ICS_DIR)
            try:
                with os.fdopen(temp_fd, 'wb') as f:
                    f.write(ics_content)
                file_path = temp_file_path
            except Exception:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                raise

        # Run xo-os import command
        # Assuming xo-os is in PATH or we can call it as module
        cmd = ["xo-os", "import", file_path]
        process = await asyncio.create_subprocess_exec(
            *cmd,
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

        # Delete the file if we saved it
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Deleted temporary ICS file: {file_path}")

        return result_msg or "Import completed successfully"

    except Exception as e:
        logger.exception(f"Error during ICS processing ({source})")
        # Clean up temp file if needed
        if 'temp_file_path' in locals() and temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except:
                pass
        raise e
```

### Преимущества этого подхода:
1. **Идентичное поведение**: Использует тот же код path что и рабочий `xo-os import`
2. **Простота**: Убирает сложную логику из бота, делегируя её проверенному компоненту
3. **Надежность**: Наследует все исправления и improvements сделанные в `xo-os import`
4. **Легкая отладка**: Проблемы с импортом можно отлаживать напрямую через `xo-os import`

### Что нужно убедиться:
1. Команда `xo-os` доступна в PATH среды где运行 бот
2. Логи импорта будут видимы в логах бота (через stdout/stderr перенаправление)
3. Обработка ошибок сохраняет информативность для пользователя

### Альтернативный подход (если subprocess нежелателен):
Если вы предпочитаете избежать subprocess overhead, можно импортировать и вызвать те же функции что использует `xo-os import` напрямую. Однако, учитывая что вы уже пробовали прямое вызов сервисных функций и сталкивались с проблемами,Delegating to CLI является более надежным решением.

### Следующие шаги:
1. Замените функцию `process_ics_content` в `app/telegram_bot.py` на предложенную выше версию
2. Убедитесь, что `xo-os` команда доступна в среде выполнения бота
3. Перезапустите бота и отправьте тестовый .ics файл
4. Проверьте, что дублирование исчезло и события создаются корректно