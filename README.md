# 🤖 HireBot — AI Resume Screener

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://khushirajput123-hirebot-appmain.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-orange?logo=google)
![LangChain](https://img.shields.io/badge/LangChain-Enabled-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> An end-to-end GenAI application that analyses resumes against job descriptions using Google Gemini API — giving candidates instant match scores, ATS feedback, skill gap analysis, interview preparation, and resume improvement suggestions.

---

## 🚀 Live Demo

🔗 **[Try HireBot Live →](https://khushirajput123-hirebot-appmain.streamlit.app)**

Upload your resume PDF + paste any job description → get AI-powered analysis in seconds.

---

## 📸 Features

| Feature | Description |
|---|---|
| 🎯 Match Score | AI scores your resume fit for the JD (0–100) |
| 🤖 ATS Score | Checks how well your resume passes ATS software |
| 🛠️ Skills Analysis | Visual chart of matched vs missing skills |
| 🗺️ Learning Roadmap | Personalized plan to learn missing skills with free resources |
| 🎯 Interview Questions | 8 personalized technical + HR questions based on your resume |
| 🤖 Model Answers | AI-generated complete answers for each interview question |
| ✏️ Bullet Rewriter | Rewrites weak resume bullets into strong, impactful lines |
| 📊 History Dashboard | Track your score improvement over time |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Google Gemini 2.5 Flash API |
| **PDF Processing** | PyMuPDF (fitz) |
| **Frontend** | Streamlit |
| **Data Visualization** | Plotly |
| **Database** | SQLite |
| **Environment** | Python-dotenv |
| **Language** | Python 3.10+ |

---

## 📁 Project Structure

```
hirebots/
├── app/
│   └── main.py              # Streamlit UI — all 4 tabs
├── utils/
│   ├── pdf_reader.py        # PDF text extraction using PyMuPDF
│   ├── scorer.py            # Gemini API calls + prompt templates
│   └── database.py          # SQLite storage for analysis history
├── data/
│   └── results.db           # Auto-generated on first run
├── .env                     # API keys (not pushed to GitHub)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ How It Works

```
User uploads Resume PDF + pastes Job Description
              ↓
PyMuPDF extracts text from PDF
              ↓
LangChain structures the prompt
              ↓
Gemini 2.5 Flash analyses both texts
              ↓
Returns JSON: Score + Skills + ATS + Roadmap
              ↓
SQLite saves the result
              ↓
Streamlit displays interactive dashboard
```

---

## 🏃 Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/Khushirajput123/hirebots.git
cd hirebots
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up API key
Create a `.env` file in root folder:
```
GEMINI_API_KEY=your_gemini_api_key_here
```
Get your free API key at [aistudio.google.com](https://aistudio.google.com)

### 5. Run the app
```bash
streamlit run app/main.py
```

Open **http://localhost:8501** in your browser.

---

## 📊 App Walkthrough

### Tab 1 — Analyse Resume
- Upload your PDF resume
- Paste any job description from Naukri/LinkedIn
- Click **Analyse** → get match score, ATS score, skills chart, and learning roadmap

### Tab 2 — Interview Prep
- After analysis, generate 8 personalized interview questions
- Click **Generate Model Answer** on any question
- Get complete answer + delivery tips + follow-up question

### Tab 3 — Bullet Rewriter
- Paste any weak resume bullet point
- Get 3 stronger AI-rewritten versions with action verbs and quantified impact

### Tab 4 — History
- View all past analyses
- Track score improvement over time with trend chart

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key from AI Studio |

For Streamlit Cloud deployment, add this under **Settings → Secrets**.

---

## 📦 Requirements

```
google-genai
pymupdf
streamlit
python-dotenv
pandas
plotly
```

---

## 🚀 Deploy on Streamlit Cloud

1. Fork this repository
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your GitHub repo
4. Set main file: `app/main.py`
5. Add secret: `GEMINI_API_KEY = "your_key"`
6. Click Deploy

---

## 👩‍💻 Author

**Khushi Rajput**


[![GitHub](https://img.shields.io/badge/GitHub-Khushirajput123-black?logo=github)](https://github.com/Khushirajput123)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://linkedin.com/in/khushirajput)
[![LeetCode](https://img.shields.io/badge/LeetCode-1600%2B_Rating-orange?logo=leetcode)](https://leetcode.com/khushirajput)

---

## 📄 License

This project is licensed under the MIT License — feel free to use and modify.

