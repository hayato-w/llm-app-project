import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.routers.products import PRODUCT_TOOL_HANDLERS, PRODUCT_TOOLS
from app.schemas.chat import ChatRequest
from app.schemas.product import responseSchema

# 使用するモデルIDの指定 (例: Claude 3.5 Sonnet)
MODEL_ID = "amazon.nova-lite-v1:0"


def _extract_text(message: dict) -> str:
    return "".join(
        block["text"] for block in message.get("content", []) if "text" in block
    )


def bedrock_chat_function(payload: ChatRequest, db: Session) -> responseSchema:
    bedrock_client = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

    # 過去の会話履歴 + 今回のユーザー発言を、Bedrock Converse API形式のmessages配列に組み立てる
    # (content は文字列ではなく、{"text": ...} のブロック配列にする必要がある)
    messages = [
        {"role": m.role, "content": [{"text": m.content}]}
        for m in payload.history
        if m.role in ("user", "assistant")
    ]
    messages.append({"role": "user", "content": [{"text": payload.message}]})

    request_kwargs = {
        "modelId": MODEL_ID,
        "inferenceConfig": {"maxTokens": 500, "temperature": 0.7},
        "toolConfig": {"tools": PRODUCT_TOOLS},
    }

    try:
        completion = bedrock_client.converse(messages=messages, **request_kwargs)
        output_message = completion["output"]["message"]

        # モデルが「関数を呼びたい(tool_use)」と回答した場合のループ。
        # 通常の会話なら stopReason は "end_turn" なので、このブロックは実行されずスキップされる。
        while completion["stopReason"] == "tool_use":
            messages.append(output_message)

            tool_results = []
            for block in output_message["content"]:
                if "toolUse" not in block:
                    continue

                tool_use = block["toolUse"]
                handler = PRODUCT_TOOL_HANDLERS[tool_use["name"]]
                # Converse APIの toolUse.input はすでにパース済みの辞書で渡ってくる
                arguments = tool_use.get("input") or {}
                result = handler(db, **arguments)

                # Bedrock Converse APIの toolResult.content[].json はJSONオブジェクトのみ許可されており、
                # 配列(list)を直接渡すとValidationExceptionになるため、オブジェクトでラップする
                json_content = result if isinstance(result, dict) else {"result": result}

                tool_results.append(
                    {
                        "toolResult": {
                            "toolUseId": tool_use["toolUseId"],
                            "content": [{"json": json_content}],
                        }
                    }
                )

            # Bedrockに"tool" roleは無いので、"user"としてtoolResultを返す
            messages.append({"role": "user", "content": tool_results})

            completion = bedrock_client.converse(messages=messages, **request_kwargs)
            output_message = completion["output"]["message"]

    except ClientError as e:
        raise HTTPException(status_code=502, detail=f"Bedrock APIエラーが発生しました: {e}") from e

    # stopReasonが"end_turn" = モデルが最終的な自然文の回答を返した状態
    return responseSchema(response=_extract_text(output_message))
