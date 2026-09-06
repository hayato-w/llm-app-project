from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI, OpenAIError

from app.core.config import get_settings
from app.core.openai_client import get_openai_client
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    client: OpenAI = Depends(get_openai_client),
) -> ChatResponse:
    settings = get_settings()

    messages = [{"role": m.role, "content": m.content} for m in payload.history]
    messages.append({"role": "user", "content": payload.message})

    try:
        completion = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
        )
    except OpenAIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return ChatResponse(reply=completion.choices[0].message.content or "")
