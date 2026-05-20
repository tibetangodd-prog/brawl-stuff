"""
Stock Market Game - Backend Stock Data Fetcher
Fetches real stock data and exposes as JSON API via GitHub Actions
Uses yfinance for free stock data
"""

import json
import os
import time
from datetime import datetime, timedelta
import yfinance as yf

# Major stock symbols to track (Taiwan + US markets)
STOCK_SYMBOLS = [
    # US Tech Giants
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "NFLX",
    "AMD", "INTC", "ORCL", "CRM", "ADBE", "PYPL", "UBER", "SNAP",
    # US Finance
    "JPM", "BAC", "GS", "V", "MA", "BRK-B",
    # US Healthcare
    "JNJ", "PFE", "UNH", "MRNA",
    # Taiwan Stocks (via ADR or direct)
    "TSM", "UMC", "ASX", "HIMAX",
    # ETFs
    "SPY", "QQQ", "DIA", "VTI",
    # Other Popular
    "BABA", "NIO", "COIN", "PLTR", "RIVN", "GME", "AMC",
]

def fetch_stock_data():
    """Fetch current stock data for all symbols"""
    stocks = []
    
    print(f"Fetching data for {len(STOCK_SYMBOLS)} stocks...")
    
    # Batch fetch using yfinance
    tickers = yf.Tickers(" ".join(STOCK_SYMBOLS))
    
    for symbol in STOCK_SYMBOLS:
        try:
            ticker = tickers.tickers[symbol]
            info = ticker.fast_info
            
            # Get current price and basic info
            current_price = getattr(info, 'last_price', None)
            prev_close = getattr(info, 'previous_close', None)
            
            if current_price is None or current_price == 0:
                # Try history as fallback
                hist = ticker.history(period="2d")
                if len(hist) > 0:
                    current_price = float(hist['Close'].iloc[-1])
                    prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
            
            if current_price is None:
                continue
                
            current_price = float(current_price)
            prev_close = float(prev_close) if prev_close else current_price
            
            change = current_price - prev_close
            change_pct = (change / prev_close * 100) if prev_close != 0 else 0
            
            # Get company name
            try:
                company_name = ticker.info.get('longName', symbol) or ticker.info.get('shortName', symbol)
            except:
                company_name = symbol
            
            stock_data = {
                "symbol": symbol,
                "name": company_name[:40] if company_name else symbol,
                "price": round(current_price, 2),
                "prev_close": round(prev_close, 2),
                "change": round(change, 2),
                "change_pct": round(change_pct, 2),
                "volume": int(getattr(info, 'three_month_average_volume', 0) or 0),
                "market_cap": getattr(info, 'market_cap', None),
                "currency": getattr(info, 'currency', 'USD'),
                "updated_at": datetime.utcnow().isoformat() + "Z"
            }
            
            stocks.append(stock_data)
            print(f"  ✓ {symbol}: ${current_price:.2f} ({change_pct:+.2f}%)")
            
        except Exception as e:
            print(f"  ✗ {symbol}: {e}")
            continue
    
    return stocks


def save_to_json(stocks, output_path="stocks.json"):
    """Save stock data to JSON file"""
    output = {
        "stocks": stocks,
        "count": len(stocks),
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "next_update": (datetime.utcnow() + timedelta(minutes=15)).isoformat() + "Z"
    }
    
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Saved {len(stocks)} stocks to {output_path}")
    return output


if __name__ == "__main__":
    print("🚀 Stock Market Game - Data Fetcher")
    print("=" * 50)
    
    stocks = fetch_stock_data()
    
    # Save to docs folder for GitHub Pages
    save_to_json(stocks, "api/stocks.json")
    
    print(f"\nDone! {len(stocks)}/{len(STOCK_SYMBOLS)} stocks fetched successfully.")
