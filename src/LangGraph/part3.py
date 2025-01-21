######################################################################
# LangGraph Quickstart
# https://langchain-ai.github.io/langgraph/tutorials/introduction/
#
# Part 3: Adding Memory to the Chatbot
# checkpointerとthread_idを使用して、各ステップのステートの状態を保存する
#
######################################################################
from typing import Annotated

from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
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
######################################################################
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)

######################################################################
# ノード間の遷移(エッジ)の追加
######################################################################
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")

######################################################################
# checkpointerの定義
######################################################################
memory = MemorySaver()

######################################################################
# グラフのコンパイル
######################################################################
graph = graph_builder.compile(checkpointer=memory)

######################################################################
# thread_idを定義
######################################################################
config = {"configurable": {"thread_id": "1"} }

######################################################################
# １番目のメッセージを定義
######################################################################
user_input = "Hi there! My name is Will. Let's talk in Japanese!"

######################################################################
# AIが生成した応答をストリーミングで逐次受信
######################################################################
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)

######################################################################
# 受信結果を表示
######################################################################
for event in events:
    event["messages"][-1].pretty_print()

######################################################################
# 2番目のメッセージを定義
######################################################################
user_input = "Remember my name?"

######################################################################
# AIが生成した応答をストリーミングで逐次受信
######################################################################
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
######################################################################
# 受信結果を表示
# １回目のやり取りをAIが覚えているのでWillと返ってくる
######################################################################
for event in events:
    event["messages"][-1].pretty_print()

######################################################################
# 3番目のメッセージを定義
######################################################################
user_input = "Remember my name?"

######################################################################
# AIが生成した応答をストリーミングで逐次受信
# thread_idを異なる値にする
######################################################################
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    {"configurable": {"thread_id": "2"}},
    stream_mode="values",
)

######################################################################
# 受信結果を表示
# 1~2回目のthread_idとは異なる値を設定したため、会話内容を保持していない
######################################################################
for event in events:
    event["messages"][-1].pretty_print()