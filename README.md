# 🚑 AccidentAI — Accident Severity & Hospital Recommendation System

An AI-powered web application that analyzes accident images using **GPT-4o Vision**, classifies injury severity, and recommends the **nearest suitable hospitals** based on real-time GPS location.

---

## 📋 Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Hospital Database](#hospital-database)
- [Severity Classification Rules](#severity-classification-rules)
- [Screenshots](#screenshots)
- [Disclaimer](#disclaimer)

---

## Overview

**AccidentAI** is a full-stack web application designed to assist in emergency situations. A user uploads an accident/injury photo, and the system:

1. Analyzes the image using **OpenAI GPT-4o Vision** to detect injuries
2. Classifies the severity as **Minor**, **Moderate**, or **Severe**
3. Captures the user's **GPS location** via the browser
4. Filters and ranks **nearby hospitals** by specialization, distance, and emergency availability
5. Presents a clean, actionable report with hospital recommendations

The system also includes a **demo/fallback mode** that works without an API key for testing purposes.

---

## How It Works

```
┌──────────────────────────────────────────────────────────────────────┐
│                        END-TO-END FLOW                               │
│                                                                      │
│  ┌─────────┐    ┌──────────────┐    ┌────────────────┐              │
│  │  User    │───▶│ Upload Image │───▶│ GPT-4o Vision  │              │
│  │ Browser  │    │ (JPG/PNG)    │    │ Injury Analysis│              │
│  └─────────┘    └──────────────┘    └───────┬────────┘              │
│       │                                      │                       │
│       │ GPS Location                         │ Injury JSON           │
│       │ (Geolocation API)                    ▼                       │
│       │              ┌───────────────────────────────────┐           │
│       │              │  Severity Classifier (Rule-Based) │           │
│       │              │  Minor / Moderate / Severe        │           │
│       │              └───────────────┬───────────────────┘           │
│       │                              │                               │
│       ▼                              ▼                               │
│  ┌──────────┐    ┌─────────────────────────────────┐                │
│  │ Lat/Lng  │───▶│ Hospital Filter & Ranking Engine │                │
│  │ Coords   │    │                                  │                │
│  └──────────┘    │ 1. Match specialization to injury│                │
│                  │ 2. Calculate distance (Haversine) │                │
│                  │ 3. Prioritize emergency services  │                │
│                  │ 4. Rank & return top 6 hospitals  │                │
│                  └──────────────┬────────────────────┘               │
│                                 │                                    │
│                                 ▼                                    │
│                  ┌──────────────────────────────┐                    │
│                  │   Results Dashboard           │                    │
│                  │  • Injury type & severity     │                    │
│                  │  • AI confidence score         │                    │
│                  │  • Ranked hospital list        │                    │
│                  │  • Distance & contact info     │                    │
│                  └──────────────────────────────┘                    │
└──────────────────────────────────────────────────────────────────────┘
```

### Step-by-Step Breakdown

| Step | Action | Technology |
|------|--------|------------|
| 1 | User opens the web app in a browser | Flask, HTML/CSS/JS |
| 2 | User uploads an accident image (JPG/JPEG/PNG) | JavaScript FileReader, Drag & Drop API |
| 3 | Browser captures GPS coordinates | JavaScript Geolocation API |
| 4 | Image is sent to the Flask backend via `POST /analyze` | AJAX Fetch API, Flask |
| 5 | Backend converts image to Base64 and sends to GPT-4o Vision | OpenAI API, Python |
| 6 | GPT-4o returns structured injury data (type, body part, description) | OpenAI GPT-4o Vision |
| 7 | Severity classifier categorizes injuries (Minor/Moderate/Severe) | Python rule-based logic |
| 8 | Frontend sends GPS coords + injury data to `POST /hospitals` | AJAX Fetch API |
| 9 | Backend queries SQLite hospital database | SQLite, Python |
| 10 | Haversine formula calculates distance to each hospital | Python math library |
| 11 | Hospitals are filtered by specialization and ranked | Python filtering logic |
| 12 | Results displayed: injuries, severity, ranked hospitals | HTML/CSS/JS |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   FRONTEND (Browser)                     │
│  ┌────────────┐  ┌──────────┐  ┌─────────────────────┐  │
│  │ index.html │  │ style.css│  │      app.js         │  │
│  │ Bootstrap 5│  │ Calm UI  │  │ Upload, GPS, Render │  │
│  └────────────┘  └──────────┘  └─────────────────────┘  │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP (AJAX)
                        ▼
┌─────────────────────────────────────────────────────────┐
│                BACKEND (Flask / Python)                   │
│                                                          │
│  app.py ─── Entry point, route registration              │
│  config.py ─ Environment variables, paths                │
│                                                          │
│  ┌─────────────────────────────────────────────────┐     │
│  │                   ROUTES                         │     │
│  │  analyze.py ──── POST /analyze (image upload)   │     │
│  │  hospitals.py ── POST /hospitals (GPS + filter)  │     │
│  └─────────────────────────────────────────────────┘     │
│                                                          │
│  ┌─────────────────────────────────────────────────┐     │
│  │                  MODULES                         │     │
│  │  llm_analysis.py ── GPT-4o Vision API client    │     │
│  │  severity.py ─────── Rule-based classifier      │     │
│  │  hospital_filter.py ─ Filtering & ranking       │     │
│  │  distance.py ──────── Haversine formula          │     │
│  └─────────────────────────────────────────────────┘     │
│                                                          │
│  ┌─────────────────────────────────────────────────┐     │
│  │                 DATABASE                         │     │
│  │  setup_db.py ──── SQLite setup & seed script    │     │
│  │  hospitals.db ─── 18 hospitals (auto-generated) │     │
│  └─────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              EXTERNAL SERVICE                            │
│  OpenAI GPT-4o Vision API (Image → Injury Analysis)     │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | HTML5, CSS3, JavaScript (ES6) | User interface |
| **CSS Framework** | Bootstrap 5.3 | Responsive grid & components |
| **Backend** | Python 3, Flask 3.0 | Web server & API |
| **AI/LLM** | OpenAI GPT-4o Vision | Accident image analysis |
| **Database** | SQLite 3 | Hospital data storage |
| **Distance Calc** | Haversine Formula (Python `math`) | GPS-based distance |
| **Location** | Browser Geolocation API | User GPS coordinates |
| **Config** | python-dotenv | Environment variable management |

---

## Project Structure

```
Health Care-AI-LLM/
│
├── app.py                    # Flask application entry point
├── config.py                 # Configuration (API keys, paths, upload settings)
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (API key) — not committed
├── README.md                 # This file
│
├── database/
│   ├── setup_db.py           # SQLite schema creation & hospital seeding
│   └── hospitals.db          # SQLite database (auto-generated on first run)
│
├── modules/
│   ├── __init__.py           # Package init
│   ├── llm_analysis.py       # GPT-4o Vision API integration
│   ├── severity.py           # Rule-based severity classifier
│   ├── hospital_filter.py    # Hospital filtering & ranking engine
│   └── distance.py           # Haversine distance calculator
│
├── routes/
│   ├── __init__.py           # Package init
│   ├── analyze.py            # POST /analyze — image upload & AI analysis
│   └── hospitals.py          # POST /hospitals — hospital recommendations
│
├── static/
│   ├── css/
│   │   └── style.css         # Application styles (calm light theme)
│   ├── js/
│   │   └── app.js            # Frontend logic (upload, GPS, rendering)
│   └── uploads/              # Uploaded images (auto-created)
│
└── templates/
    └── index.html            # Main HTML template
```

---

## Setup & Installation

### Prerequisites

- **Python 3.8+** installed on your system
- **pip** (Python package manager)
- An **OpenAI API key** with GPT-4o Vision access (optional — demo mode works without it)

### Step 1 — Clone or Download the Project

```bash
git clone <repository-url>
cd Health-Care-AI-LLM
```

### Step 2 — Create a Virtual Environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `flask==3.0.3` — Web framework
- `python-dotenv==1.0.1` — Environment variable loader
- `openai==1.51.0` — OpenAI API client

### Step 4 — Configure Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

> **Note:** If you don't have an API key, the app runs in **demo mode** with simulated injury analysis results.

---

## Configuration

All configuration is managed in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `OPENAI_API_KEY` | From `.env` | OpenAI API key for GPT-4o Vision |
| `UPLOAD_FOLDER` | `static/uploads/` | Directory for uploaded images |
| `ALLOWED_EXTENSIONS` | `jpg, jpeg, png` | Accepted image formats |
| `MAX_CONTENT_LENGTH` | `16 MB` | Maximum upload file size |
| `DB_PATH` | `database/hospitals.db` | SQLite database location |

---

## Running the Application

```bash
# Make sure virtual environment is activated
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows

# Run the application
python app.py
```

You will see:

```
✅ Database seeded with 18 hospitals at: database/hospitals.db
🚑  Accident Severity & Hospital Recommendation System
🌐  Running at: http://127.0.0.1:5050
```

Open your browser and navigate to **http://127.0.0.1:5050**

### Using the Application

1. **Allow location access** when prompted by the browser
2. **Upload an accident image** — click the upload zone or drag & drop a JPG/PNG
3. **Click "Analyze Now"** — the AI analyzes the image
4. **View results** — injury details, severity level, and ranked hospitals are displayed

---

## API Endpoints

### `POST /analyze`

Uploads an accident image and returns AI-powered injury analysis.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | File | Yes | Accident image (JPG/JPEG/PNG) |

**Response:** `application/json`

```json
{
  "image_filename": "a1b2c3d4.jpg",
  "injuries": [
    {
      "type": "Head Trauma",
      "description": "Visible contusion on the forehead",
      "body_part": "Head"
    }
  ],
  "primary_injury_type": "Head Trauma",
  "severity": "Severe",
  "overall_description": "Severe head trauma with visible contusion",
  "confidence": 0.87,
  "requires_emergency": true,
  "demo_mode": false
}
```

---

### `POST /hospitals`

Returns ranked hospitals based on injury type, severity, and user location.

**Request:** `application/json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `lat` | Float | Yes | User latitude |
| `lng` | Float | Yes | User longitude |
| `injury_type` | String | No | Detected injury type |
| `severity` | String | No | Severity level (Minor/Moderate/Severe) |

**Response:** `application/json`

```json
{
  "hospitals": [
    {
      "id": 1,
      "name": "Apollo Hospital",
      "specialization": "Trauma Care",
      "latitude": 17.4435,
      "longitude": 78.3772,
      "emergency": 1,
      "contact": "+91-40-23607777",
      "distance_km": 2.34
    }
  ],
  "count": 6
}
```

---

## Hospital Database

The system comes pre-seeded with **18 hospitals** across Hyderabad, India, covering 4 specializations:

| Specialization | Count | Hospitals |
|---------------|-------|-----------|
| **Trauma Care** | 5 | Apollo, NIMS, Osmania General, Global, Maxcure |
| **Orthopedic** | 5 | Yashoda, Kamineni, Star, Sunshine, Lotus Children |
| **Emergency** | 5 | Care, Medicover, Continental, Virinchi, Rainbow |
| **Neurology** | 3 | KIMS, Manipal, Aster Prime |

Each hospital record stores:
- Name, Specialization, Latitude, Longitude, Emergency availability (yes/no), Contact number

---

## Severity Classification Rules

The system uses **keyword-based rules** to classify injuries into three levels:

| Severity | Example Keywords | Action |
|----------|-----------------|--------|
| 🔴 **Severe** | Head trauma, skull fracture, internal bleeding, spinal injury, amputation, severe burns, cardiac arrest | Immediate emergency response |
| 🟠 **Moderate** | Fracture, broken bone, concussion, dislocation, whiplash, contusion, laceration | Urgent medical attention |
| 🟢 **Minor** | Minor cut, abrasion, scratch, bruise, surface wound, minor swelling | Standard medical care |

### Injury-to-Hospital Specialization Mapping

| Injury Type | Preferred Specialization |
|------------|-------------------------|
| Head injury / Brain trauma | Neurology → Trauma Care → Emergency |
| Fracture / Broken bone | Orthopedic → Trauma Care |
| External / Internal bleeding | Emergency → Trauma Care |
| Minor cuts / Abrasions | Emergency |

---

## Hospital Ranking Algorithm

Hospitals are ranked using a **multi-factor scoring system**:

1. **Specialization match** — How well the hospital's specialization matches the detected injury (highest weight)
2. **Emergency availability** — Hospitals with emergency services are prioritized for Severe/Moderate injuries
3. **Distance** — Closer hospitals rank higher (calculated using the Haversine formula)

The system always returns at least **6 hospitals** to ensure the user has options.

---

## Demo Mode

If no OpenAI API key is configured, the application runs in **demo mode**:

- Image upload still works normally
- A simulated injury analysis is returned (External Bleeding + Body Trauma)
- All hospital filtering, ranking, and distance features work normally
- A yellow banner indicates demo mode in the results

---

## Cross-Platform Compatibility

This application runs on **any operating system**:

| OS | Supported | Notes |
|----|-----------|-------|
| macOS | ✅ | Fully tested |
| Windows | ✅ | Use `venv\Scripts\activate` |
| Linux | ✅ | Use `source venv/bin/activate` |

All file paths use `os.path.join()` for cross-platform compatibility. No OS-specific dependencies.

---

## Disclaimer

> ⚠️ **This application is for educational and demonstration purposes only.**  
> It is NOT a substitute for professional medical diagnosis or emergency services.  
> In a real emergency, always call **112** (India) or your local emergency number immediately.

---

## License

This project is developed for academic/educational purposes.

---

*Built with Python, Flask, GPT-4o Vision, SQLite & the Haversine Formula*
