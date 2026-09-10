import os
import pandas as pd
from mcp.server.fastmcp import FastMCP

# Inizializzazione del Server MCP per le metriche etiche ESG
mcp = FastMCP("ESG-Ethics-Server")

# ---- Gestione Dinamica dei Percorsi ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "SP 500 ESG Risk Ratings.csv")

# Cache locale per evitare chiamate ridondanti al file-system
_DF_CACHE = None


def load_and_clean() -> pd.DataFrame:
    """Carica e pulisce il dataset ESG applicando la cache locale."""
    global _DF_CACHE
    if _DF_CACHE is not None:
        return _DF_CACHE

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"File non trovato nel percorso: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    
    df = df.rename(columns={
        'Symbol': 'Ticker',
        'Environment Risk Score': 'Env_Score',
        'Social Risk Score': 'Soc_Score',
        'Governance Risk Score': 'Gov_Score'
    })
    
    df['Ticker'] = df['Ticker'].astype(str).str.strip().str.upper()

    cols_esg = ['Env_Score', 'Soc_Score', 'Gov_Score']
    for col in cols_esg:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(df[col].mean())

    df['ESG_Total'] = (
        df['Env_Score'] * 0.4 + 
        df['Soc_Score'] * 0.3 + 
        df['Gov_Score'] * 0.3
    ).round(2)

    _DF_CACHE = df
    return _DF_CACHE


@mcp.tool()
def get_company_esg_metrics(ticker: str) -> str:
    """Estrae i punteggi di dettaglio sui tre pilastri ESG per una determinata società."""
    try:
        df = load_and_clean()
        target = ticker.strip().upper()
        res = df[df['Ticker'] == target]
        
        if res.empty:
            return f"Nessun dato ESG reperibile per l'azienda {target}."

        row = res.iloc[0]
        env = row['Env_Score']
        soc = row['Soc_Score']
        gov = row['Gov_Score']
        tot = row['ESG_Total']
        
        return (
            f"📊 Metriche ESG per {target}:\n"
            f"- Environmental Risk: {env}\n"
            f"- Social Risk: {soc}\n"
            f"- Governance Risk: {gov}\n"
            f"- Punteggio Totale Pesato: {tot}"
        )
    except Exception as e:
        return f"Errore nel recupero delle metriche per {ticker}: {str(e)}"


if __name__ == "__main__":
    mcp.run()