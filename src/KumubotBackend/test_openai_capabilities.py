import base64
import importlib.util
import io
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")

BACKEND_PATH = Path(__file__).with_name("backend.py")
BACKEND_SPEC = importlib.util.spec_from_file_location("kumubot_backend_under_test", BACKEND_PATH)
backend = importlib.util.module_from_spec(BACKEND_SPEC)
assert BACKEND_SPEC.loader is not None
BACKEND_SPEC.loader.exec_module(backend)


class FakeUsage:
    def __init__(self, prompt_tokens=0, completion_tokens=0, total_tokens=None):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens if total_tokens is not None else prompt_tokens + completion_tokens


class FakeResponse:
    def __init__(self, *, output_text="", usage=None, output=None, response_id="resp_test", payload=None):
        self.output_text = output_text
        self.usage = usage or FakeUsage()
        self.output = output or []
        self.id = response_id
        self._payload = payload or {"output": []}

    def model_dump(self):
        return self._payload


class FakeStreamingSpeechResponse:
    def __init__(self, audio_bytes):
        self.audio_bytes = audio_bytes

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def stream_to_file(self, path):
        Path(path).write_bytes(self.audio_bytes)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(backend, "log_api_usage", lambda *args, **kwargs: None)
    backend.app.testing = True
    return backend.app.test_client()


def test_openai_capabilities_lists_inventory(client):
    response = client.get("/openai/capabilities")

    assert response.status_code == 200
    payload = response.get_json()
    assert "openai_capability_endpoints" in payload
    assert any(item["route"] == "/openai/agent" for item in payload["openai_capability_endpoints"])
    assert any(item["product"] == "KumuChat" for item in payload["existing_product_endpoints"])


