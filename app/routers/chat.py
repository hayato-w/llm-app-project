import json

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI, OpenAIError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chat import ChatRequest
from app.schemas.product import responseSchema
from app.server.service_bedrock import bedrock_chat_function

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=responseSchema)
def chat_bedrock(
    payload: ChatRequest,
    db: Session = Depends(get_db),
) -> responseSchema:
    return bedrock_chat_function(payload, db)
