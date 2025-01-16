######################################################################
# Build a simple LLM application with chat models and prompt templates
# https://python.langchain.com/docs/tutorials/llm_chain/
#
# OutputParsers
# 
######################################################################

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# 言語モデルの選択
model = ChatOpenAI(model="gpt-4o-mini")

# AIモデルに送信するメッセージの定義
messages = [
    SystemMessage("Translate the following from English into Japanese"), # ここを変えると返答が変わります
    HumanMessage("bye!"), # ここを変えると返答が変わります
]

# モデルの呼び出し
response = model.invoke(messages)

######################################################################
# OutputParsers(出力パーサー)の定義
# AIモデルからの返答は、返答に関するメタデータを含んでいる。
# 出力パーサーを使用することで、応答の中から必要なデータのみ抽出することができる。
######################################################################
parser = StrOutputParser()

######################################################################
# 出力パーサーを使用し、AIモデルからの返答から文字列を抽出する。
######################################################################
answer = parser.invoke(response)

######################################################################
# 返答出力
######################################################################
print(answer)

# 出力パーサーを使用しない場合は以下のように記述する必要がある
# print(response.content)

######################################################################
# チェーンでの使用
# 出力パーサーはモデルと組み合わせて使用することができる。
# 以下のチェーンでは、モデルの入力型を受け取り、出力パーサの出力型を返す。
# (要するにこういう書き方ができるよってこと)
######################################################################
chain = model | parser
print(chain.invoke(messages))
