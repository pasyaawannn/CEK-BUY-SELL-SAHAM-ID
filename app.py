from flask import Flask, render_template, request
import yfinance as yf
import plotly.graph_objects as go

app = Flask(__name__)

# Auto tambah .JK kalau user input saham Indo
def fix_symbol(symbol):
    symbol = symbol.upper().strip()
    if "." not in symbol:
        symbol += ".JK"
    return symbol


@app.route("/", methods=["GET", "POST"])
def home():
    stocks = []
    chart_html = None
    selected_symbol = None

    if request.method == "POST":
        input_symbols = request.form["symbols"]

        # Checkbox BUY only
        buy_only = request.form.get("buy_only")

        # Dropdown saham pilihan chart
        selected_symbol = request.form.get("chart_symbol")

        symbol_list = input_symbols.split(",")

        # === Ambil data semua saham ===
        for sym in symbol_list:
            sym = fix_symbol(sym)

            stock = yf.Ticker(sym)
            hist = stock.history(period="7d")

            if not hist.empty:
                price = round(hist["Close"].iloc[-1], 2)

                trend = "NAIK 📈" if hist["Close"].iloc[-1] > hist["Close"].iloc[0] else "TURUN 📉"
                signal = "BUY ✅" if "NAIK" in trend else "SELL ❌"

                # Filter BUY only kalau dicentang
                if buy_only and "SELL" in signal:
                    continue

                stocks.append({
                    "symbol": sym,
                    "price": price,
                    "trend": trend,
                    "signal": signal
                })

        # === Tentukan saham untuk chart ===
        if stocks:
            if not selected_symbol:
                selected_symbol = stocks[0]["symbol"]

            hist = yf.Ticker(selected_symbol).history(period="1mo")

            fig = go.Figure(data=[go.Candlestick(
                x=hist.index,
                open=hist["Open"],
                high=hist["High"],
                low=hist["Low"],
                close=hist["Close"]
            )])

            fig.update_layout(
                title=f"Candlestick Chart {selected_symbol}",
                template="plotly_dark",
                height=500
            )

            chart_html = fig.to_html(full_html=False)

    return render_template(
        "index.html",
        stocks=stocks,
        chart=chart_html,
        selected_symbol=selected_symbol
    )


if __name__ == "__main__":
    app.run(debug=True)
