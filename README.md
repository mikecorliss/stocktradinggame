# Stock Trading Game

Full Flask + SQLite + Docker stock trading simulation with user accounts.

## How to Run

```bash
docker build -t stock-trader .
docker run -p 5000:5000 -v $(pwd)/stockgame.db:/app/stockgame.db stock-trader
```

Open http://localhost:5000

Enjoy trading!