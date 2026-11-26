UA ------------------------------------------------------------

# 🦜 Parrot Voice Client

Легкий клієнт для миттєвого запису голосових повідомлень у Discord (із розшифровкою в текст) та фонового прослуховування чату.

## Безпека та прозорість
Весь вихідний код клієнта відкритий у файлі `parrot_client.py`. Клієнт **не запитує** пароль чи токен від вашого акаунта Discord — він лише зчитує назву відкритого каналу із заголовка вікна та передає запис із мікрофона на сервер бота.

---

## Встановлення та запуск (Windows)

Ви можете обрати будь-який із двох способів:

### Варіант 1: Готовий `.exe` файл (без встановлення Python)
1. Перейдіть у розділ **Releases** (праворуч на сторінці репозиторію) та завантажте **`ParrotClient.exe`**.
2. Запустіть файл — іконка **Parrot** з'явиться в системному треї (біля годинника).
   > *Примітка:* `ParrotClient.exe` автоматично зібрано серверами GitHub із відкритого коду цього репозиторію. При першому запуску Windows SmartScreen може показати попередження через відсутність платного сертифіката — натисніть **Додатково (More info)** → **Все одно виконати (Run anyway)**.

### Варіант 2: Запуск із відкритого коду (через Python)
1. Переконайтеся, що на ПК встановлено **Python 3.10 – 3.12** (під час встановлення обов'язково поставте галочку **Add Python to PATH**).
2. Натисніть зелену кнопку **Code → Download ZIP** у верхній частині сторінки та розпакуйте архів.
3. Запустіть **`Start_Parrot.bat`** — скрипт сам створить ізольоване середовище, встановить необхідні бібліотеки й запустить клієнт у системному треї.

---

## Перше налаштування

1. Натисніть правою кнопкою миші по іконці **Parrot** у системному треї → **Settings**.
2. **Parrot Server URL:** вставте посилання, яке надав адміністратор сервера (наприклад, `https://....trycloudflare.com`).
3. **Your Discord Username:** впишіть свій логін Discord (без `@`).
4. Натисніть **Save & Apply**.

---

## Керування та можливості

* **Запис голосового (`f9` за замовчуванням):** натисніть гарячу клавішу, щоб почати запис у відкритий текстовий канал Discord, і натисніть її ще раз для відправки.
* **Скасування запису (`Esc` за замовчуванням):** натисніть під час запису, щоб скинути його без відправки.
* **Відповідь учаснику голосом (`Reply to ...`):** почніть голосове повідомлення англійською фразою **`Reply to [Нікнейм]`** (наприклад, *«Reply to Alex, я вже завантажив файл»*) або **`Reply to last`**, щоб відповісти на останнє повідомлення в чаті — бот автоматично прикріпить цитату-відповідь.
* **Редагування та видалення повідомлень:** натисніть **правою кнопкою миші** по своєму повідомленню в чаті → **Застосунки (Apps)** → **`Edit`** (щоб змінити текст і перегенерувати озвучку) або **`Delete`** (щоб видалити повідомлення).
* **Auto-Play Chat** (галочка в меню трею): автоматично озвучує в навушниках нові повідомлення у відкритому каналі Discord.


RU ------------------------------------------------------------

# 🦜 Parrot Voice Client

Лёгкий клиент для мгновенной записи голосовых сообщений в Discord (с расшифровкой в текст) и фонового прослушивания чата.

## Безопасность и прозрачность
Весь исходный код клиента открыт в файле `parrot_client.py`. Клиент **не запрашивает** пароль или токен от вашего аккаунта Discord — он только считывает название открытого канала из заголовка окна и передаёт запись с микрофона на сервер бота.

---

## Установка и запуск (Windows)

Вы можете выбрать любой из двух способов:

### Вариант 1: Готовый `.exe` файл (без установки Python)
1. Перейдите в раздел **Releases** (справа на странице репозитория) и скачайте **`ParrotClient.exe`**.
2. Запустите файл — иконка **Parrot** появится в системном трее (возле часов).
   > *Примечание:* `ParrotClient.exe` автоматически собран серверами GitHub из открытого кода этого репозитория. При первом запуске Windows SmartScreen может показать предупреждение из-за отсутствия платного сертификата — нажмите **Подробнее (More info)** → **Выполнить в любом случае (Run anyway)**.

### Вариант 2: Запуск из открытого кода (через Python)
1. Убедитесь, что на ПК установлен **Python 3.10 – 3.12** (при установке обязательно поставьте галочку **Add Python to PATH**).
2. Нажмите зелёную кнопку **Code → Download ZIP** в верхней части страницы и распакуйте архив.
3. Запустите **`Start_Parrot.bat`** — скрипт сам создаст изолированное окружение, установит нужные библиотеки и запустит клиент в системном трее.

---

## Первая настройка

1. Нажмите правой кнопкой мыши по иконке **Parrot** в системном трее → **Settings**.
2. **Parrot Server URL:** вставьте ссылку, которую выдал администратор сервера (например, `https://....trycloudflare.com`).
3. **Your Discord Username:** впишите свой логин Discord (без `@`).
4. Нажмите **Save & Apply**.

---

## Управление и возможности

* **Запись голосового (`f9` по умолчанию):** нажмите горячую клавишу, чтобы начать запись в открытый текстовый канал Discord, и нажмите её ещё раз для отправки.
* **Отмена записи (`Esc` по умолчанию):** нажмите во время записи, чтобы сбросить её без отправки.
* **Ответ участнику голосом (`Reply to ...`):** начните голосовое сообщение английской фразой **`Reply to [Никнейм]`** (например, *«Reply to Alex, я уже загрузил файл»*) или **`Reply to last`**, чтобы ответить на последнее сообщение в чате — бот автоматически прикрепит цитату-ответ.
* **Редактирование и удаление сообщений:** нажмите **правой кнопкой мыши** по своему сообщению в чате → **Приложения (Apps)** → **`Edit`** (чтобы изменить текст и перегенерировать озвучку) или **`Delete`** (чтобы удалить сообщение).
* **Auto-Play Chat** (галочка в меню трея): автоматически озвучивает в наушниках новые сообщения в открытом канале Discord.


EN ------------------------------------------------------------

# 🦜 Parrot Voice Client

A lightweight desktop client for instant voice-to-text messaging in Discord and hands-free background chat playback.

## Security & Transparency
The full source code is open and available in `parrot_client.py`. The client **never asks** for your Discord password or account token — it simply reads the active channel name from the Discord window title and streams your microphone recording to the bot server.

---

## Installation & Launch (Windows)

Choose either of the two options below:

### Option 1: Standalone `.exe` File (No Python required)
1. Go to the **Releases** section (on the right side of the repository page) and download **`ParrotClient.exe`**.
2. Run the file — the **Parrot** icon will appear in your system tray (near the clock).
   > *Note:* `ParrotClient.exe` is automatically built by GitHub Actions directly from the open-source code in this repository. On first launch, Windows SmartScreen may display a warning because the executable is unsigned — click **More info** → **Run anyway**.

### Option 2: Run from Source Code (via Python)
1. Make sure **Python 3.10 – 3.12** is installed on your PC (check **Add Python to PATH** during installation).
2. Click the green **Code → Download ZIP** button at the top of this page and extract the archive.
3. Run **`Start_Parrot.bat`** — it will automatically set up a virtual environment, install dependencies, and launch the client in the system tray.

---

## Initial Setup

1. Right-click the **Parrot** icon in the system tray → **Settings**.
2. **Parrot Server URL:** paste the server URL provided by the server admin (e.g., `https://....trycloudflare.com`).
3. **Your Discord Username:** enter your Discord username (without `@`).
4. Click **Save & Apply**.

---

## Controls & Features

* **Record Voice (`f9` by default):** press the hotkey to start recording into the currently open Discord text channel, and press it again to send.
* **Cancel Recording (`Esc` by default):** press while recording to discard the audio without sending.
* **Voice Reply (`Reply to ...`):** start your voice message with **`Reply to [Nickname]`** (e.g., *"Reply to Alex, I just pushed the update"*) or **`Reply to last`** to reply to the latest message in chat — the bot will automatically attach a reply quote.
* **Edit & Delete Messages:** **right-click** your message in Discord → **Apps** → **`Edit`** (to update the text and regenerate TTS audio) or **`Delete`** (to remove the message).
* **Auto-Play Chat** (tray menu toggle): automatically reads incoming messages from the open Discord channel aloud in your headphones.


