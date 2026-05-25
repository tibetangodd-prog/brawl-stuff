"""
Stock Market Game - Data Fetcher
- 美股前100: 使用 yfinance (Yahoo Finance)
- 台股前100: 使用台灣證交所官方 API (TWSE Open Data)
"""

import json
import os
import time
import requests
from datetime import datetime, timedelta
import yfinance as yf

# ══════════════════════════════════════════════
# 美股前100大熱門股票
# ══════════════════════════════════════════════
US_SYMBOLS = [
    # 市值前段：科技巨頭
    "AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AVGO",
    "ORCL", "NFLX", "AMD", "ADBE", "CRM", "INTC", "QCOM", "TXN",
    "AMAT", "MU", "KLAC", "LRCX",
    # 金融
    "BRK-B", "JPM", "V", "MA", "BAC", "GS", "MS", "WFC", "AXP", "BLK",
    "SCHW", "C", "SPGI", "MCO", "COF",
    # 醫療
    "LLY", "UNH", "JNJ", "ABBV", "MRK", "TMO", "ABT", "DHR", "AMGN",
    "ISRG", "GILD", "VRTX", "REGN", "BSX", "SYK",
    # 消費/零售
    "AMZN", "COST", "WMT", "HD", "MCD", "SBUX", "NKE", "LOW", "TGT",
    "BKNG", "MAR", "HLT",
    # 工業/能源
    "XOM", "CVX", "CAT", "GE", "BA", "RTX", "HON", "UPS", "LMT", "DE",
    # 電信/媒體
    "DIS", "CMCSA", "T", "VZ", "TMUS",
    # 其他熱門
    "TSLA", "PYPL", "UBER", "ABNB", "SNOW", "PLTR", "COIN", "SHOP",
    "ZM", "ROKU", "RBLX", "HOOD", "RIVN", "LCID",
    # 熱門ETF
    "SPY", "QQQ", "DIA", "VTI", "IWM",
    # 台股ADR（在美上市的台灣公司）
    "TSM", "UMC",
]
# 去重
US_SYMBOLS = list(dict.fromkeys(US_SYMBOLS))[:100]

# ══════════════════════════════════════════════
# 台股前100大（代號清單）
# 來源：台灣證交所市值排名
# ══════════════════════════════════════════════
TW_SYMBOLS = [
    "2330", "2317", "2454", "2382", "2308", "2303", "2881", "2882",
    "2891", "2886", "2884", "2885", "2892", "2883", "2887", "2888",
    "2412", "2002", "1301", "1303", "1326", "2207", "2357", "2379",
    "2395", "3711", "2376", "2408", "3008", "2327", "4938", "2337",
    "2344", "2345", "3034", "3037", "3045", "3231", "3533", "4904",
    "5871", "6505", "6669", "6770", "8046", "9910", "2105", "2049",
    "2915", "1216", "2801", "1402", "1101", "1102", "1216", "2912",
    "2823", "2880", "5880", "2474", "2352", "2301", "2356", "2324",
    "2353", "2360", "2347", "2385", "2迪", "3006", "3考", "3682",
    "4958", "5009", "6176", "6153", "6202", "6239", "6415", "6451",
    "6488", "6547", "6657", "6669", "8詮", "9914", "9917", "9921",
    "2609", "2615", "2618", "2603", "2605", "2606", "2610", "5302",
    "1904", "1907", "2101", "2103",
]

# 清理台股代號（只保留純數字）
TW_SYMBOLS = [s for s in TW_SYMBOLS if s.isdigit()]

# 正確的台股前100（市值排名，純數字代號）
TW_SYMBOLS = [
    "2330", "2317", "2454", "2382", "2308", "2303", "2881", "2882",
    "2891", "2886", "2884", "2885", "2892", "2883", "2887", "2888",
    "2412", "2002", "1301", "1303", "1326", "2207", "2357", "2379",
    "2395", "3711", "2376", "2408", "3008", "2327", "4938", "2337",
    "2344", "2345", "3034", "3037", "3045", "3231", "3533", "4904",
    "5871", "6505", "6669", "6770", "8046", "9910", "2105", "2049",
    "2915", "1216", "2801", "1402", "1101", "1102", "2912", "2823",
    "2880", "5880", "2474", "2352", "2301", "2356", "2324", "2353",
    "2360", "2347", "2385", "3006", "3682", "4958", "5009", "6176",
    "6153", "6202", "6239", "6415", "6451", "6488", "6547", "6657",
    "2609", "2615", "2618", "2603", "2605", "2606", "2610", "5302",
    "1904", "1907", "2101", "2103", "1590", "2618", "3293", "6271",
    "6278", "3008", "2408", "2448",
]
TW_SYMBOLS = list(dict.fromkeys(TW_SYMBOLS))[:100]


