from .text import generate, classify, summarize, translate

__all__ = ["generate", "summarize", "classify", "translate"]

try:
    import torch
except ImportError:
    raise ImportError(
        "⚠️ GenAI Toolkit requires PyTorch. Please install it manually:\n"
        "pip install torch --index-url https://download.pytorch.org/whl/cpu"
    )