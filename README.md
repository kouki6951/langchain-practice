# README

## プロジェクト概要
生成AI技術の習得を目的として、[OpenAI Platform](https://platform.openai.com/docs/guides/text-generation)に記載されているサンプルプログラムを実行できる環境を構築し、OpenAI SDKやLangChainを実際に動かせる環境を整えることが目的である。

## 環境構築手順

### 前提条件
- Dockerがインストールされていること

### .envファイルの作成
.envファイルを作成し、以下のようにopenAIのシークレットキーを記載する。
```
OPENAI_API_KEY=(your-secret-key)
```

### Dockerイメージのビルド
```
docker-compose build
```

### コンテナ起動
```
docker-compose up
```

## ファイル構造
コンテナ内は以下のようなファイル構造をしている。
```
/app/
├── docker-compose.yml  # Docker Compose 設定ファイル
├── .env                # 環境変数設定ファイル
├── src/                # アプリケーションのソースコード
│   ├── 00.py           # 環境変数確認用コード
│   ├── 01.py           # Build a simple LLM application with chat models and prompt templates Using Language Models
│   └── 02.py           # Build a simple LLM application with chat models and prompt templates Prompt Templates
├── Dockerfile          # アプリケーション用 Dockerfile
├── requirements.txt    # Python依存パッケージ定義ファイル
└── README.md
```

## プログラム実行方法
各プログラムはsrcディレクトリに格納されてるので、以下のように個別に実行することができる。
```
python 00.py
```