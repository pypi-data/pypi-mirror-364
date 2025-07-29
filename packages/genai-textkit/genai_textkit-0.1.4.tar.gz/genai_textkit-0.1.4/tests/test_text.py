from genai import generate, summarize, classify, translate

def test_generate():
    result = generate("Testing model", max_tokens=10)
    assert isinstance(result, str)
    assert len(result) > 0

def test_summarize():
    result = summarize("Artificial intelligence is transforming industries.")
    assert isinstance(result, str)
    assert len(result) > 0

def test_classify():
    result = classify("I hate bugs")
    assert result in ["POSITIVE", "NEGATIVE"]

def test_translate():
    result = translate("Hello", from_lang="en", to_lang="hi")
    assert isinstance(result, str)
    assert len(result) > 0
