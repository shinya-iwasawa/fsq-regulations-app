# translate_ja_en.py
from transformers import MarianMTModel, MarianTokenizer

MODEL_NAME = "Helsinki-NLP/opus-mt-ja-en"

_tokenizer = None
_model = None

def load_model():
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        _tokenizer = MarianTokenizer.from_pretrained(MODEL_NAME)
        _model = MarianMTModel.from_pretrained(MODEL_NAME)

def translate_ja_to_en(text: str) -> str:
    load_model()

    inputs = _tokenizer(text, return_tensors="pt", padding=True)
    translated = _model.generate(**inputs, max_length=64)
    en_text = _tokenizer.decode(translated[0], skip_special_tokens=True)

    return en_text.lower()
