######################################################################
# LangGraph Quickstart
# https://langchain-ai.github.io/langgraph/tutorials/introduction/
#
# Part 1: Build a Basic Chatbot
#
######################################################################
from typing import Annotated
from langchain_anthropic import ChatAnthropic
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

######################################################################
# State定義
# StateとはLangGraph内で現在の状態を保存すrう要素
# グラフ内のノードやエッジにわたされ、グラフがどの段階にあるかやどのタスクが
# 進行中なのかを記録する
# Memo1
#  TypedDictを継承することによって、辞書のキーとその値の型(type)を指定する
#  ことができる。
# Memo2
#  Annotatedを使用し、型に対するメタデータを指定する。
# Memo3
#  add_messagesとは、LangGraphライブラリで提供されるメッセージ処理のための
#  ユーティリティ関数のこと。
# Memo4
#  Memo1/Memo2/Memo3をまとめると、Stateという辞書型のクラスには、messages
# というキーが存在し、その値はlist型であり、add_messageというメタデータが付
#  加されている。
######################################################################
class State(TypedDict): # 
    messages: Annotated[list, add_messages]

######################################################################
# グラフの構築
######################################################################
graph_builder = StateGraph(State)

######################################################################
# 言語モデル（Anthropic LLM）の初期化
######################################################################
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")

######################################################################
# チャットボットのノード関数定義
######################################################################
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

######################################################################
# ノードの追加
######################################################################
graph_builder.add_node("chatbot", chatbot)

######################################################################
# ノード間の遷移(エッジ)の追加
######################################################################
graph_builder.add_edge(START, "chatbot")    # STARTノードからchatbotノードへの遷移
graph_builder.add_edge("chatbot", END)      # chatbotノードからENDノードへの遷移

######################################################################
# グラフのコンパイル
# 設定されたノードとエッジを使用して最終的なグラフを構築する。
# compile()が呼ばれると、ノード間の遷移が整理され、実行可能な
# グラフオブジェクト(graph)が生成される。
######################################################################
graph = graph_builder.compile()

######################################################################
# エントリーポイントを実行
######################################################################
state = {"messages": [{"role": "user", "content": "Hello, chatbot! Please talk me in Japanese"}]}
result = graph.invoke(state)
print(result)