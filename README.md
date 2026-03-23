# Telegram Message Sender

Production-ready Python-скрипт для периодической отправки сообщений в Telegram через Telethon.

## Описание

Скрипт автоматически отправляет сообщение "Hello world" контакту с именем "Հայկո" каждый час после активации.

### Возможности:
- ✅ Асинхронное программирование (async/await)
- ✅ Автоматическое переподключение при потере связи
- ✅ Цветное логирование в консоль
- ✅ Обработка всех типов ошибок Telegram API
- ✅ Поддержка двухфакторной аутентификации
- ✅ Гибкая настройка через переменные окружения

---

##  Требования

### Системные требования:
- **Python 3.8+** (рекомендуется Python 3.10 или 3.11)
- **pip** (менеджер пакетов Python)
- Интернет-соединение

### Получение API credentials:

1. Перейдите на **https://my.telegram.org/apps**
2. Войдите с вашим номером телефона
3. Создайте новое приложение (Create new application)
4. Скопируйте **api_id** и **api_hash**

---

##  Установка

### Шаг 1: Клонирование/скачивание

```zsh
# Создайте директорию проекта
mkdir -p ~/telegram_sender
cd ~/telegram_sender

# Скопируйте файлы скрипта в эту директорию
```

### Шаг 2: Создание виртуального окружения (рекомендуется)

```zsh
# Создаём виртуальное окружение
python3 -m venv venv

# Активируем в zsh
source venv/bin/activate
```

### Шаг 3: Установка зависимостей

```zsh
# Установка из requirements.txt
pip install -r requirements.txt

# Или вручную
pip install telethon
```

### Шаг 4: Настройка переменных окружения

**Способ 1: Через .env файл (рекомендуется)**

```zsh
# Копируем пример
cp .env.example .env

# Редактируем файл
nano .env
# или
vim .env
```

Заполните файл:
```
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_PHONE=+37499123456
```

**Способ 2: Через экспорт в zsh**

```zsh
# Добавьте в ~/.zshrc
export TELEGRAM_API_ID="12345678"
export TELEGRAM_API_HASH="abcdef1234567890abcdef1234567890"
export TELEGRAM_PHONE="+37499123456"

# Примените изменения
source ~/.zshrc
```

**Способ 3: Прямое редактирование скрипта**

Откройте `telegram_sender.py` и замените значения:
```python
API_ID = 'YOUR_API_ID_HERE'      # замените на ваш API ID
API_HASH = 'YOUR_API_HASH_HERE'  # замените на ваш API Hash
PHONE_NUMBER = '+374XXXXXXXX'    # замените на ваш номер
```

---

##  Запуск

### Первый запуск (авторизация)

```zsh
# Активируем виртуальное окружение (если используете)
source venv/bin/activate

# Запускаем скрипт
python3 telegram_sender.py
```

При первом запуске скрипт запросит:
1. **Код подтверждения** — придёт в Telegram
2. **Пароль 2FA** — если включена двухфакторная аутентификация

После успешной авторизации создастся файл сессии `telegram_sender_session.session`.

### Последующие запуски

```zsh
python3 telegram_sender.py
```

Авторизация больше не потребуется (используется сохранённая сессия).

### Остановка скрипта

Нажмите `Ctrl+C` для корректной остановки.

---

##  Постоянный запуск (фоновый режим)

### Способ 1: systemd (рекомендуется для Linux)

```zsh
# 1. Копируем service файл
sudo cp telegram-sender.service /etc/systemd/system/

# 2. Редактируем под вашу систему
sudo nano /etc/systemd/system/telegram-sender.service
# Замените:
# - YOUR_USERNAME на ваше имя пользователя
# - YOUR_GROUP на вашу группу (обычно = username)
# - Пути к файлам
# - Переменные окружения (API_ID, API_HASH, PHONE)

# 3. Перезагружаем systemd
sudo systemctl daemon-reload

# 4. Включаем автозапуск при загрузке системы
sudo systemctl enable telegram-sender.service

# 5. Запускаем сервис
sudo systemctl start telegram-sender.service

# 6. Проверяем статус
sudo systemctl status telegram-sender.service
```

**Управление сервисом:**
```zsh
# Просмотр статуса
sudo systemctl status telegram-sender

# Остановка
sudo systemctl stop telegram-sender

# Перезапуск
sudo systemctl restart telegram-sender

# Просмотр логов
sudo journalctl -u telegram-sender.service -f

# Просмотр последних 100 строк логов
sudo journalctl -u telegram-sender.service -n 100
```

### Способ 2: cron (альтернатива)

