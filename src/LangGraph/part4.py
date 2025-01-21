######################################################################
# LangGraph Quickstart
# https://langchain-ai.github.io/langgraph/tutorials/introduction/
#
# Part 4: Human-in-the-loop
#
######################################################################
from typing import Annotated

from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langgraph.types import Command, interrupt

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
#  AIが対応できない質問を人間にエスカレーションする
#  引数 ユーザからの質問またはリクエスト
#  戻り値 人間の回答
#  interrupt関数を使用することで、グラフの実行を一度中断し、外部にエスカレー
#  ションする時間を作る
######################################################################
@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]

tool = TavilySearchResults(max_results=2)
tools = [tool, human_assistance]

######################################################################
# 言語モデル（Anthropic LLM）の初期化
# memo1
# bind_tools：外部ツールをモデルに結び付ける
######################################################################
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm_with_tools = llm.bind_tools(tools)

######################################################################
# チャットボットのノード関数定義
# message.tool_cellsが1つ以下であることを確認することで、並列ツール呼び出し
# を防ぐ
######################################################################
def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    # Because we will be interrupting during tool execution,
    # we disable parallel tool calling to avoid repeating any
    # tool invocations when we resume.
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}

######################################################################
# ノードの追加
######################################################################
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

######################################################################
# 条件付きエッジを追加
######################################################################
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

######################################################################
# checkpointerの定義
######################################################################
memory = MemorySaver()

######################################################################
# グラフのコンパイル
######################################################################
graph = graph_builder.compile(checkpointer=memory)

######################################################################
# １番目のメッセージを定義
######################################################################
user_input = "AIエージェントを構築するために専門家の指導が必要です。支援をお願いできますか？"

######################################################################
# thread_idを定義
######################################################################
config = {"configurable": {"thread_id": "1"}}

######################################################################
# AIが生成した応答をストリーミングで逐次受信
######################################################################
events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

######################################################################
# 外部からの回答をを定義
######################################################################
human_response = (
    "エージェントの構築にはLangGraphをお勧めします。"
    " 単純な自律型エージェントよりもはるかに信頼性が高く、拡張性もあります。"
)

######################################################################
# commandオブジェクトの生成
######################################################################
human_command = Command(resume={"data": human_response})

######################################################################
# AIが生成した応答をストリーミングで逐次受信
######################################################################
events = graph.stream(human_command, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()