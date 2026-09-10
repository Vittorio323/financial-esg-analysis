
# Financial-ESG Analysis — MCP Servers per Claude

Progetto universitario che implementa tre server **MCP (Model Context Protocol)** in Python, utilizzabili da Claude per estrarre dati finanziari e metriche ESG e generare analisi e visualizzazioni automatizzate.

## Architettura

Il progetto è composto da tre server MCP indipendenti, ciascuno con una responsabilità specifiche:

| Server | File | Funzione |
|---|---|---|
| **Market Data Server** | `market_data_server.py` | Recupera quotazioni in tempo reale, dati fondamentali (Market Cap, P/E), serie storiche e performance finanziaria tramite l'API di **yfinance** |
| **ESG Ethics Server** | `esg_ethics_server.py` | Estrae i punteggi di dettaglio sui tre pilastri ESG (Environment, Social, Governance) per le aziende dell'S&P 500 |
| **Analytics Server** | `analytics_server.py` | Genera visualizzazioni (istogrammi, scatter plot, boxplot, barplot) per analizzare distribuzione, correlazioni e confronti settoriali del rischio ESG |

## Requisiti

- Python 3.10+
- Claude Desktop (o altro client compatibile MCP)

## Installazione

```bash
git clone https://github.com/Vittorio323/financial-esg-analysis.git
cd financial-esg-analysis
pip install -r requirements.txt
```

### Dataset ESG

I server `analytics_server.py` ed `esg_ethics_server.py` richiedono il dataset **"SP 500 ESG Risk Ratings"**, disponibile su [Kaggle](https://www.kaggle.com/datasets/pritish509/s-and-p-500-esg-risk-ratings).

**Nota**: i punteggi ESG sono aggiornati alla data di pubblicazione del dataset; per un utilizzo in produzione andrebbero sostituiti con una fonte dati ESG in tempo reale

Scarica il CSV e posizionalo in:
```
data/SP 500 ESG Risk Ratings.csv
```

## Configurazione con Claude Desktop

Aggiungi i server al file di configurazione `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "market-data-server": {
      "command": "python",
      "args": ["/percorso/assoluto/market_data_server.py"]
    },
    "esg-ethics-server": {
      "command": "python",
      "args": ["/percorso/assoluto/esg_ethics_server.py"]
    },
    "analytics-server": {
      "command": "python",
      "args": ["/percorso/assoluto/analytics_server.py"]
    }
  }
}
```

Riavvia Claude Desktop: i tool dei tre server saranno disponibili in conversazione.

## Esempi d'uso

Una volta connessi, puoi chiedere a Claude cose come:

- *"Qual è la quotazione attuale di Apple e come si è mossa negli ultimi 30 giorni?"*
- *"Mostrami il profilo di rischio ESG di Microsoft"*
- *"Genera un boxplot di confronto del rischio ESG tra i settori dell'S&P 500"*

## Struttura del progetto

```
financial-esg-analysis/
├── market_data_server.py
├── esg_ethics_server.py
├── analytics_server.py
├── data/
│   └── SP 500 ESG Risk Ratings.csv   (da scaricare, vedi sopra)
├── outputs/                          (generato automaticamente dai grafici)
├── requirements.txt
└── README.md
```

## Note

Progetto sviluppato per un esame universitario del corso di Laurea Magistrale in Data Science, Università degli Studi di Salerno.

## Autore

**Vittorio Pio Sarno**
[LinkedIn](https://www.linkedin.com/in/vittorio-pio-sarno-8125622ba/)

## Licenza

Distribuito con licenza MIT — vedi il file `LICENSE`.
