
# 🧠 GenAI-Toolkit

A minimal, CPU-friendly, no-API-key-required **LLM-powered Python library** — for text generation, summarization, sentiment classification, and translation.

> ⚡ Just `pip install genai_toolkit` and you're ready to build with GenAI-Toolkit on any machine.

---

## 🚀 Features

- ✅ Offline text generation with `distilgpt2`
- ✅ Fast summarization with `distilbart-cnn-12-6`
- ✅ Sentiment classification using `distilbert-sst2`
- ✅ Multilingual translation via `facebook/nllb-200-distilled-600M`
- ✅ Works on **CPU** — no GPU required
- ✅ No API keys, no internet after install

---

## 📦 Installation


# Step 1: Install GenAI-Toolkit
pip install genai_toolkit
# Step 2: (If not already installed) Install PyTorch manually
pip install torch --index-url https://download.pytorch.org/whl/cpu
```


Author: Abhinav | GitHub: [IamAbhinav01](https://github.com/IamAbhinav01)
Repository: [IamAbhinav01/GenAI](https://github.com/IamAbhinav01/GenAI)

---

## 🚀 Features

- ✅ Offline text generation with `distilgpt2`
- ✅ Fast summarization with `distilbart-cnn-12-6`
- ✅ Sentiment classification using `distilbert-sst2`
- ✅ Multilingual translation via `facebook/nllb-200-distilled-600M`
- ✅ Works on **CPU** — no GPU required
- ✅ No API keys, no internet after install

---

## 📦 Installation

```bash
pip install genai_toolkit
```

---

## 🏁 Quick Start

```python

from genai_toolkit import generate, summarize, classify, translate

# Text generation
print(generate("Write a poem about the moon", max_tokens=50))

# Summarization
print(summarize("Your long text here..."))

# Sentiment Classification
print(classify("I really loved the product!"))

# Translation (English to Hindi)
print(translate("I am happy to meet you", to_lang="hi"))
```

---

## 🌍 Supported Translation Languages

| Code | Language   |
|------|------------|
| en   | English    |
| hi   | Hindi      |
| ta   | Tamil      |
| ml   | Malayalam  |
| fr   | French     |
| es   | Spanish    |
| bn   | Bengali    |

---

## 📂 Project Structure

```
genai-toolkit/
│
├── genai/                # Core package
│   ├── __init__.py       # Public API
│   ├── text.py           # generate, summarize, classify, translate
│   ├── config.py         # Device/model paths
│   └── download_models.py# Download models utility
│
├── examples/             # Usage examples
│   ├── example_generate.py
│   ├── example_summarize.py
│   ├── example_translate.py
│   └── example_classify.py
│
├── tests/                # Unit tests
│   └── test_text.py
│
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project metadata
├── README.md             # Project documentation
└── ...                   # Other files
```

---

## 🧪 Run Examples

See the `examples/` folder for ready-to-run scripts.

## 🤝 Contributing

Pull requests and issues are welcome! Please open an issue or PR on [GitHub](https://github.com/IamAbhinav01/GenAI).

## 📄 License

MIT License © Abhinav


