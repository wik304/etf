import streamlit as st
import yfinance as yf
import pandas as pd

# Tytuł aplikacji
st.title("📊 Analiza ETF XTB")

tickers = {
    "Rynki Wschodzące (EIMI)": "EIMI.L",
    "Cały Świat (ISAC)": "ISAC.L",
    "Polska Małe (sWIG80)": "ETFBS80TR.WA"
}

def oblicz_rsi(series, period=14):
    delta = series.diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Przycisk do odświeżania
if st.button('Pobierz i Analizuj Dane'):
    wyniki = []
    st.text("Pobieranie danych z Yahoo Finance...")
    
    for nazwa, symbol in tickers.items():
        try:
            data = yf.download(symbol, period="1y", progress=False)
            if data.empty: continue

            # Obsługa danych
            if isinstance(data.columns, pd.MultiIndex):
                current_price = data['Close'].iloc[-1].item()
                history_close = data['Close'].squeeze()
            else:
                current_price = data['Close'].iloc[-1]
                history_close = data['Close']

            rsi = oblicz_rsi(history_close).iloc[-1]
            max_price = history_close.max()
            drawdown = ((current_price - max_price) / max_price) * 100

            # Logika sygnału
            if rsi < 40:
                sygnal = "KUP 🟢"
            elif rsi > 70:
                sygnal = "CZEKAJ 🔴"
            else:
                sygnal = "TRZYMAJ 🟠"

            wyniki.append({
                "ETF": nazwa,
                "Cena": round(current_price, 2),
                "RSI": round(rsi, 1),
                "Spadek": f"{round(drawdown, 1)}%",
                "Decyzja": sygnal
            })
            
        except Exception as e:
            st.error(f"Błąd: {e}")

    # Wyświetlanie tabeli
    if wyniki:
        df = pd.DataFrame(wyniki)
        
        # Kolorowanie tabeli (opcjonalne, proste wyświetlenie)
        st.dataframe(df, hide_index=True)
        
        # Podświetlenie najlepszej opcji
        najlepszy = df.sort_values(by="RSI").iloc[0]
        st.success(f"💡 Najlepsza opcja dzisiaj: **{najlepszy['ETF']}** (RSI: {najlepszy['RSI']})")
