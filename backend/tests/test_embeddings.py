import importlib
import sys
import types

from app.services import embeddings


def test_get_model_loads_once(monkeypatch):
    created = []

    class FakeSentenceTransformer:
        def __init__(self, model_name):
            created.append(model_name)

        def encode(self, text):
            return FakeVector([0.1, 0.2])

    class FakeVector(list):
        def tolist(self):
            return list(self)

    fake_module = types.SimpleNamespace(
        SentenceTransformer=FakeSentenceTransformer
    )

    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_module)
    embeddings.get_model.cache_clear()

    first = embeddings.get_model()
    second = embeddings.get_model()

    assert first is second
    assert created == [embeddings.MODEL_NAME]

    embeddings.get_model.cache_clear()


def test_generate_embedding_uses_cached_model(monkeypatch):
    class FakeModel:
        def encode(self, text):
            assert text == "hello"
            return FakeVector([0.3, 0.4])

    class FakeVector(list):
        def tolist(self):
            return list(self)

    monkeypatch.setattr(embeddings, "get_model", lambda: FakeModel())

    assert embeddings.generate_embedding("hello") == [0.3, 0.4]
