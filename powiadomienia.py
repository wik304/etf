import os
import requests
import yfinance as yf
import pandas as pd

# Pobieramy sekrety ze środowiska (GitHub jest tu podstawi)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

tickers = {
    "Rynki Wschodzące (EIMI)": "EIMI.L",
    "Cały Świat (ISAC)": "ISAC.L",
    "Polska Małe (sWIG80)": "ETFBS80TR.WA"
}

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def check_market():
    alerts = []
    
    for nazwa, symbol in tickers.items():
        try:
            data = yf.download(symbol, period="3mo", progress=False) # Krótszy okres wystarczy
            if data.empty: continue
            
            # Obsługa formatu
            close = data['Close'].squeeze() if isinstance(data.columns, pd.MultiIndex) else data['Close']
            
            # Oblicz RSI
            delta = close.diff(1)
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = rsi.iloc[-1]
            current_price = close.iloc[-1]

            # --- WARUNEK POWIADOMIENIA ---
            # Wyślij wiadomość tylko jeśli jest TANIO (RSI < 40)
            if current_rsi < 40:
                alerts.append(f"🟢 *OKAZJA NA: {nazwa}*\nCena: {current_price:.2f}\nRSI: {current_rsi:.1f} (Dołek!)")
                
        except Exception as e:
            print(f"Błąd: {e}")

    if alerts:
        # Złączamy wszystkie alerty w jedną wiadomość
        full_message = "📢 *RAPORT ETF*\n\n" + "\n\n".join(alerts)
        send_telegram_message(full_message)
    else:
        # Opcjonalnie: odkomentuj linię niżej, jeśli chcesz dostawać raport codziennie nawet jak nie ma okazji
        # send_telegram_message("Spokój na rynku. Żaden ETF nie jest na dołku (RSI > 40).")
        pass

if __name__ == "__main__":
    if TOKEN and CHAT_ID:
        check_market()
    else:
        print("Brak tokenów konfiguracyjnych.")
