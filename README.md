# 🎓 Smart Educational Quiz Generator (AI Quiz Bot)

An interactive Streamlit application that turns plain-text lecture notes into an AI-generated multiple-choice question. It uses the Groq API and an open-source large language model (LLM) to return structured quiz data.

## ✨ Features

- Upload a `.txt` lecture or study-notes file from the browser.
- Generate a multiple-choice question from the uploaded content.
- Receive a predictable JSON response containing the question, four answer options, and the correct answer.
- See clear in-app feedback for missing API keys and request failures.
- Keep API keys out of the repository through `.gitignore`.

## 🛠️ Tech stack

- [Streamlit](https://streamlit.io/) for the web interface
- [Groq Python SDK](https://github.com/groq/groq-python) for AI inference
- `llama-3.3-70b-versatile` as the question-generation model
- Python 3.10+

## 🚀 Run locally

### 1. Clone the repository

```bash
git clone https://github.com/Whiteghost0859/ai-quiz-bot.git
cd ai-quiz-bot
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your Groq API key

Create an API key in the [Groq Console](https://console.groq.com/keys), then set it in your terminal. Do not place the key in source code or commit it to Git.

Windows PowerShell:

```powershell
$env:GROQ_API_KEY = "your_groq_api_key"
```

macOS or Linux:

```bash
export GROQ_API_KEY="your_groq_api_key"
```

### 5. Start the app

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit, upload a `.txt` file, and select **Generate Question Test**.

## 📦 Expected quiz format

The model is asked to return a JSON object in this shape:

```json
{
  "question": "What is the SI unit of force?",
  "options": {
    "A": "Joule",
    "B": "Newton",
    "C": "Watt",
    "D": "Pascal"
  },
  "answer": "B"
}
```

## Troubleshooting

| Issue | What to check |
| --- | --- |
| `GROQ_API_KEY environment variable is missing` | Set `GROQ_API_KEY` in the same terminal before running Streamlit. |
| `APIConnectionError` | Confirm internet access, then restart Streamlit. Ensure the key contains no accidental spaces or line breaks. |
| `ModuleNotFoundError: groq` | Run `pip install -r requirements.txt` in the active virtual environment. |

## Roadmap

- Generate several questions from different sections of a lecture
- Add answer selection and live quiz grading
- Save quiz results between sessions
- Support additional document formats

## License

This project is intended for educational use. Add a license file before distributing it publicly.
