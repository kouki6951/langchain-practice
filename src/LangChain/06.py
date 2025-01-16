######################################################################
# Build a Simple LLM Application with LCEL
# https://python.langchain.com/v0.2/docs/tutorials/llm_chain/
#
# Chaining together components with LCEL
# 
######################################################################

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# Prompt Templates定義
system_template = "Translate the following into {language}"
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

# Model定義
model = ChatOpenAI(model="gpt-4o-mini")

# OutputParsers定義
parser = StrOutputParser()

######################################################################
# chainの作成
# chainとは処理を段階的に組み合わせたワークフローの構造のこと
# chainを利用することでデータが一連のステップを通過し、
# 最終的な結果が生成される仕組みを実現することができる
######################################################################
chain = prompt_template | model | parser

######################################################################
# チェーンの呼び出し(実行)
# chain.invoke()で定義したチェーンを実行する
######################################################################
result = chain.invoke({"language": "italian", "text": "hi"})

######################################################################
# 結果の出力
######################################################################
print(result)


