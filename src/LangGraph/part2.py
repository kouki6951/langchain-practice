######################################################################
# LangGraph Quickstart
# https://langchain-ai.github.io/langgraph/tutorials/introduction/
#
# Part 2: Enhancing the Chatbot with Tools
# TavilySearch(AIエンジン用に設計された検索エンジンAPI)を使用する。
#
######################################################################
from typing import Annotated

from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

######################################################################
# State定義
######################################################################
class State(TypedDict):
    messages: Annotated[list, add_messages]

######################################################################
# グラフの構築
######################################################################
graph_builder = StateGraph(State)

######################################################################
# ツールの定義
# memo1
# TravilySearchResultsを実行するとTravilySearchAPIに対してクエリを実行し、
# 結果をJSON形式で返却する。
######################################################################
tool = TavilySearchResults(max_results=2)
tools = [tool]

######################################################################
# 言語モデル（Anthropic LLM）の初期化
# memo1
# bind_tools：外部ツールをモデルに結び付ける
######################################################################
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm_with_tools = llm.bind_tools(tools)

######################################################################
# チャットボットのノード関数定義
######################################################################
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

######################################################################
# ノードの追加
######################################################################
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

######################################################################
# 条件付きエッジを追加
# memo1
#  "chatbot"の実行後、tools_conditionsがTrueを返す時にツールノードが実行さ
#  れる。
# memo2
#  tools_conditionは現在の状態(State)を確認し、外部ツールを呼び出す必要が
#  あるかを判定する
######################################################################
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

######################################################################
# ノード間の遷移(エッジ)の追加
######################################################################
# toolsノードが実行された場合、再び"chatbot"ノードに遷移するように設定
graph_builder.add_edge("tools", "chatbot")
# グラフの最初のノードを"chatbot"に設定
graph_builder.set_entry_point("chatbot")

######################################################################
# グラフのコンパイル
# 設定されたノードとエッジを使用して最終的なグラフを構築する。
# compile()が呼ばれると、ノード間の遷移が整理され、実行可能な
# グラフオブジェクト(graph)が生成される。
######################################################################
graph = graph_builder.compile()

######################################################################
# グラフの実行
######################################################################
state = {"messages": [{"role": "user", "content": "What's a 'node' in LangGraph? Please tell me in Japanese."}]}
result = graph.invoke(state)
print(result)