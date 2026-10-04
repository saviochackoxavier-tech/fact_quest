# 🛡️ Fact-Quest: The Disinformation Dungeon

> *"The internet is full of monsters. It's time to fight back."*

**Fact-Quest** is a gamified, real-time fact-checking web application built for the **SerpApi India Hackathon 2026**. It transforms the abstract threat of viral misinformation into an interactive dungeon-crawler — where every lie is a monster, every search result is your weapon, and the truth is your ultimate power.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.x-green.svg)](https://www.djangoproject.com/)
[![Powered by SerpApi](https://img.shields.io/badge/Powered%20by-SerpApi-orange.svg)](https://serpapi.com/)

---

## 🎬 Official Demo Video

> **[▶ Watch the full gameplay demo on Google Drive](https://drive.google.com/file/d/1ckHJv1UAWe2cxoPzaZqvgbACEm4Clknu/view?usp=sharing)**

---

## 🎮 The Concept — Why This Exists

Fake news spreads **6x faster** than the truth on social media. Traditional fact-checkers are dry, slow, and ignored by the very audiences that need them most. **Fact-Quest reframes the problem entirely.**

What if debunking a rumor felt like defeating a dungeon boss?

Each viral myth — *"Drinking bleach cures COVID-19"*, *"NASA confirmed 6 days of darkness"*, *"5G towers spread viruses"* — becomes a **Rumor Monster** with its own health bar, difficulty rating, and lore. Players don't just read a verdict; they actively probe the claim, cross-reference sources, and watch the monster lose HP in real time as live SerpApi evidence dismantles the lie piece by piece.

**The result:** media literacy disguised as entertainment.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Browser (Client)                  │
│         Tailwind CSS  ·  Vanilla JS  ·  Fetch API    │
└───────────────────────┬─────────────────────────────┘
                        │ HTTP (Django URLs)
┌───────────────────────▼─────────────────────────────┐
│                  Django Application                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  │
│  │   Views      │  │   Models     │  │  Templates │  │
│  │  (views.py)  │  │ (models.py)  │  │  (Jinja2)  │  │
│  └──────┬───────┘  └──────┬───────┘  └────────────┘  │
│         │                 │                           │
│  ┌──────▼───────────────▼────────────────────────┐   │
│  │            dungeon/utils/serp_verifier.py      │   │
│  │   Truth Score Heuristic · SerpApi Client       │   │
│  │   1-hour result cache · Keyword analysis       │   │
│  └──────────────────────┬────────────────────────┘   │
└─────────────────────────┼───────────────────────────┘
                          │ HTTPS
┌─────────────────────────▼───────────────────────────┐
│                     SerpApi                          │
│         Google Search  ·  Live snippets              │
└─────────────────────────────────────────────────────┘
```

**Request lifecycle:**
1. Player selects a combat action (Source Probe / Cross-Reference / Date Check).
2. The Django view calls `serp_verifier.py` with the monster's claim text.
3. `serp_verifier` queries SerpApi (cached per claim for 1 hour to conserve quota).
4. Returned titles & snippets are scored against a keyword heuristic.
5. A `truth_score` (0–100) is computed and returned as JSON.
6. The frontend JS translates the score into damage dealt, updates the HP bar, and renders source cards.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend | Python 3.8+, Django 4.x | MVC web framework, ORM, URL routing |
| Database | SQLite | Zero-config local persistence |
| Search API | SerpApi (`google-search-results`) | Live Google Search results |
| Frontend | Tailwind CSS (CDN), Vanilla JS | Responsive UI, async combat actions |
| Static files | WhiteNoise (`CompressedStaticFilesStorage`) | Production static file serving |
| WSGI server | Gunicorn | Production HTTP server |

---

## 📂 Project Structure

```
fact_quest_project/
├── manage.py
├── requirements.txt
├── LICENSE
├── README.md
│
├── fact_quest/                  # Django project config
│   ├── settings.py              # WhiteNoise, SERPAPI_KEY, DEBUG flag
│   ├── urls.py
│   └── wsgi.py
│
├── dungeon/                     # Core application
│   ├── models.py                # Zone, Monster, PlayerScore
│   ├── views.py                 # Map, Battle, Custom Arena, Leaderboard
│   ├── urls.py
│   ├── admin.py
│   ├── context.py               # Seed data auto-loader
│   └── utils/
│       └── serp_verifier.py     # SerpApi client + Truth Score heuristic
│
├── templates/                   # Jinja2 HTML templates
│   └── dungeon/
│       ├── base.html
│       ├── map.html
│       ├── battle.html
│       ├── custom_arena.html
│       └── leaderboard.html
│
└── static/                      # CSS, JS, images
```

---

## 🎯 Gameplay Mechanics & Core Features

### 🗺️ 1. World Map
- Displays all **dungeon zones** (e.g., *Health Misinformation*, *Political Propaganda*, *Science Denial*).
- Each zone lists its **Rumor Monsters** with difficulty stars, HP, and a teaser description.
- Players choose their target and enter the Combat Arena.

### ⚔️ 2. Combat Arena
The heart of the game. Three combat actions trigger **live SerpApi queries**:

| Action | Query Strategy | Effect |
|---|---|---|
| **Source Probe** | Searches for the claim + "fact check" | High damage on debunked myths |
| **Cross-Reference** | Searches for the claim + "evidence study" | Moderate damage, reveals scientific consensus |
| **Date Check** | Searches for the claim + "original source date" | Exposes recycled/out-of-context stories |

Each action returns **live source cards** (title, snippet, link) from Google Search, so players see *exactly* why a claim is false. The **Truth Score** (0–100) drives damage calculation — a claim that scores 10/100 on credibility deals 90 damage.

### 🧪 3. Truth Score Heuristic
`serp_verifier.py` applies a weighted keyword analysis over SerpApi snippets:
- **Debunking signals** (`"false"`, `"misleading"`, `"no evidence"`, `"debunked"`) → decrease score
- **Credibility signals** (`"confirmed"`, `"study shows"`, `"peer-reviewed"`) → increase score
- Results are **cached for 1 hour per unique claim** to conserve API quota

> ⚠️ The Truth Score is a game mechanic, not a journalistic verdict.

### 🧩 4. Custom Arena
- Paste **any suspicious headline or claim** into the Custom Arena.
- The engine auto-generates a Boss Monster from the text and runs a full simulated battle using live SerpApi verification.
- Ideal for players who encounter fresh misinformation and want an instant check.

### 🏆 5. XP & Leaderboard
- Defeating a monster awards **XP** (base score × difficulty multiplier).
- Final score formula: `XP × 10 + 50 per cleared monster`
- Top 20 scores are displayed on the global Leaderboard.

---

## 🚀 Local Setup

### Prerequisites
- Python 3.8+
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/saviochackoxavier-tech/fact_quest.git
cd fact_quest/fact_quest_project

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
# or manually:
pip install django google-search-results requests gunicorn whitenoise

# 4. Run migrations and seed data
python manage.py makemigrations dungeon
python manage.py migrate
# Zones and monsters are seeded automatically after migrate
# and again on first page load if the database is empty.

# 5. Start the dev server
python manage.py runserver
```

Open **http://127.0.0.1:8000/** and start slaying rumors.

---

## 🔑 API Configuration

The active SerpApi key is pre-configured in [`dungeon/utils/serp_verifier.py`](fact_quest_project/dungeon/utils/serp_verifier.py). Override it with an environment variable:

```bash
# Linux / macOS
export SERPAPI_KEY="your_serpapi_key_here"

# Windows PowerShell
$env:SERPAPI_KEY="your_serpapi_key_here"
```

Get a free key at **https://serpapi.com/**.

---

## 🌐 Production Deployment

```bash
# 1. Set required environment variables
export DJANGO_DEBUG=0
export DJANGO_SECRET_KEY="a-very-long-random-secret-key"
export SERPAPI_KEY="your_serpapi_key_here"

# 2. Collect static files (WhiteNoise serves them)
python manage.py collectstatic --noinput

# 3. Start Gunicorn
gunicorn fact_quest.wsgi --bind 0.0.0.0:8000 --workers 2
```

**WhiteNoise is already configured** in `settings.py`:
- Middleware: `whitenoise.middleware.WhiteNoiseMiddleware`
- Storage: `CompressedStaticFilesStorage` (gzip + cache headers)
- `STATIC_ROOT`: `BASE_DIR / "staticfiles"`

No separate static file server (nginx for static) required for moderate traffic.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- **[SerpApi](https://serpapi.com/)** — for making live Google Search results accessible via a clean API, and for hosting the India Hackathon 2026.
- The open-source community behind Django, Tailwind CSS, and WhiteNoise.

---

*Built with ❤️ and a healthy distrust of viral WhatsApp forwards.*
