import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- KONFIGURACJA ---
# Pobieramy tokeny i czyścimy je ze spacji (.strip()) dla pewności
token_raw = os.environ.get("TELEGRAM_TOKEN")
chat_id_raw = os.environ.get("TELEGRAM_CHAT_ID")

TOKEN = token_raw.strip() if token_raw else None
CHAT_ID = chat_id_raw.strip() if chat_id_raw else None

# Zaktualizowana lista tickerów
tickers = {
    "Rynki Wschodzące (EIMI)": "EIMI.L",
    "Cały Świat (ISAC)": "ISAC.L",
    "Polska Małe (sWIG80)": "ETFBS80TR.WA",
    "Polska Średnie (mWIG40)": "ETFBM40TR.WA",
    "Polska Duże (WIG20)": "ETFBW20TR.WA"
}

def send_telegram_message(message):
    """Wysyła wiadomość na Telegram."""
    if not TOKEN or not CHAT_ID:
        print("BŁĄD: Brak tokenów konfiguracji telegrama.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"Błąd wysyłania: {response.text}")
        else:
            print("Wiadomość wysłana pomyślnie.")
    except Exception as e:
        print(f"Błąd połączenia z Telegramem: {e}")

def check_market():
    print(f"--- ANALIZA RYNKU: {datetime.now().strftime('%Y-%m-%d')} ---")
    alerts = []
    
    for nazwa, symbol in tickers.items():
        try:
            print(f"Sprawdzam: {nazwa}...")
            # Pobieramy dane (3 miesiące wystarczą do RSI)
            data = yf.download(symbol, period="3mo", progress=False)
            
            if data.empty:
                print(f"-> Brak danych dla {symbol}")
                continue
            
            # Obsługa formatu danych yfinance (razem z MultiIndex)
            if isinstance(data.columns, pd.MultiIndex):
                close = data['Close'].squeeze()
            else:
                close = data['Close']
            
            # Upewnienie się, że close to Series, a nie DataFrame (zabezpieczenie)
            if isinstance(close, pd.DataFrame):
                close = close[symbol]
            
            # Obliczenie RSI
            delta = close.diff(1)
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            # Pobranie konkretnych wartości liczbowych
            current_rsi = rsi.iloc[-1].item() if hasattr(rsi.iloc[-1], 'item') else rsi.iloc[-1]
            current_price = close.iloc[-1].item() if hasattr(close.iloc[-1], 'item') else close.iloc[-1]
            
            print(f"-> Cena: {current_price:.2f}, RSI: {current_rsi:.2f}")

            # --- WARUNEK ALARMU ---
            # Wysyłamy, jeśli RSI < 40 (taniej niż zwykle)
            if current_rsi < 40:
                # Wybieramy walutę do wyświetlenia
                waluta = "PLN" if "WA" in symbol else "USD/GBP"
                
                tresc_alarmu = (
                    f"🟢 *OKAZJA: {nazwa}*\n"
                    f"Cena: `{current_price:.2f} {waluta}`\n"
                    f"RSI: `{current_rsi:.1f}` (Lokalny dołek!)"
                )
                alerts.append(tresc_alarmu)
                
        except Exception as e:
            print(f"Błąd przy analizie {nazwa}: {e}")

    # Raportowanie
    if alerts:
        print("ZNALEZIONO OKAZJE! Wysyłam powiadomienie...")
        full_message = "📢 *RAPORT ETF - SYGNAŁ KUPNA*\n\n" + "\n\n".join(alerts)
        send_telegram_message(full_message)
    else:
        print("Brak okazji inwestycyjnych (wszystkie RSI > 40). Telegram milczy.")

if __name__ == "__main__":
    check_market()
