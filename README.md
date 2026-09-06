# llm-web-api

FastAPI テンプレートプロジェクト。

## セットアップ

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

`.env.example` を `.env` にコピーし、`OPENAI_API_KEY` に自分のキーを設定してください。

## 起動

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

## テスト

```bash
pytest
```

## 構成

```
app/
  main.py               アプリのエントリポイント
  core/config.py        設定 (環境変数)
  core/openai_client.py OpenAIクライアント取得
  routers/               エンドポイント定義
  schemas/               Pydanticモデル
tests/                   テストコード
```
