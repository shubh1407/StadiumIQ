# 🏟️ StadiumIQ: AI Stadium Intelligence Platform (FIFA World Cup 2026)

StadiumIQ is an enterprise-grade, production-ready Generative AI platform designed to orchestrate and optimize operations, logistics, fan experience, and safety for the **FIFA World Cup 2026**. Utilizing state-of-the-art LLMs (Llama-3.3-70B-Versatile via the Groq API) and high-performance visualizations, StadiumIQ serves as the central nervous system for stadium command centers, transit hubs, and fan spaces.

---

## 📋 Problem Statement

Hosting a mega-event like the FIFA World Cup 2026 presents massive challenges:
* **Crowd Congestion & Safety**: Identifying safety hazards, bottleneck zones, and predicting stampedes in real-time.
* **Complex Logistics & Transit**: Seamless coordination of multi-modal transport (Metro, Bus, Rideshare, Walking, Parking) for up to 100,000 fans per stadium.
* **Inclusive Accessibility**: Real-time personalized assistance for fans with physical, visual, or hearing impairments.
* **Environmental Impact & Sustainability**: Managing massive waste generation, carbon footprint, and energy grids efficiently.
* **Incident Response & Operations**: Bridging communication between security, ops, and volunteers with fast triage and automated briefings.

StadiumIQ leverages centralized prompt templates, structured output parsing (Pydantic models), conversation memory, and automated simulations to address these challenges head-on.

---

## 🏗️ System Architecture

StadiumIQ is built with a highly modular, decoupled, and clean architecture adhering strictly to SOLID design principles.

```
stadiumiq/
│
├── app.py                      # Main entrypoint & UI layout coordinator
├── requirements.txt            # Declared external Python dependencies
├── README.md                   # Enterprise technical documentation
├── LICENSE                     # Standard open-source license documentation
├── .gitignore                  # Active Git exclude rules
├── .env.example                # Example template for environmental secrets
├── run_app.py                  # Streamlit CLI runner & arg sanitizer
│
├── assets/
│   └── styles.css              # Glassmorphic, modern responsive CSS styles
│
├── models/
│   └── schemas.py              # Central Pydantic models for structured outputs
│
├── modules/
│   ├── fan_assistant.py        # 1. AI Chatbot (Navigation, Tickets, Schedules, Memory)
│   ├── crowd.py                # 2. Crowd Intelligence (Density heatmaps, Risk forecasting)
│   ├── accessibility.py        # 3. Accessibility Hub (Assisted routing, Audio narration)
│   ├── transport.py            # 4. Transport Nexus (Multi-modal transit recommendations)
│   ├── sustainability.py       # 5. Sustainability Monitor (Carbon, Waste, Eco-gamification)
│   └── operations.py           # 6. Operations Command (Incident dispatch, Shift briefings)
│
├── services/
│   ├── groq_client.py          # Groq API Gateway (Llama-3.3 gateway with retry logic)
│   ├── prompt_manager.py       # Centrally versioned, structured prompt templates
│   ├── llm_chain.py            # Reusable chains (Context injection & token streaming)
│   ├── memory.py               # Conversational thread state management
│   ├── output_parser.py        # Clean validator mapping LLM raw text to schemas
│   ├── simulator.py            # High-fidelity realistic mock data generator
│   └── utils.py                # Formatting, logging, and styling utilities
│
└── tests/                      # Full test suite covering chains & simulators
```

---

## 🛠️ Tech Stack

* **Language**: Python 3.12 (Strong type hinting and PEP 8 compliance)
* **Frontend/Dashboard**: Streamlit (Glassmorphic dark design, custom CSS, tabs, metrics, charts)
* **Core LLM**: Groq Cloud API (Utilizing `llama-3.3-70b-versatile` for lightning-fast sub-second latency)
* **Structured Modeling**: Pydantic v2 (Guaranteed type safety, input validation, and structural JSON mappings)
* **Resiliency & Retry**: Tenacity (Automatic exponential backoff, rate limit handling, and API fallbacks)
* **Data & Analytics**: Pandas, Plotly Express, and Altair (High-performance interactive maps, charts, and metrics)
* **Logging**: Loguru (Robust structural logging, outputting standardized audit records)
* **Fast Serialization**: Orjson (Highly performant JSON encoder and decoder)

---

## 🌟 Key Functional Modules

### 1️⃣ Fan Assistant
An interactive AI chatbot utilizing conversation state memory. Handles multi-lingual fan requests for navigation, ticket status, schedules, and restrooms. Supports streaming token outputs and quick-suggested prompts.

### 2️⃣ Crowd Intelligence
Visualizes live heatmaps, density counts, and uses AI to predict risk levels (e.g., crush risks, bottle-necks, slow ingress). Generates real-time operator alerts and security dispatch actions.

### 3️⃣ Accessibility Hub
Designed with inclusivity in mind. Provides wheelchair-accessible route guides, voice-ready route narrations, companion dispatch simulator, and global display switches for high contrast and large text.

### 4️⃣ Transport Nexus
Analyzes active traffic flows across rail, metro, shuttle buses, and rideshares. Uses LLMs to generate optimized transit recommendations and travel-time estimates for crowd dispersion.

### 5️⃣ Sustainability Monitor
Provides carbon footprint, waste recycling, and energy grid load analytics. Gamifies sustainability with fan-driven leaderboards and automated, contextual eco-friendly recommendation engines.

### 6️⃣ Operations Command Center
The central terminal for administrators. Streamlines security incident reporting, classifies issues automatically by priority (Critical, High, Medium, Low), assigns work coordinates to closest volunteers, and generates ready-to-read pre-shift crew briefings.

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
Ensure you have Python 3.12+ and `pip` installed on your machine.

### 2. Clone and Prepare Workspace
```bash
git clone https://github.com/your-username/stadiumiq.git
cd stadiumiq
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Secrets & API Keys
Create a `.env` file based on the provided template:
```bash
cp .env.example .env
```
Fill in your `GROQ_API_KEY`:
```env
GROQ_API_KEY="gsk_your_actual_key_here"
```

### 5. Running the Application
StadiumIQ includes a dedicated wrapper `run_app.py` to prevent environment-specific argument conflicts:
```bash
python run_app.py
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🛡️ Reliability & Robust Fallback (Demo Mode)
StadiumIQ is engineered to be **100% resilient**. If the Groq API is unreachable, rate-limited, or if the user is running the app without an API key:
1. The platform automatically detects the omission.
2. A gentle, toast-based warning notification is issued.
3. The system switches seamlessly into **Simulation/Demo Mode**, utilizing a high-fidelity synthetic generation service (`simulator.py`) to supply incredibly realistic, context-aware operational answers, ensuring zero downtime.

---

## 📈 Future Scope & Improvements
* **Live IoT Stream Integration**: Connect physical ticket scanner turnstiles and security cameras.
* **Offline Embedding Vectors**: Implement local SQLite Vector DB search for static stadium maps.
* **Native Voice Capture**: Implement client-side Web Audio API recorder to support hands-free operations.
