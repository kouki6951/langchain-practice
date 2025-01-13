######################################################################
# Build a Simple LLM Application with LCEL
# https://python.langchain.com/v0.2/docs/tutorials/llm_chain/
#
# Using Language Models
# 注意) 01.pyと同じ内容です
######################################################################

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

######################################################################
# 言語モデルの選択
# Open AIの場合は以下から選択
# - gpt-4o
# - gpt-4o-mini (安いので試すのにおすすめ)
# その他モデルについては公式サイト参照
# https://platform.openai.com/docs/models
######################################################################
model = ChatOpenAI(model="gpt-4o-mini")

######################################################################
# AIモデルに送信するメッセージの定義
# - HumanMessage
#   ユーザーが送信するメッセージを定義するためのインタフェース
#   質問やリクエストなど、ユーザーがAIやシステムに対して伝えたい内容を定義
# - SystemMessage
#   システムが内部で管理・利用するメッセージを定義するためのインタフェース
#　　AIに対する振る舞いやトーンの設定、応答の制御を目的として使用する
######################################################################
messages = [
    SystemMessage("Translate the following from English into Japanese"), # ここを変えると返答が変わります
    HumanMessage("bye!"), # ここを変えると返答が変わります
]

######################################################################
# モデルの呼び出し
# モデルはSystemMessageに基づき、HumanMessageを処理する
# モデルからの返答を変数answerに格納
######################################################################
response = model.invoke(messages)

######################################################################
# 返答出力
######################################################################
print(response.content)