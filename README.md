# Stock Trading Game

A full-stack stock trading simulation with Flask, SQLite persistence, user authentication, and Docker support.

## Quick Start with Docker

```bash
docker build -t stock-trader .
docker run -p 5000:5000 -v $(pwd)/stockgame.db:/app/stockgame.db stock-trader
```

Open http://localhost:5000

## Features
- User registration & login
- Persistent portfolio across sessions
- Real-time price simulation
- Beautiful chart visualization
- Docker ready

Made with ❤️ using Grok