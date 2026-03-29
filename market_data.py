import yfinance as yf
import logging

logger = logging.getLogger(__name__)

def fetch_market_snapshot() -> dict:
    """
    Fetches the current or latest closing price and percentage change 
    for major market indices/assets.
    """
    symbols = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "Bitcoin": "BTC-USD",
        "10-Yr Yield": "^TNX"
    }
    
    snapshot = {}
    logger.info("Fetching market data snapshot...")
    
    for name, ticker in symbols.items():
        try:
            stock = yf.Ticker(ticker)
            # Fetch last 2 days to calculate % change
            hist = stock.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[0]
                current = hist['Close'].iloc[1]
                change_pct = ((current - prev_close) / prev_close) * 100
                
                # Format to 2 decimal places
                snapshot[name] = {
                    "price": round(current, 2),
                    "change_pct": round(change_pct, 2)
                }
            elif len(hist) == 1:
                # Fallback if only 1 day of data is available
                current = hist['Close'].iloc[0]
                snapshot[name] = {
                    "price": round(current, 2),
                    "change_pct": 0.0
                }
            else:
                snapshot[name] = {"price": 0.0, "change_pct": 0.0}
        except Exception as exc:
            logger.warning(f"Could not fetch data for {name} ({ticker}): {exc}")
            snapshot[name] = {"price": 0.0, "change_pct": 0.0}
            
    logger.info("Market data snapshot fetched successfully.")
    return snapshot
