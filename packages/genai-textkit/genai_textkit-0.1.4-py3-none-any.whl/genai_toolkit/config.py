# device/model paths configuration


# Language code mapping for NLLB model
LANG_MAP = {
    "en": "eng_Latn",
    "fr": "fra_Latn",
    "hi": "hin_Deva",
    "es": "spa_Latn",
    "ta": "tam_Taml",
    "bn": "ben_Beng",
    "ml": "mal_Mlym",
}

# Model names
MODEL_NAMES = {
    "generator": "distilgpt2",
    "summarizer": "sshleifer/distilbart-cnn-12-6",
    "classifier": "distilbert-base-uncased-finetuned-sst-2-english",
    "translator": "facebook/nllb-200-distilled-600M"
}

# Default parameters
DEFAULTS = {
    "max_tokens": 50
}

# Version info
__version__ = "0.1.0"
