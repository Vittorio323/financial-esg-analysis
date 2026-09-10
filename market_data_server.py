import yfinance as yf
import pandas as pd
from mcp.server.fastmcp import FastMCP

# Inizializzazione del Server MCP per la gestione dei dati di mercato in tempo reale
mcp = FastMCP("Market-Data-Server")


def format_big_numbers(num) -> str:
    """Formatta cifre finanziarie di grandi dimensioni per una lettura pulita."""
    if isinstance(num, (int, float)):
        if num >= 1e12:
            return f"{num / 1e12:.2f} T (Trilioni USD)"
        if num >= 1e9:
            return f"{num / 1e9:.2f} B (Miliardi USD)"
        if num >= 1e6:
            return f"{num / 1e6:.2f} M (Milioni USD)"
    return str(num)


@mcp.tool()
def get_live_market_data(ticker: str) -> str:
    """Recupera la quotazione corrente ed il delta percentuale rispetto alla chiusura precedente."""
    try:
        target = ticker.strip().upper()
        stock = yf.Ticker(target)
        
        # Fetch minimale dell'ultimo giorno per ottimizzare la banda di rete
        data = stock.history(period="1d")
        
        if data.empty:
            return f"Impossibile reperire quotazioni per il ticker: {target}."
        
        prezzo_attuale = data['Close'].iloc[-1]
        
        # Recupero del prezzo di chiusura precedente con fallback di sicurezza
        info = stock.info
        prev_close = info.get('previousClose', prezzo_attuale)
        
        var_perc = ((prezzo_attuale - prev_close) / prev_close) * 100 if prev_close else 0.0
        
        return f"📈 {target}: Prezzo Attuale {prezzo_attuale:.2f} USD ({var_perc:+.2f}%)"
    except Exception as e:
        return f"Errore di connessione API durante il recupero quotazione: {str(e)}"


@mcp.tool()
def get_stock_fundamentals(ticker: str) -> str:
    """Recupera la Market Cap, il P/E Ratio e le escursioni di prezzo a 52 settimane."""
    try:
        target = ticker.strip().upper()
        stock = yf.Ticker(target)
        info = stock.info
        
        mkt_cap = format_big_numbers(info.get('marketCap', 'N/D'))
        pe_ratio = info.get('forwardPE', 'N/D')
        
        if isinstance(pe_ratio, (int, float)):
            pe_ratio = round(pe_ratio, 2)
            
        high_52 = info.get('fiftyTwoWeekHigh', 'N/D')
        low_52 = info.get('fiftyTwoWeekLow', 'N/D')
        
        return (
            f"📋 Dati Fondamentali per {target}:\n"
            f"- Market Capitalization: {mkt_cap}\n"
            f"- Forward P/E Ratio: {pe_ratio}\n"
            f"- Range 52 Settimane: {low_52} - {high_52} USD"
        )
    except Exception as e:
        return f"Errore nel recupero dei fondamentali per {ticker}: {str(e)}"


@mcp.tool()
def get_historical_data(ticker: str, days: int = 30) -> str:
    """Estrae la serie storica dei prezzi di chiusura per un intervallo di giorni specificato."""
    try:
        target = ticker.strip().upper()
        stock = yf.Ticker(target)
        hist = stock.history(period=f"{days}d")
        
        if hist.empty:
            return f"Nessuna serie storica disponibile per {target}."
        
        prezzi = hist['Close'].round(2).to_dict()
        prezzi_puliti = {str(date.date()): price for date, price in prezzi.items()}
        
        return f"📅 Storico prezzi di chiusura {target} (ultimi {days} giorni):\n{prezzi_puliti}"
    except Exception as e:
        return f"Errore nel recupero della serie storica per {ticker}: {str(e)}"


@mcp.tool()
def get_financial_performance(ticker: str) -> str:
    """Estrae metriche operative di bilancio: EBITDA, Margini di Profitto e Crescita dei Ricavi."""
    try:
        target = ticker.strip().upper()
        stock = yf.Ticker(target)
        info = stock.info
        
        ebitda = info.get('ebitda', 'N/D')
        profit_margins = info.get('profitMargins', 'N/D')
        revenue_growth = info.get('revenueGrowth', 'N/D')
        total_revenue = info.get('totalRevenue', 'N/D')

        margin_pc = f"{profit_margins * 100:.2f}%" if isinstance(profit_margins, (int, float)) else "N/D"
        growth_pc = f"{revenue_growth * 100:.2f}%" if isinstance(revenue_growth, (int, float)) else "N/D"

        return (
            f"📊 Performance Finanziaria per {target}:\n"
            f"- EBITDA: {format_big_numbers(ebitda)}\n"
            f"- Ricavi Totali: {format_big_numbers(total_revenue)}\n"
            f"- Margine di Profitto: {margin_pc}\n"
            f"- Crescita Ricavi (YoY): {growth_pc}"
        )
    except Exception as e:
        return f"Errore nel recupero della performance per {ticker}: {str(e)}"


if __name__ == "__main__":
    mcp.run()