def test_openai_agent_runs_function_call_loop(client, monkeypatch):
    queued_responses = [
        FakeResponse(
            output=[
                SimpleNamespace(
                    type="function_call",
                    name="get_openai_capability_inventory",
                    arguments=json.dumps({"section": "new"}),
                    call_id="call_1",
                )
            ],
            usage=FakeUsage(12, 4),
            response_id="resp_1",
        ),
        FakeResponse(
            output_text="Lead with the agent, web search, and hosted retrieval endpoints.",
            output=[],
            usage=FakeUsage(8, 16),
            response_id="resp_2",
        ),
    ]
    captured_calls = []

    def fake_create(**kwargs):
        captured_calls.append(kwargs)
        return queued_responses.pop(0)

    monkeypatch.setattr(
        backend,
        "openai_client",
        SimpleNamespace(responses=SimpleNamespace(create=fake_create)),
    )

    response = client.post("/openai/agent", json={"prompt": "How should I position these capabilities for a cohort application?"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["answer"].startswith("Lead with the agent")
    assert payload["tool_trace"][0]["tool"] == "get_openai_capability_inventory"
    assert payload["usage"]["total_tokens"] == 40
    assert payload["model"] == backend.DEFAULT_CHAT_MODEL
    assert payload["reasoning_effort"] == backend.DEFAULT_CHAT_REASONING_EFFORT
    assert len(captured_calls) == 2
    assert captured_calls[0]["model"] == backend.DEFAULT_CHAT_MODEL
    assert captured_calls[0]["reasoning"] == {"effort": backend.DEFAULT_CHAT_REASONING_EFFORT}


def test_openai_web_search_returns_citations(client, monkeypatch):
    captured_calls = []
    search_payload = {
        "output": [
            {
                "type": "web_search_call",
                "action": {
                    "type": "search",
                    "queries": ["ChatGPT 26 cohort"],
                    "sources": [{"title": "OpenAI", "url": "https://openai.com"}],
                },
            },
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": "Here is the result.",
                        "annotations": [
                            {
                                "type": "url_citation",
                                "title": "OpenAI",
                                "url": "https://openai.com",
                            }
                        ],
                    }
                ],
            },
        ]
    }

    monkeypatch.setattr(
        backend,
        "openai_client",
        SimpleNamespace(
            responses=SimpleNamespace(
                create=lambda **kwargs: captured_calls.append(kwargs) or FakeResponse(
                    output_text="Here is the result.",
                    usage=FakeUsage(14, 11),
                    payload=search_payload,
                )
            )
        ),
    )

    response = client.post(
        "/openai/web-search",
        json={"query": "Find public details about the ChatGPT 26 cohort", "allowed_domains": ["openai.com"]},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["citations"] == [{"title": "OpenAI", "url": "https://openai.com"}]
    assert payload["search_actions"][0]["queries"] == ["ChatGPT 26 cohort"]
    assert payload["model"] == backend.DEFAULT_CHAT_MODEL
    assert payload["reasoning_effort"] == backend.DEFAULT_CHAT_REASONING_EFFORT
    assert captured_calls[0]["model"] == backend.DEFAULT_CHAT_MODEL
    assert captured_calls[0]["reasoning"] == {"effort": backend.DEFAULT_CHAT_REASONING_EFFORT}


def test_openai_rag_index_creates_vector_store_and_uploads_files(client, monkeypatch):
    uploaded = []

    def fake_upload_and_poll(**kwargs):
        uploaded.append(kwargs["vector_store_id"])
        return SimpleNamespace(model_dump=lambda: {"id": f"file_{len(uploaded)}", "status": "completed"})

    fake_openai_client = SimpleNamespace(
        vector_stores=SimpleNamespace(
            create=lambda **kwargs: SimpleNamespace(id="vs_123"),
            files=SimpleNamespace(upload_and_poll=fake_upload_and_poll),
        )
    )
    monkeypatch.setattr(backend, "openai_client", fake_openai_client)

    response = client.post(
        "/openai/rag/index",
        json={
            "name": "Kumu Docs",
            "documents": [
                {"filename": "overview.txt", "text": "KumuBot uses OpenAI across multiple endpoints."},
                "A second document about Hawaiian language workflows.",
            ],
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["vector_store_id"] == "vs_123"
    assert len(payload["uploaded_files"]) == 2
    assert uploaded == ["vs_123", "vs_123"]


def test_openai_rag_query_returns_results_and_citations(client, monkeypatch):
    captured_calls = []
    rag_payload = {
        "output": [
            {
                "type": "file_search_call",
                "results": [
                    {"file_id": "file_1", "filename": "overview.txt", "score": 0.98},
                ],
            },
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": "KumuBot uses OpenAI heavily.",
                        "annotations": [
                            {
                                "type": "file_citation",
                                "file_id": "file_1",
                                "filename": "overview.txt",
                            }
                        ],
                    }
                ],
            },
        ]
    }

    monkeypatch.setattr(
        backend,
        "openai_client",
        SimpleNamespace(
            responses=SimpleNamespace(
                create=lambda **kwargs: captured_calls.append(kwargs) or FakeResponse(
                    output_text="KumuBot uses OpenAI heavily.",
                    usage=FakeUsage(18, 9),
                    payload=rag_payload,
                )
            )
        ),
    )

    response = client.post(
        "/openai/rag/query",
        json={"vector_store_id": "vs_123", "question": "How does KumuBot use OpenAI?"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["answer"] == "KumuBot uses OpenAI heavily."
    assert payload["citations"] == [{"file_id": "file_1", "filename": "overview.txt"}]
    assert payload["results"][0]["score"] == 0.98
    assert payload["model"] == backend.DEFAULT_CHAT_MODEL
    assert payload["reasoning_effort"] == backend.DEFAULT_CHAT_REASONING_EFFORT
    assert captured_calls[0]["model"] == backend.DEFAULT_CHAT_MODEL
    assert captured_calls[0]["reasoning"] == {"effort": backend.DEFAULT_CHAT_REASONING_EFFORT}


def test_chat_route_uses_gpt_5_4_mini_defaults(client, monkeypatch):
    captured_calls = []

    def fake_create(**kwargs):
        captured_calls.append(kwargs)
        return FakeResponse(output_text="Aloha", usage=FakeUsage(7, 5))

    monkeypatch.setattr(
        backend,
        "openai_client",
        SimpleNamespace(responses=SimpleNamespace(create=fake_create)),
    )

    response = client.post("/chat", json={"history": [], "hawaiian_output": False, "message": "Tell me about Hawaii."})

    assert response.status_code == 200
    assert response.get_json() == {"message": "Aloha"}
    assert captured_calls[0]["model"] == backend.DEFAULT_CHAT_MODEL
    assert captured_calls[0]["reasoning"] == {"effort": backend.DEFAULT_CHAT_REASONING_EFFORT}


def test_art_route_uses_gpt_image_1_5_and_chat_defaults(client, monkeypatch):
    image_calls = []
    response_calls = []

    def fake_generate(**kwargs):
        image_calls.append(kwargs)
        return SimpleNamespace(data=[SimpleNamespace(b64_json=base64.b64encode(b"fake-webp").decode("ascii"))])

    def fake_create(**kwargs):
        response_calls.append(kwargs)
        return FakeResponse(output_text="Fun fact", usage=FakeUsage(4, 6))

    monkeypatch.setattr(
        backend,
        "openai_client",
        SimpleNamespace(
            images=SimpleNamespace(generate=fake_generate),
            responses=SimpleNamespace(create=fake_create),
        ),
    )

    response = client.post("/art", json={"description": "a canoe on Waikiki beach"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["fun_fact"] == "Fun fact"
    assert payload["image_url"].startswith("data:image/webp;base64,")
    assert image_calls[0]["model"] == backend.DEFAULT_IMAGE_MODEL
    assert image_calls[0]["quality"] == backend.DEFAULT_IMAGE_QUALITY
    assert response_calls[0]["model"] == backend.DEFAULT_CHAT_MODEL
    assert response_calls[0]["reasoning"] == {"effort": backend.DEFAULT_CHAT_REASONING_EFFORT}


def test_openai_voice_speech_returns_base64_audio(client, monkeypatch):
    audio_bytes = b"fake-mp3-audio"

    def fake_create(**kwargs):
        return FakeStreamingSpeechResponse(audio_bytes)

    fake_openai_client = SimpleNamespace(
        audio=SimpleNamespace(
            speech=SimpleNamespace(
                with_streaming_response=SimpleNamespace(create=fake_create)
            )
        )
    )
    monkeypatch.setattr(backend, "openai_client", fake_openai_client)

    response = client.post("/openai/voice/speech", json={"text": "Aloha from KumuBot"})

    assert response.status_code == 200
    payload = response.get_json()
    assert base64.b64decode(payload["audio_base64"]) == audio_bytes
    assert payload["mime_type"] == "audio/mp3"


def test_openai_voice_transcribe_returns_text(client, monkeypatch):
    transcript = SimpleNamespace(
        text="Aloha kakahiaka",
        model_dump=lambda: {"text": "Aloha kakahiaka", "language": "haw"},
    )
    fake_openai_client = SimpleNamespace(
        audio=SimpleNamespace(
            transcriptions=SimpleNamespace(create=lambda **kwargs: transcript)
        )
    )
    monkeypatch.setattr(backend, "openai_client", fake_openai_client)

    response = client.post(
        "/openai/voice/transcribe",
        data={"audio": (io.BytesIO(b"audio-bytes"), "sample.wav")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["text"] == "Aloha kakahiaka"
    assert payload["raw"]["language"] == "haw"


def test_openai_structured_plan_returns_json_schema_output(client, monkeypatch):
    plan = {
        "headline": "KumuBot is an OpenAI-heavy cultural platform",
        "why_it_is_distinct": "It combines agentic tools, retrieval, image generation, and voice in one backend.",
        "feature_sequence": [
            {
                "step": "Start with the agent",
                "endpoint": "/openai/agent",
                "why_it_matters": "Shows custom tool calling.",
            }
        ],
        "resume_bullet": "Built a multi-endpoint OpenAI application for Hawaiian language workflows.",
        "application_pitch": "I use OpenAI products across real product surfaces, not isolated experiments.",
    }

    monkeypatch.setattr(
        backend,
        "openai_client",
        SimpleNamespace(
            responses=SimpleNamespace(
                create=lambda **kwargs: FakeResponse(
                    output_text=json.dumps(plan),
                    usage=FakeUsage(20, 13),
                )
            )
        ),
    )

    response = client.post("/openai/structured-plan", json={"goal": "Strengthen my cohort application"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["plan"]["headline"] == plan["headline"]
    assert payload["plan"]["feature_sequence"][0]["endpoint"] == "/openai/agent"


@pytest.mark.parametrize(
    ("route", "payload"),
    [
        ("/openai/agent", {}),
        ("/openai/web-search", {}),
        ("/openai/rag/index", {}),
        ("/openai/rag/query", {"question": "missing store"}),
        ("/openai/structured-plan", {}),
    ],
)
def test_openai_json_routes_validate_required_inputs(client, route, payload):
    response = client.post(route, json=payload)

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_openai_voice_transcribe_requires_audio_file(client):
    response = client.post("/openai/voice/transcribe", data={}, content_type="multipart/form-data")

    assert response.status_code == 400
    assert "error" in response.get_json()
