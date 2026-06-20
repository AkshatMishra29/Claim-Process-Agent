# 🛡️ Claim Processing Agent

An AI-powered damage claim verification system built with **Google Gemini** and **Streamlit**. It lets users submit damage photos and a written claim, then uses a multimodal AI agent to analyse the evidence and return a structured verdict.

---

## ✨ Features

| Feature | Details |
|---|---|
| 📷 **Multi-image upload** | Accepts multiple damage photos per claim |
| 🤖 **Gemini vision analysis** | Uses `gemini-3.1-flash-lite` to evaluate images against the claim |
| 📋 **Structured output** | Returns severity, issue type, risk flags, and claim status |
| 🕵️ **User history risk scoring** | Cross-references past claim history for fraud signals |
| ✅ **Pydantic validation** | All AI responses are validated with a typed schema |
| 📊 **CSV data integration** | Loads claim & history data from CSV files |

---

## 🗂️ Project Structure

```
Claim Processing Agent Project/
└── damage_claim_verifier/
    ├── agent.py          # Core AI agent – calls Gemini, builds prompts
    ├── app.py            # Streamlit UI
    ├── validator.py      # Pydantic model for ClaimAnalysisResult
    ├── requirements.txt  # Python dependencies
    ├── .env.example      # Template for environment variables
    └── data/
        ├── claims.csv         # Sample claim records
        ├── sample_claims.csv  # Additional sample data
        └── user_history.csv   # User claim history for risk scoring
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/AkshatMishra29/Claim-Process-Agent.git
cd Claim-Process-Agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r damage_claim_verifier/requirements.txt
```

### 4. Configure environment variables

Copy the example env file and add your API key:

```bash
cp damage_claim_verifier/.env.example damage_claim_verifier/.env
```

Edit `.env`:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

> 🔑 Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 5. Run the app

```bash
streamlit run damage_claim_verifier/app.py
```

The app will open at `http://localhost:8501`.

---

## 🧠 How It Works

1. **User submits** a damage claim with photos, claim description, and object type (car / laptop / package).
2. **`agent.py`** resizes and converts images, builds a structured prompt, and calls the Gemini multimodal API.
3. **Gemini returns** a JSON object with claim status, severity, issue type, risk flags, and more.
4. **`validator.py`** validates the response with a Pydantic model.
5. **`app.py`** renders the result with a clean Streamlit dashboard.

---

## 📦 Dependencies

```
streamlit
google-generativeai
pillow
pandas
pydantic
python-dotenv
```

---

## 🔐 Security Note

Never commit your `.env` file or API keys. The `.gitignore` already excludes `.env`.

---

## 📄 License

MIT License – feel free to use and modify.
