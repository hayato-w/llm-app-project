# llm-web-api

FastAPI テンプレートプロジェクト。

## セットアップ

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

`.env.example` を `.env` にコピーし、`DATABASE_URL`(PostgreSQL接続先) を必要に応じて設定してください。

PostgreSQLはDocker Composeで起動できます。

```bash
docker compose up -d
```

`products` テーブルはアプリ起動時に自動作成されます。

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
  db/base.py            SQLAlchemy Base
  db/session.py         DBエンジン・セッション (get_db)
  models/                SQLAlchemyモデル (DBテーブル定義)
  routers/               エンドポイント定義
  schemas/               Pydanticモデル
tests/                   テストコード
```
