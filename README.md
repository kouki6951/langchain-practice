# README

## プロジェクト概要
生成AI技術の習得を目的として、[LangCahin公式サイト](https://python.langchain.com/docs/introduction/)に記載されているサンプルプログラムを実行できる環境を構築し、OpenAI SDKやLangChainを実際に動かせる環境を整えることが目的である。

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
|   ├ LangChain/
    │   ├── test.py     # LangSmith疎通確認用コード
    │   ├── 00.py       # 環境変数確認用コード
    │   ├── 01.py       # Build a simple LLM application with chat models and prompt templates - Using Language Models
    │   ├── 02.py       # Build a simple LLM application with chat models and prompt templates - Prompt Templates~
    │   ├── 03.py       # Build a Simple LLM Application with LCEL - Using Language Models    
    │   ├── 04.py       # Build a Simple LLM Application with LCEL - OutputParsers    
    │   ├── 05.py       # Build a Simple LLM Application with LCEL - Prompt Templates    
    │   ├── 06.py       # Build a Simple LLM Application with LCEL - Chaining together components with LCEL
    │   ├── 07.py       # How to use chat models to call tools
    │   ├── serve.py    # Build a Simple LLM Application with LCEL - Serving with LangServe  ☆詳細は後述
    │   └── client.py   # Build a Simple LLM Application with LCEL - Serving with LangServe  ☆詳細は後述     
    └ LangGraph/
        ├── part1.py    # LangGraph Quickstart - Part 1: Build a Basic Chatbot
        ├── part2.py    # LangGraph Quickstart - Part 2: Enhancing the Chatbot with Tools
        ├── part3.py    # LangGraph Quickstart - Part 3: Adding Memory to the Chatbot
        ├── part4.py    # LangGraph Quickstart - Part 4: Human-in-the-loop
        ├── part5.py    # LangGraph Quickstart - Part 5: Customizing State

├── Dockerfile          # アプリケーション用 Dockerfile
├── requirements.txt    # Python依存パッケージ定義ファイル
└── README.md
```

## プログラム実行方法
各プログラムはsrcディレクトリに格納されてるので、以下のように個別に実行することができる。
```
python 00.py
```

## LangSmith設定

### LangSmithとは
LangSmithとはLangChainの開発チームが提供するツールで、生成AIを使用したアプリケーションのトラッキングとデバッグを支援するためのプラットフォームのことである。LangSmithを利用することで、AIモデルの入出力・プロンプトのパフォーマンス・エラーの発生状況などを追跡・可視化することができる。

![](./image/01.png)

### LangSmith設定手順

#### 1. LangSmithアカウント作成
[公式サイト](https://www.langchain.com/langsmith)でアカウントを作成する。

#### 2. プロジェクト作成
ログイン後のダッシュボード画面の左または画面中央あたりに表示されている「TracingProject」を押下し、遷移した画面で「New Project」を押下する。

![](./image/02.png)

![](./image/03.png)

#### 3. API Keyの生成
「Generate API Key」を押下するとAPI Keyが表示されるので控えておく。

![](./image/04.png)

#### 4. Project Nameの設定
「Project Name」入力フォームに任意のプロジェクト名を設定する。

![](./image/05.png)

#### 5. 環境変数の設定
表示されている環境変数を.envファイルに追記する

![](./image/06.png)


.env
```
OPENAI_API_KEY=<your_openai_api_key>
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=<your_longsmith_api_key>
LANGSMITH_PROJECT=<your_project_name>
```

#### 6. コンテナ再ビルド(既にコンテナをビルドしている場合)

イメージビルド
```
docker-compose build
```

コンテナ起動
```
docker-compose up
```

#### 7. 疎通確認コードを実行する
/app/src/test.pyを実行し、実行内容がLangSmithに表示されるかを確認する。

```
python /app/src/test.py
```

正常に設定が完了すると以下のように表示される

![](./image/07.png)

## Build a Simple LLM Application with LCELのServing with LangServe
本章ではLCELで構築したLLMアプリケーションをLangServeを用いてLangChainチェーンをREST APIとして展開し、実際にそのAPIにアクセスしてレスポンスを取得する。

### serve.py
LLMアプリケーション本体。localhost:8001で公開される。

### client.py
LLMアプリケーションにアクセスするためのクライアント。

### 実行手順

#### 1. 稼働しているDockerにSSH接続したターミナルを２つ用意する
![](./image/08.png)

#### 2. 片方のターミナルで以下のコマンドを実行する

```
python /app/src/serve.py
```

LangServeが正常に立ち上がると以下のような表示になる(左のターミナルで実行)
![](./image/09.png)

### 3. もう片方のターミナルで以下のコマンドを実行する

```
python /app/src/client.py
```

clientが正常に実行されるとLLMからのレスポンスがターミナルに表示される
![](./image/10.png)