# ══════════════════════════════════════════════
# 抓美股資料（yfinance）
# ══════════════════════════════════════════════
def fetch_us_stocks():
    stocks = []
    print(f"\n📈 抓取美股 {len(US_SYMBOLS)} 支...")

    # 分批抓，每批20支，避免超時
    batch_size = 20
    for i in range(0, len(US_SYMBOLS), batch_size):
        batch = US_SYMBOLS[i:i+batch_size]
        print(f"  批次 {i//batch_size + 1}: {', '.join(batch)}")
        try:
            tickers = yf.Tickers(" ".join(batch))
            for symbol in batch:
                try:
                    ticker = tickers.tickers[symbol]
                    info = ticker.fast_info

                    price = getattr(info, 'last_price', None)
                    prev_close = getattr(info, 'previous_close', None)

                    if not price or price == 0:
                        hist = ticker.history(period="2d")
                        if len(hist) >= 1:
                            price = float(hist['Close'].iloc[-1])
                            prev_close = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else price

                    if not price:
                        print(f"    ✗ {symbol}: 無價格資料")
                        continue

                    price = round(float(price), 2)
                    prev_close = round(float(prev_close), 2) if prev_close else price
                    change = round(price - prev_close, 2)
                    change_pct = round(change / prev_close * 100, 2) if prev_close else 0

                    try:
                        raw_info = ticker.info
                        name = raw_info.get('longName') or raw_info.get('shortName') or symbol
                    except:
                        name = symbol

                    stocks.append({
                        "symbol": symbol,
                        "name": name[:40],
                        "price": price,
                        "prev_close": prev_close,
                        "change": change,
                        "change_pct": change_pct,
                        "currency": "USD",
                        "market": "US",
                        "updated_at": datetime.utcnow().isoformat() + "Z"
                    })
                    print(f"    ✓ {symbol}: ${price} ({change_pct:+.2f}%)")

                except Exception as e:
                    print(f"    ✗ {symbol}: {e}")

        except Exception as e:
            print(f"  批次失敗: {e}")

        time.sleep(1)  # 避免被限速

    print(f"  美股完成: {len(stocks)} 支")
    return stocks


# ══════════════════════════════════════════════
# 抓台股資料（台灣證交所官方 API）
# ══════════════════════════════════════════════
def fetch_tw_stocks():
    stocks = []
    print(f"\n🇹🇼 抓取台股 {len(TW_SYMBOLS)} 支...")

    # 證交所每日收盤行情 API
    # 這個 API 每天盤後更新，回傳當日所有股票的收盤資料
    url = "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY_ALL?response=json"

    try:
        resp = requests.get(url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0"
        })
        data = resp.json()

        if data.get("stat") != "OK":
            print(f"  ✗ 證交所 API 回應異常: {data.get('stat')}")
            return fetch_tw_stocks_fallback()

        fields = data.get("fields", [])
        rows = data.get("data", [])

        # 欄位順序: 證券代號, 證券名稱, 成交股數, 成交筆數, 成交金額, 開盤價, 最高價, 最低價, 收盤價, 漲跌(+/-), 漲跌價差, 本益比
        print(f"  證交所回傳 {len(rows)} 筆資料")

        # 建立代號→資料的字典
        tw_data = {}
        for row in rows:
            if len(row) < 9:
                continue
            code = row[0].strip()
            tw_data[code] = row

        # 對照我們的清單
        for symbol in TW_SYMBOLS:
            if symbol not in tw_data:
                print(f"    ✗ {symbol}: 證交所無此資料")
                continue

            row = tw_data[symbol]
            try:
                name = row[1].strip()

                # 價格欄位去除逗號
                def parse_price(s):
                    s = s.strip().replace(",", "")
                    if s in ("--", "", "除權息", "暫停"):
                        return None
                    return float(s)

                close = parse_price(row[8])   # 收盤價
                open_p = parse_price(row[5])  # 開盤價

                if close is None:
                    print(f"    ✗ {symbol} {name}: 無收盤價")
                    continue

                # 漲跌符號 + 漲跌價差
                sign_str = row[9].strip()   # + 或 -
                diff_str = parse_price(row[10]) if len(row) > 10 else 0
                diff = diff_str if diff_str else 0
                if sign_str == "-":
                    diff = -abs(diff)

                prev_close = round(close - diff, 2)
                change_pct = round(diff / prev_close * 100, 2) if prev_close else 0

                stocks.append({
                    "symbol": symbol,
                    "name": name[:20],
                    "price": round(close, 2),
                    "prev_close": prev_close,
                    "change": round(diff, 2),
                    "change_pct": change_pct,
                    "currency": "TWD",
                    "market": "TW",
                    "updated_at": datetime.utcnow().isoformat() + "Z"
                })
                print(f"    ✓ {symbol} {name}: NT${close} ({change_pct:+.2f}%)")

            except Exception as e:
                print(f"    ✗ {symbol}: 解析失敗 {e}")

    except Exception as e:
        print(f"  ✗ 證交所 API 失敗: {e}")
        return fetch_tw_stocks_fallback()

    print(f"  台股完成: {len(stocks)} 支")
    return stocks


