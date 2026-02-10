import os
import requests
import yfinance as yf

# 1. Wypisujemy start, żeby widzieć w logach, że skrypt ruszył
print("--- START SKRYPTU ---")

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 2. Sprawdzamy czy GitHub podstawił sekrety
if TOKEN:
    print("Token: OK (Załadowany)")
else:
    print("BŁĄD: Brak Tokena! Sprawdź plik YAML sekcję 'env'.")

if CHAT_ID:
    print(f"Chat ID: {CHAT_ID}")
else:
    print("BŁĄD: Brak Chat ID!")

# 3. Próba wysłania
if TOKEN and CHAT_ID:
    print("Próbuję wysłać wiadomość do Telegrama...")
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": "🚀 TEST: Połączenie działa! GitHub widzi Twojego Telegrama.",
    }
    try:
        r = requests.post(url, data=params)
        print(f"Odpowiedź serwera Telegrama: {r.status_code}")
        print(r.text)
    except Exception as e:
        print(f"Błąd połączenia: {e}")
else:
    print("Nie mogę wysłać wiadomości, bo brakuje danych logowania.")

print("--- KONIEC SKRYPTU ---")
