import json

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI, OpenAIError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.openai_client import get_openai_client
from app.db.session import get_db
from app.routers.products import PRODUCT_TOOL_HANDLERS, PRODUCT_TOOLS
from app.schemas.chat import ChatRequest
from app.schemas.product import responseSchema

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=responseSchema)
def chat(
    payload: ChatRequest,
    client: OpenAI = Depends(get_openai_client),
    db: Session = Depends(get_db),
) -> responseSchema:
    settings = get_settings()

    # 過去の会話履歴 + 今回のユーザー発言を、OpenAI API形式のメッセージ配列に組み立てる
    messages = [{"role": m.role, "content": m.content} for m in payload.history]
    messages.append({"role": "user", "content": payload.message})

    try:
        # 1回目の呼び出し。tools=PRODUCT_TOOLS を渡すことで
        # 「商品について聞かれたらこの関数を呼んでいい」とモデルに伝える
        completion = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=PRODUCT_TOOLS,
        )
        message = completion.choices[0].message

        # モデルが「関数を呼びたい(tool_calls)」と回答した場合のループ。
        # 通常の会話なら tool_calls は空なので、このブロックは実行されずスキップされる。
        while message.tool_calls:
            # モデル自身の「この関数を呼びたい」という発言も履歴に残す
            # (次にAPIへ送るmessagesにtool_callの文脈を含めるため必須)
            messages.append(message.model_dump(exclude_none=True))

            # モデルは1回の応答で複数の関数呼び出しを要求することがあるため全て処理する
            for tool_call in message.tool_calls:
                # tool_call.function.name (例: "get_products_by_category") から
                # 実行すべきPython関数をPRODUCT_TOOL_HANDLERSで引く
                handler = PRODUCT_TOOL_HANDLERS[tool_call.function.name]
                # モデルが指定してきた引数はJSON文字列で来るのでパースする
                arguments = json.loads(tool_call.function.arguments or "{}")
                # 実際にDBへ問い合わせて結果を取得する
                result = handler(db, **arguments)
                # 関数の実行結果を role="tool" としてmessagesに追加し、
                # どの tool_call に対する結果かを tool_call_id で紐付ける
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )

            # 関数の実行結果を踏まえて、モデルに再度回答を作らせる。
            # ここでまた tool_calls が返ってくる可能性があるので while で繰り返す。
            completion = client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                tools=PRODUCT_TOOLS,
            )
            message = completion.choices[0].message
    except OpenAIError as exc:
        # OpenAI API側のエラー(認証切れ・レート制限等)は502として呼び出し元に返す
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    # tool_callsが無くなった = モデルが最終的な自然文の回答を返した状態
    # これをresponseSchema(response: str)に詰めて返却する
    return responseSchema(response=message.content or "")