def fetch_tw_stocks_fallback():
    """備用：用 yfinance 抓台股（格式為 XXXX.TW）"""
    print("  使用備用方案: yfinance 抓台股...")
    stocks = []
    batch_size = 10

    for i in range(0, len(TW_SYMBOLS), batch_size):
        batch = [s + ".TW" for s in TW_SYMBOLS[i:i+batch_size]]
        try:
            tickers = yf.Tickers(" ".join(batch))
            for j, tw_sym in enumerate(batch):
                symbol_code = TW_SYMBOLS[i+j]
                try:
                    ticker = tickers.tickers[tw_sym]
                    info = ticker.fast_info
                    price = getattr(info, 'last_price', None)
                    prev_close = getattr(info, 'previous_close', None)

                    if not price:
                        hist = ticker.history(period="2d")
                        if len(hist) >= 1:
                            price = float(hist['Close'].iloc[-1])
                            prev_close = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else price

                    if not price:
                        continue

                    price = round(float(price), 2)
                    prev_close = round(float(prev_close), 2) if prev_close else price
                    change = round(price - prev_close, 2)
                    change_pct = round(change / prev_close * 100, 2) if prev_close else 0

                    try:
                        name = ticker.info.get('longName') or ticker.info.get('shortName') or symbol_code
                    except:
                        name = symbol_code

                    stocks.append({
                        "symbol": symbol_code,
                        "name": name[:20],
                        "price": price,
                        "prev_close": prev_close,
                        "change": change,
                        "change_pct": change_pct,
                        "currency": "TWD",
                        "market": "TW",
                        "updated_at": datetime.utcnow().isoformat() + "Z"
                    })
                    print(f"    ✓ {symbol_code}: NT${price}")

                except Exception as e:
                    print(f"    ✗ {symbol_code}: {e}")

        except Exception as e:
            print(f"  批次失敗: {e}")

        time.sleep(1)

    return stocks


# ══════════════════════════════════════════════
# 儲存 JSON
# ══════════════════════════════════════════════
def save_to_json(us_stocks, tw_stocks, output_path="api/stocks.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    output = {
        "us_stocks": us_stocks,
        "tw_stocks": tw_stocks,
        "us_count": len(us_stocks),
        "tw_count": len(tw_stocks),
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 儲存完成: {output_path}")
    print(f"   美股: {len(us_stocks)} 支")
    print(f"   台股: {len(tw_stocks)} 支")
    print(f"   合計: {len(us_stocks) + len(tw_stocks)} 支")


# ══════════════════════════════════════════════
# 主程式
# ══════════════════════════════════════════════
if __name__ == "__main__":
    print("🚀 股海爭霸 - 股票資料抓取程式")
    print("=" * 50)

    us_stocks = fetch_us_stocks()
    tw_stocks = fetch_tw_stocks()

    save_to_json(us_stocks, tw_stocks, "api/stocks.json")

    print("\n✅ 全部完成！")
