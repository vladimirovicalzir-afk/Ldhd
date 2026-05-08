#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║         Devin Session Creator (без GitHub)               ║
║   Создание сессий Devin без подключения Git-провайдера   ║
╚══════════════════════════════════════════════════════════╝

Как получить токен (одноразово):
  1. Откройте https://app.devin.ai в браузере
  2. Войдите в свой аккаунт
  3. Нажмите F12 (откроются DevTools)
  4. Перейдите во вкладку Console
  5. Вставьте эту команду и нажмите Enter:

     JSON.parse(localStorage.getItem('auth1_session')).token

  6. Скопируйте результат — это ваш токен (начинается с auth1_)

Как получить org_id (одноразово):
  1. В той же консоли (F12) вставьте:

     JSON.parse(localStorage.getItem('auth1_session')).userId

  2. Затем посмотрите URL — в адресной строке будет:
     app.devin.ai/org/ВАШ_ОРГ — это имя вашей организации

  3. Или вставьте в консоль:

     Object.keys(localStorage).filter(k => k.includes('org-'))

     Найдите строку вида org-xxxxx — это ваш org_id

Использование:
  python3 devin_session_creator.py
"""

import json
import os
import sys

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "devin_config.json")


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def setup_config():
    config = load_config()

    print("\n╔══════════════════════════════════════╗")
    print("║       Настройка Devin Creator        ║")
    print("╚══════════════════════════════════════╝\n")

    if config.get("token"):
        print(f"  Текущий токен: {config['token'][:20]}...")
        change = input("  Изменить токен? (y/n): ").strip().lower()
        if change != "y":
            token = config["token"]
        else:
            token = input("  Вставьте новый токен (auth1_...): ").strip()
    else:
        print("  Как получить токен:")
        print("  1. Откройте https://app.devin.ai")
        print("  2. Нажмите F12 → Console")
        print("  3. Вставьте: JSON.parse(localStorage.getItem('auth1_session')).token")
        print("  4. Скопируйте результат\n")
        token = input("  Вставьте токен (auth1_...): ").strip()

    if not token.startswith("auth1_"):
        print("\n  ⚠ Токен должен начинаться с auth1_")
        print("  Проверьте инструкцию выше")
        return None

    if config.get("org_id"):
        print(f"\n  Текущий org_id: {config['org_id']}")
        change = input("  Изменить org_id? (y/n): ").strip().lower()
        if change != "y":
            org_id = config["org_id"]
        else:
            org_id = input("  Вставьте org_id (org-...): ").strip()
    else:
        print("\n  Как получить org_id:")
        print("  В консоли (F12) вставьте:")
        print("  Object.keys(localStorage).filter(k => k.includes('org-'))")
        print("  Найдите строку вида org-xxxxx\n")
        org_id = input("  Вставьте org_id (org-...): ").strip()

    if not org_id.startswith("org-"):
        print("\n  ⚠ org_id должен начинаться с org-")
        return None

    config["token"] = token
    config["org_id"] = org_id
    save_config(config)
    print("\n  ✓ Настройки сохранены!\n")
    return config


def create_session(config, message):
    try:
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError, URLError
    except ImportError:
        print("  Ошибка: не удалось импортировать urllib")
        return None

    url = "https://app.devin.ai/api/sessions"
    headers = {
        "Authorization": f"Bearer {config['token']}",
        "x-cog-org-id": config["org_id"],
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = json.dumps({"user_message": message}).encode("utf-8")

    req = Request(url, data=data, headers=headers, method="POST")

    try:
        with urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result
    except HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"\n  ✗ Ошибка {e.code}: {body}")
        if e.code == 401:
            print("  → Токен истёк. Получите новый (F12 → Console).")
            print("  → Запустите: python3 devin_session_creator.py --setup")
        return None
    except URLError as e:
        print(f"\n  ✗ Ошибка соединения: {e.reason}")
        return None


def list_sessions(config):
    try:
        from urllib.request import Request, urlopen
        from urllib.error import HTTPError
    except ImportError:
        return None

    url = (
        f"https://app.devin.ai/api/{config['org_id']}/v2sessions"
        f"?limit=10&order_by=created_at&sort_direction=desc&compact=true"
    )
    headers = {
        "Authorization": f"Bearer {config['token']}",
        "x-cog-org-id": config["org_id"],
        "Accept": "application/json",
    }

    req = Request(url, headers=headers)

    try:
        with urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("result", [])
    except HTTPError:
        return None


def main():
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║        🤖 Devin Session Creator (без GitHub)        ║")
    print("╚══════════════════════════════════════════════════════╝")

    if "--setup" in sys.argv:
        setup_config()
        return

    config = load_config()

    if not config.get("token") or not config.get("org_id"):
        print("\n  Первый запуск — нужна настройка.\n")
        config = setup_config()
        if not config:
            return

    while True:
        print("\n  ┌─────────────────────────────────────┐")
        print("  │  1. Создать новую сессию             │")
        print("  │  2. Мои последние сессии              │")
        print("  │  3. Настройки (сменить токен)        │")
        print("  │  0. Выход                            │")
        print("  └─────────────────────────────────────┘")

        choice = input("\n  Выберите действие: ").strip()

        if choice == "1":
            print("\n  Введите задачу для Devin:")
            print("  (что вы хотите чтобы Devin сделал)\n")
            message = input("  → ").strip()

            if not message:
                print("  ⚠ Сообщение не может быть пустым")
                continue

            print("\n  ⏳ Создаю сессию...")
            result = create_session(config, message)

            if result and result.get("devin_id"):
                session_id = result["devin_id"].replace("devin-", "")
                url = f"https://app.devin.ai/sessions/{session_id}"
                print(f"\n  ✓ Сессия создана!")
                print(f"  🔗 {url}")
                print(f"\n  Откройте ссылку в браузере для работы с Devin.")
            else:
                print("  ✗ Не удалось создать сессию")

        elif choice == "2":
            print("\n  ⏳ Загружаю сессии...")
            sessions = list_sessions(config)

            if sessions:
                print(f"\n  Последние {len(sessions)} сессий:\n")
                for i, s in enumerate(sessions, 1):
                    sid = s.get("devin_id", "").replace("devin-", "")
                    title = s.get("title", "Без названия")
                    status = s.get("status", "?")
                    url = f"https://app.devin.ai/sessions/{sid}"
                    status_icon = {"running": "🟢", "blocked": "🟡", "suspended": "⚪"}.get(status, "⚫")
                    print(f"  {i}. {status_icon} {title}")
                    print(f"     Статус: {status}")
                    print(f"     🔗 {url}\n")
            else:
                print("  Не удалось загрузить сессии (возможно, токен истёк)")

        elif choice == "3":
            setup_config()

        elif choice == "0":
            print("\n  👋 До встречи!\n")
            break

        else:
            print("  ⚠ Неизвестное действие")


if __name__ == "__main__":
    main()
