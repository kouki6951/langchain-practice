######################################################################
# Build a simple LLM application with chat models and prompt templates
# https://python.langchain.com/docs/tutorials/llm_chain/
#
# Prompt Templates
#
######################################################################

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

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
# テンプレート文字列の定義
# {language}というプレースホルダーを設定する
# プレースホルダーは後の処理で具体値で書き換えられる
######################################################################
system_template = "Translate the folowing from English into {language}"

######################################################################
# ChatPromptTemplate の作成
#  - ChatPromptTemplate.from_messagesメソッド
#    チャットテンプレートを作成する。
#    "system": AIにタスクを表示するメッセージ(01.pyのSystemMessageに相当)
#    "user": ユーザからの入力(01.pyのHumanMessageに相当)
######################################################################
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

# 以下でも動作する、直接from_messagesメソッドの引数にプレースホルダーを設定されている文字列を指定しても良いし、
# 予め変数にプレースホルダーが設定されている文字列を格納されたものを使用しても良い
#
# ex1)
# prompt_template = ChatPromptTemplate.from_messages(
#     [("system", "Translate the folowing from English into {language}"), ("user", "{text}")]
# )
#
# ex2)
# system_template = "Translate the folowing from English into {language}"
# user_template = "{text}"
# prompt_template = ChatPromptTemplate.from_messages(
#     [("system", system_template), ("user", user_template)]
# )
#

######################################################################
# プロンプトの作成
# prompt_templateに格納されたテンプレート文字列のプレースホルダーに、
# それぞれlanguage=>Italian、text=>hiを置き換えてプロンプトを作成する。
######################################################################
prompt = prompt_template.invoke({"language": "Italian", "text": "hi"})

######################################################################
# 生成されたプロンプト(prompt)をAIモデルに渡して、レスポンスを取得する。
######################################################################
response = model.invoke(prompt)

######################################################################
# 返答出力
######################################################################
print(response.content)