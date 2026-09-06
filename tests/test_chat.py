from fastapi.testclient import TestClient

from app.core.openai_client import get_openai_client
from app.main import app

client = TestClient(app)


class _FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = _FakeMessage(content)


class _FakeCompletion:
    def __init__(self, content: str) -> None:
        self.choices = [_FakeChoice(content)]


class _FakeCompletions:
    def __init__(self, content: str) -> None:
        self._content = content
        self.last_kwargs: dict | None = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return _FakeCompletion(self._content)


class _FakeChat:
    def __init__(self, content: str) -> None:
        self.completions = _FakeCompletions(content)


class _FakeOpenAIClient:
    def __init__(self, content: str = "hello!") -> None:
        self.chat = _FakeChat(content)


def test_chat_returns_reply():
    fake_client = _FakeOpenAIClient(content="hello!")
    app.dependency_overrides[get_openai_client] = lambda: fake_client
    try:
        response = client.post("/chat", json={"message": "hi"})
    finally:
        app.dependency_overrides.pop(get_openai_client, None)

    assert response.status_code == 200
    assert response.json() == {"reply": "hello!"}

    sent_messages = fake_client.chat.completions.last_kwargs["messages"]
    assert sent_messages == [{"role": "user", "content": "hi"}]


def test_chat_includes_history():
    fake_client = _FakeOpenAIClient(content="ok")
    app.dependency_overrides[get_openai_client] = lambda: fake_client
    try:
        response = client.post(
            "/chat",
            json={
                "message": "and then?",
                "history": [
                    {"role": "user", "content": "hi"},
                    {"role": "assistant", "content": "hello"},
                ],
            },
        )
    finally:
        app.dependency_overrides.pop(get_openai_client, None)

    assert response.status_code == 200
    sent_messages = fake_client.chat.completions.last_kwargs["messages"]
    assert sent_messages == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
        {"role": "user", "content": "and then?"},
    ]
