#!/usr/bin/env python3
"""
Telegram Message Sender - Production Ready Script
===================================================

Этот скрипт отправляет сообщение "Hello world" контакту с именем "Հայկ Բաղդասարյան"
каждый час после активации.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Optional

from telethon import TelegramClient, errors
from telethon.tl.types import User

# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================

# API credentials - ВАЖНО: Замените на свои данные!
# Получите их на https://my.telegram.org/apps
API_ID = int(os.environ.get("TELEGRAM_API_ID", "YOUR"))
API_HASH = os.environ.get("TELEGRAM_API_HASH", "YOUR")

# Номер телефона (для первого запуска)
PHONE_NUMBER = os.environ.get("TELEGRAM_PHONE", "+YOUR")

# Имя контакта-получателя
TARGET_CONTACT_NAME = "Հայկ Բաղդասարյան"

# Сообщение для отправки
MESSAGE_TEXT = "Hello world․ Տեսար ոնց ստացվեց"

# Интервал отправки (в секундах) - 1 час = 3600 секунд
SEND_INTERVAL_SECONDS = 11

# Имя сессии (файл сессии будет сохранён с этим именем)
SESSION_NAME = "telegram_sender_session"

# Настройки переподключения
MAX_RECONNECT_ATTEMPTS = 5
RECONNECT_DELAY_SECONDS = 30

# ============================================================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================================================


def setup_logging() -> logging.Logger:
    """
    Настраивает логирование с цветным выводом в консоль.

    Returns:
        logging.Logger: Настроенный логгер
    """

    # Создаём кастомный форматтер с цветами
    class ColoredFormatter(logging.Formatter):
        """Форматтер с цветным выводом для разных уровней логов."""

        # ANSI коды цветов
        COLORS = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[32m",  # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[35m",  # Magenta
        }
        RESET = "\033[0m"

        def format(self, record: logging.LogRecord) -> str:
            """Форматирует запись лога с цветом."""
            color = self.COLORS.get(record.levelname, self.RESET)
            record.levelname = f"{color}{record.levelname}{self.RESET}"
            return super().format(record)

    # Создаём логгер
    logger = logging.getLogger("TelegramSender")
    logger.setLevel(logging.DEBUG)

    # Обработчик для консоли
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Применяем форматтер
    formatter = ColoredFormatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    # Добавляем обработчик
    logger.addHandler(console_handler)

    return logger


# Инициализируем логгер
logger = setup_logging()


# ============================================================================
# КЛАСС ОТПРАВЩИКА СООБЩЕНИЙ
# ============================================================================


class TelegramMessageSender:
    """
    Класс для периодической отправки сообщений в Telegram.

    Attributes:
        api_id (str): API ID от Telegram
        api_hash (str): API Hash от Telegram
        phone (str): Номер телефона
        target_name (str): Имя целевого контакта
        message (str): Текст сообщения
        interval (int): Интервал отправки в секундах
        client (TelegramClient): Клиент Telethon
        is_running (bool): Флаг работы скрипта
    """

    def __init__(
        self,
        api_id: str,
        api_hash: str,
        phone: str,
        target_name: str,
        message: str,
        interval: int = 11,
    ):
        """
        Инициализирует отправщик сообщений.

        Args:
            api_id: API ID от my.telegram.org
            api_hash: API Hash от my.telegram.org
            phone: Номер телефона в международном формате
            target_name: Имя контакта-получателя
            message: Текст сообщения
            interval: Интервал отправки в секундах (по умолчанию 1 час)
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.target_name = target_name
        self.message = message
        self.interval = interval

        self.client: Optional[TelegramClient] = None
        self.is_running = False
        self.reconnect_attempts = 0

        logger.info("TelegramMessageSender инициализирован")
        logger.info(f"Целевой контакт: {target_name}")
        logger.info(f"Интервал отправки: {interval} секунд ({interval // 60} минут)")

    async def connect(self) -> bool:
        """
        Подключается к Telegram API.

        Returns:
            bool: True если подключение успешно, иначе False
        """
        try:
            logger.info("Подключение к Telegram API...")

            # Создаём клиент
            self.client = TelegramClient(
                SESSION_NAME,
                self.api_id,
                self.api_hash,
                system_version="4.16.30-vxCUSTOM",
            )

            # Подключаемся
            await self.client.connect()

            # Проверяем авторизацию
            if not await self.client.is_user_authorized():
                logger.warning("Требуется авторизация!")
                logger.info("Отправка кода подтверждения...")

                await self.client.send_code_request(self.phone)

                # Запрашиваем код у пользователя
                code = input("Введите код подтверждения из Telegram: ")

                try:
                    await self.client.sign_in(self.phone, code)
                    logger.info("Авторизация успешна!")
                except errors.SessionPasswordNeededError:
                    # Если включена двухфакторная аутентификация
                    password = input("Введите пароль двухфакторной аутентификации: ")
                    await self.client.sign_in(password=password)
                    logger.info("Авторизация с 2FA успешна!")
            else:
                logger.info("Уже авторизован. Подключение установлено.")

            self.reconnect_attempts = 0
            return True

        except errors.PhoneNumberInvalidError:
            logger.error("Неверный номер телефона!")
            return False

        except errors.PhoneCodeInvalidError:
            logger.error("Неверный код подтверждения!")
            return False

        except errors.PhoneCodeExpiredError:
            logger.error("Код подтверждения истёк!")
            return False

        except errors.PasswordHashInvalidError:
            logger.error("Неверный пароль двухфакторной аутентификации!")
            return False

        except ConnectionError as e:
            logger.error(f"Ошибка соединения: {e}")
            return False

        except Exception as e:
            logger.error(f"Неожиданная ошибка при подключении: {type(e).__name__}: {e}")
            return False

    async def disconnect(self) -> None:
        """Корректно отключается от Telegram API."""
        if self.client and self.client.is_connected():
            logger.info("Отключение от Telegram API...")
            await self.client.disconnect()
            logger.info("Отключение завершено")

    async def find_contact(self) -> Optional[User]:
        """
        Ищет контакт по имени.

        Returns:
            Optional[User]: Найденный контакт или None
        """
        try:
            logger.info(f"Поиск контакта: {self.target_name}")

            # Получаем список диалогов
            dialogs = await self.client.get_dialogs()

            for dialog in dialogs:
                entity = dialog.entity

                # Проверяем, что это пользователь (не группа/канал)
                if isinstance(entity, User):
                    # Проверяем имя (first_name, last_name или username)
                    full_name = (
                        f"{entity.first_name or ''} {entity.last_name or ''}".strip()
                    )

                    if (
                        self.target_name.lower() in full_name.lower()
                        or self.target_name.lower() == (entity.first_name or "").lower()
                        or self.target_name.lower() == (entity.username or "").lower()
                    ):
                        logger.info(f"Контакт найден: {full_name} (ID: {entity.id})")
                        return entity

            # Если не нашли в диалогах, пробуем найти в контактах
            logger.info("Поиск в списке контактов...")
            contacts = await self.client.get_contacts()

            for contact in contacts:
                if isinstance(contact, User):
                    full_name = (
                        f"{contact.first_name or ''} {contact.last_name or ''}".strip()
                    )

                    if (
                        self.target_name.lower() in full_name.lower()
                        or self.target_name.lower()
                        == (contact.first_name or "").lower()
                    ):
                        logger.info(
                            f"Контакт найден в списке: {full_name} (ID: {contact.id})"
                        )
                        return contact

            logger.warning(f"Контакт '{self.target_name}' не найден")
            return None

        except Exception as e:
            logger.error(f"Ошибка при поиске контакта: {e}")
            return None

    async def send_message_to_contact(self) -> bool:
        """
        Отправляет сообщение целевому контакту.

        Returns:
            bool: True если сообщение отправлено успешно
        """
        try:
            # Ищем контакт
            contact = await self.find_contact()

            if not contact:
                logger.error(f"Не удалось найти контакт '{self.target_name}'")
                return False

            # Отправляем сообщение
            logger.info(f"Отправка сообщения: '{self.message}'")

            await self.client.send_message(contact, self.message, parse_mode="html")

            logger.info(f"Сообщение успешно отправлено: {self.target_name}")
            return True

        except errors.FloodWaitError as e:
            logger.warning(f"FloodWait: нужно подождать {e.seconds} секунд")
            await asyncio.sleep(e.seconds)
            return await self.send_message_to_contact()

        except errors.PeerIdInvalidError:
            logger.error("Неверный ID пользователя")
            return False

        except errors.UserIsBlockedError:
            logger.error("Пользователь заблокировал вас")
            return False

        except errors.ChatWriteForbiddenError:
            logger.error("Нет прав писать этому пользователю")
            return False

        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {type(e).__name__}: {e}")
            return False

    async def reconnect(self) -> bool:
        """
        Пытается переподключиться при потере соединения.

        Returns:
            bool: True если переподключение успешно
        """
        self.reconnect_attempts += 1

        if self.reconnect_attempts > MAX_RECONNECT_ATTEMPTS:
            logger.critical(
                f"Превышено максимальное количество попыток переподключения "
                f"({MAX_RECONNECT_ATTEMPTS})"
            )
            return False

        logger.warning(
            f"Попытка переподключения {self.reconnect_attempts}/{MAX_RECONNECT_ATTEMPTS}"
        )

        # Закрываем текущее соединение
        await self.disconnect()

        # Ждём перед переподключением
        await asyncio.sleep(RECONNECT_DELAY_SECONDS)

        # Пытаемся подключиться
        return await self.connect()

    async def run_periodic_sender(self) -> None:
        """
        Запускает периодическую отправку сообщений.

        Основной цикл работы скрипта.
        """
        logger.info("Запуск периодической отправки сообщений")
        logger.info(f"Следующая отправка через {self.interval // 60} минут")

        self.is_running = True

        while self.is_running:
            try:
                # Проверяем соединение
                if not self.client or not self.client.is_connected():
                    logger.warning("Соединение потеряно")

                    if not await self.reconnect():
                        logger.error("Не удалось переподключиться. Остановка.")
                        self.is_running = False
                        break

                # Отправляем сообщение
                await self.send_message_to_contact()

                # Логируем следующую отправку
                next_send = datetime.now().timestamp() + self.interval
                next_send_time = datetime.fromtimestamp(next_send).strftime("%H:%M:%S")
                logger.info(f"Следующая отправка в {next_send_time}")

                # Ждём до следующей отправки
                await asyncio.sleep(self.interval)

            except errors.RPCError as e:
                logger.error(f"RPC ошибка: {e}")

                if not await self.reconnect():
                    self.is_running = False
                    break

            except ConnectionError as e:
                logger.error(f"Ошибка соединения: {e}")

                if not await self.reconnect():
                    self.is_running = False
                    break

            except asyncio.CancelledError:
                logger.info("Получен сигнал остановки")
                self.is_running = False
                break

            except Exception as e:
                logger.error(
                    f"Неожиданная ошибка в основном цикле: {type(e).__name__}: {e}"
                )
                await asyncio.sleep(60)  # Ждём минуту перед повторной попыткой

    async def start(self) -> None:
        """Запускает отправщик сообщений."""
        logger.info("=" * 60)
        logger.info("Telegram Message Sender - Запуск")
        logger.info("=" * 60)

        try:
            # Подключаемся
            if not await self.connect():
                logger.error("Не удалось подключиться. Выход.")
                return

            # Запускаем периодическую отправку
            await self.run_periodic_sender()

        finally:
            # Всегда отключаемся при выходе
            await self.disconnect()
            logger.info("Скрипт остановлен")

    def stop(self) -> None:
        """Останавливает отправщик сообщений."""
        logger.info("Получен сигнал остановки")
        self.is_running = False


# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================


def validate_config() -> bool:
    """
    Проверяет корректность конфигурации.

    Returns:
        bool: True если конфигурация валидна
    """
    errors = []

    if API_ID == "YOUR_API_ID_HERE":
        errors.append("API_ID не настроен!")

    if API_HASH == "YOUR_API_HASH_HERE":
        errors.append("API_HASH не настроен!")

    if PHONE_NUMBER == "+374XXXXXXXX":
        errors.append("PHONE_NUMBER не настроен!")

    if not isinstance(API_ID, int):
        errors.append(f"API_ID должен быть числом, получено: {type(API_ID).__name__}")

    if errors:
        logger.error("Ошибки конфигурации:")
        for error in errors:
            logger.error(f"  - {error}")
        logger.error("")
        logger.error(
            "Пожалуйста, настройте переменные окружения или отредактируйте скрипт:"
        )
        logger.error("  TELEGRAM_API_ID - ваш API ID")
        logger.error("  TELEGRAM_API_HASH - ваш API Hash")
        logger.error("  TELEGRAM_PHONE - ваш номер телефона")
        logger.error("")
        logger.error("Получите credentials на https://my.telegram.org/apps")
        return False

    return True


async def main() -> None:
    """Главная функция скрипта."""
    # Проверяем конфигурацию
    if not validate_config():
        sys.exit(1)

    # Создаём отправщик
    sender = TelegramMessageSender(
        api_id=API_ID,
        api_hash=API_HASH,
        phone=PHONE_NUMBER,
        target_name=TARGET_CONTACT_NAME,
        message=MESSAGE_TEXT,
        interval=SEND_INTERVAL_SECONDS,
    )

    try:
        await sender.start()
    except KeyboardInterrupt:
        logger.info("Прервано пользователем (Ctrl+C)")
        sender.stop()


if __name__ == "__main__":
    try:
        # Запускаем асинхронный main
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Завершение работы...")
