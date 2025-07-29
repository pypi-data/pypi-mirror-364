from genai_toolkit.config import LANG_MAP, MODEL_NAMES, DEFAULTS
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from functools import lru_cache

# Generator: distilgpt2
@lru_cache(maxsize=None)
def _get_generator():
    return pipeline("text-generation", model=MODEL_NAMES["generator"])

# Summarizer: distilbart-cnn
@lru_cache(maxsize=None)
def _get_summarizer():
    return pipeline("summarization", model=MODEL_NAMES["summarizer"])

# Sentiment Classifier: distilbert-sst2
@lru_cache(maxsize=None)
def _get_classifier():
    return pipeline("sentiment-analysis", model=MODEL_NAMES["classifier"])

# Translator: facebook/nllb-200-distilled-600M
@lru_cache(maxsize=None)
def _get_translator_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAMES["translator"])
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAMES["translator"])
    return tokenizer, model

# Exposed functions

def generate(prompt: str, max_words: int = 100) -> str:
    model = _get_generator()
    result = model(prompt, max_new_tokens=150)[0]["generated_text"]
    words = result.split()
    trimmed = " ".join(words[:max_words])
    return trimmed

def summarize(text: str) -> str:
    return _get_summarizer()(text)[0]["summary_text"]

def classify(text: str) -> str:
    return _get_classifier()(text)[0]["label"]

def translate(text: str, to_lang: str = "hi", from_lang: str = "en") -> str:
    tokenizer, model = _get_translator_model()
    src = LANG_MAP.get(from_lang, from_lang)
    tgt = LANG_MAP.get(to_lang, to_lang)

    translator = pipeline(
        "translation",
        model=model,
        tokenizer=tokenizer,
        src_lang=src,
        tgt_lang=tgt
    )
    return translator(text)[0]["translation_text"]