>  **Внимание:** cron не подходит для постоянной работы скрипта, 
> так как скрипт уже содержит встроенный таймер.

Если нужно запускать скрипт каждый час как отдельный процесс:

```zsh
# Открываем редактор crontab
crontab -e

# Добавляем строку (запуск каждый час)
0 * * * * cd /home/YOUR_USERNAME/telegram_sender && /usr/bin/python3 telegram_sender.py >> /tmp/telegram_sender.log 2>&1
```

### Способ 3: tmux / screen (для сессий)

```zsh
# Создаём новую сессию tmux
tmux new -s telegram

# Запускаем скрипт
python3 telegram_sender.py

# Отключаемся от сессии: Ctrl+B, затем D

# Подключиться обратно:
tmux attach -t telegram
```

### Способ 4: nohup (простой способ)

```zsh
# Запуск в фоне
nohup python3 telegram_sender.py > telegram_sender.log 2>&1 &

# Просмотр логов
tail -f telegram_sender.log

# Поиск процесса
ps aux | grep telegram_sender

# Остановка (замените PID)
kill PID
```

---

##  Конфигурация

### Переменные скрипта (telegram_sender.py)

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `TARGET_CONTACT_NAME` | `Հայկո` | Имя контакта-получателя |
| `MESSAGE_TEXT` | `Hello world` | Текст сообщения |
| `SEND_INTERVAL_SECONDS` | `3600` | Интервал отправки (секунды) |
| `MAX_RECONNECT_ATTEMPTS` | `5` | Максимум попыток переподключения |
| `RECONNECT_DELAY_SECONDS` | `30` | Задержка между попытками |

### Изменение интервала отправки

```python
# В файле telegram_sender.py
SEND_INTERVAL_SECONDS = 1800  # 30 минут
SEND_INTERVAL_SECONDS = 7200  # 2 часа
SEND_INTERVAL_SECONDS = 86400 # 24 часа
```

---

##  Логирование

Пример вывода:
```
2024-01-15 10:00:00 | INFO | TelegramMessageSender инициализирован
2024-01-15 10:00:00 | INFO | Целевой контакт: Հայկո
2024-01-15 10:00:00 | INFO | Интервал отправки: 3600 секунд (60 минут)
2024-01-15 10:00:00 | INFO | Подключение к Telegram API...
2024-01-15 10:00:02 | INFO | Уже авторизован. Подключение установлено.
2024-01-15 10:00:02 | INFO | Поиск контакта: Հայկո
2024-01-15 10:00:03 | INFO | Контакт найден: Հայկո (ID: 123456789)
2024-01-15 10:00:03 | INFO | Отправка сообщения: 'Hello world'
2024-01-15 10:00:04 | INFO | Сообщение успешно отправлено: Հայկո
2024-01-15 10:00:04 | INFO | Следующая отправка в 11:00:04
```

---

##  Устранение неполадок

### Ошибка: "API_ID не настроен!"
Проверьте установку переменных окружения:
```zsh
echo $TELEGRAM_API_ID
echo $TELEGRAM_API_HASH
```

### Ошибка: "Контакт не найден"
1. Проверьте точное написание имени контакта
2. Убедитесь, что контакт есть в списке диалогов или контактов
3. Проверьте кодировку (скрипт поддерживает Unicode/армянские буквы)

### Ошибка: "FloodWait"
Telegram ограничивает частоту отправки сообщений. Скрипт автоматически подождёт указанное время.

### Ошибка: "Session password needed"
Включена двухфакторная аутентификация. Введите пароль при запросе.

### Проблемы с соединением
1. Проверьте интернет-соединение
2. Проверьте доступность Telegram API
3. Скрипт автоматически переподключится

---

##  Структура файлов

```
telegram_sender/
├── telegram_sender.py       # Основной скрипт
├── requirements.txt         # Зависимости Python
├── .env.example            # Пример конфигурации
├── telegram-sender.service # systemd service файл
├── README.md               # Этот файл
└── venv/                   # Виртуальное окружение (создаётся)
```

---

##  Безопасность

1. **Никогда не делитесь** API ID и API Hash
2. **Не коммитьте** файл `.env` в Git
3. **Добавьте** в `.gitignore`:
   ```
   .env
   *.session
   *.session-journal
   __pycache__/
   venv/
   ```
4. Файл сессии `*.session` содержит ключи авторизации — храните безопасно

---

##  Лицензия

MIT License

---

##  Поддержка

При возникновении проблем:
1. Проверьте логи
2. Убедитесь в правильности credentials
3. Проверьте подключение к Интернету
4. Обратитесь к документации Telethon: https://docs.telethon.dev/
