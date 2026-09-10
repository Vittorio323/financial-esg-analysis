import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mcp.server.fastmcp import FastMCP

# Inizializzazione del Server MCP per le analisi e visualizzazioni
mcp = FastMCP("Analytics-Server")

# ---- Gestione Dinamica dei Percorsi (Clean Code & Portabilità) ----
# Individua la directory dove risiede lo script corrente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Assicura l'esistenza automatica della cartella di output per le immagini
os.makedirs(OUTPUT_DIR, exist_ok=True)

CSV_PATH = os.path.join(DATA_DIR, "SP 500 ESG Risk Ratings.csv")

# Cache in-memory del DataFrame per ridurre l'I/O su disco O(1) alle chiamate successive
_DF_CACHE = None


def load_and_clean() -> pd.DataFrame:
    """Carica e pulisce il dataset ESG applicando una cache locale in memoria."""
    global _DF_CACHE
    if _DF_CACHE is not None:
        return _DF_CACHE

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"File non trovato nel percorso: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    
    # Rinomina standard delle colonne del dominio
    df = df.rename(columns={
        'Symbol': 'Ticker',
        'Environment Risk Score': 'Env_Score',
        'Social Risk Score': 'Soc_Score',
        'Governance Risk Score': 'Gov_Score'
    })
    
    # Normalizzazione stringhe (PEP8 / Data Cleaning)
    df['Ticker'] = df['Ticker'].astype(str).str.strip().str.upper()

    # Imputazione dei valori mancanti con la media per le feature numeriche
    cols_esg = ['Env_Score', 'Soc_Score', 'Gov_Score']
    for col in cols_esg:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(df[col].mean())

    # Calcolo della media pesata per il Total Risk Score
    df['ESG_Total'] = (
        df['Env_Score'] * 0.4 + 
        df['Soc_Score'] * 0.3 + 
        df['Gov_Score'] * 0.3
    ).round(2)

    _DF_CACHE = df
    return _DF_CACHE


@mcp.tool()
def plot_esg_distribution() -> str:
    """Genera un istogramma della distribuzione del rischio ESG totale."""
    try:
        data = load_and_clean()
        
        # Pulizia del buffer grafico precedente
        plt.clf()
        plt.figure(figsize=(10, 6))
        
        # Generazione dell'istogramma con stima della densità di kernel (KDE)
        sns.histplot(data['ESG_Total'], bins=20, kde=True, color='skyblue')
        plt.title("Distribuzione del Rischio ESG Totale (S&P 500)")
        plt.xlabel("Punteggio di Rischio (Più basso = Migliore)")
        plt.ylabel("Frequenza")

        img_path = os.path.join(OUTPUT_DIR, "esg_distribution.png")
        plt.savefig(img_path, bbox_inches='tight')
        plt.close()
        
        return f"Istogramma generato con successo: {img_path}"
    except Exception as e:
        return f"Errore durante la generazione del grafico: {str(e)}"


@mcp.tool()
def plot_esg_correlation(metric_x: str = "Env_Score", metric_y: str = "Soc_Score") -> str:
    """Genera uno scatter plot per valutare la correlazione tra due metriche ESG."""
    try:
        data = load_and_clean()
        
        plt.clf()
        plt.figure(figsize=(10, 6))
        
        # Regressione lineare visiva per identificare trend e correlazione
        sns.regplot(
            data=data, 
            x=metric_x, 
            y=metric_y, 
            scatter_kws={'alpha': 0.5}, 
            line_kws={'color': 'red'}
        )
        plt.title(f"Correlazione tra {metric_x} e {metric_y}")
        
        img_path = os.path.join(OUTPUT_DIR, "esg_correlation.png")
        plt.savefig(img_path, bbox_inches='tight')
        plt.close()
        
        return f"Scatter plot di correlazione generato: {img_path}"
    except Exception as e:
        return f"Errore durante il plot della correlazione: {str(e)}"


@mcp.tool()
def plot_sector_comparison() -> str:
    """Genera un Boxplot per confrontare le distribuzioni di rischio ESG tra settori."""
    try:
        data = load_and_clean()
        
        plt.clf()
        plt.figure(figsize=(12, 8))
        
        # Boxplot per evidenziare mediana, quartili ed eventuali outlier per settore
        sns.boxplot(data=data, x='ESG_Total', y='Sector', palette='Set2')
        plt.title("Confronto Rischio ESG per Settore Industriale")
        plt.xlabel("Punteggio ESG Totale")
        plt.tight_layout()

        img_path = os.path.join(OUTPUT_DIR, "sector_comparison.png")
        plt.savefig(img_path, bbox_inches='tight')
        plt.close()
        
        return f"Boxplot settoriale generato: {img_path}"
    except Exception as e:
        return f"Errore durante la generazione del boxplot: {str(e)}"


@mcp.tool()
def plot_company_esg_bar(ticker: str) -> str:
    """Genera un barplot dei tre pilastri ESG per una specifica azienda."""
    try:
        df = load_and_clean()
        target = ticker.strip().upper()
        res = df[df['Ticker'] == target]
        
        if res.empty:
            return f"Nessun dato trovato nel dataset per il ticker: {target}"

        row = res.iloc[0]
        labels = ['Environment', 'Social', 'Governance']
        values = [row['Env_Score'], row['Soc_Score'], row['Gov_Score']]
        colors = ['green', 'steelblue', 'orange']

        plt.clf()
        plt.figure(figsize=(8, 5))
        plt.bar(labels, values, color=colors)
        plt.title(f"Profilo di Rischio ESG - {target}")
        plt.ylabel("Risk Score (0-100)")
        plt.ylim(0, max(values) * 1.2 if max(values) > 0 else 100)

        img_path = os.path.join(OUTPUT_DIR, f"{target}_esg_bar.png")
        plt.savefig(img_path, bbox_inches='tight')
        plt.close()
        
        return f"Barplot ESG generato per {target}: {img_path}"
    except Exception as e:
        return f"Errore durante il calcolo per il ticker {ticker}: {str(e)}"


if __name__ == "__main__":
    mcp.run()