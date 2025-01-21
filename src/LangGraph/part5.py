######################################################################
# LangGraph Quickstart
# https://langchain-ai.github.io/langgraph/tutorials/introduction/
#
# Part 5: Customizing State
#
######################################################################
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.types import Command, interrupt
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

######################################################################
# State定義
# messages -> チャットの履歴
# name, birthday -> 確認や修正が必要な情報を定義
######################################################################
class State(TypedDict):
    messages: Annotated[list, add_messages]
    name: str
    birthday: str

######################################################################
# ツールの定義１
# 人間の支援(ユーザーの入力)を通じて、名前と誕生美の確認・修正を行うツール
######################################################################
@tool
def human_assistance(
    name: str, birthday: str, tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    # ################################################################
    # ユーザーの介入要求
    # interruptを使用して人間に確認を依頼
    # question -> 質問内容
    # name, birthday -> データ
    ##################################################################
    """Request assistance from a human."""
    human_response = interrupt(
        {
            "question": "Is this correct?",
            "name": name,
            "birthday": birthday,
        },
    )
    # ################################################################
    # 「正しい」と回答された場合はデータをそのまま保持
    # ################################################################
    if human_response.get("correct", "").lower().startswith("y"):
        verified_name = name
        verified_birthday = birthday
        response = "Correct"
    # ################################################################
    # 修正が必要な場合は修正後のデータを更新
    # ################################################################
    else:
        verified_name = human_response.get("name", name)
        verified_birthday = human_response.get("birthday", birthday)
        response = f"Made a correction: {human_response}"

    # ################################################################
    # state_updateにStateの更新情報を格納
    # ################################################################
    state_update = {
        "name": verified_name,
        "birthday": verified_birthday,
        "messages": [ToolMessage(response, tool_call_id=tool_call_id)],
    }
    # ################################################################
    # ツールの実行結果として状態を更新する指示を返す
    # ################################################################
    return Command(update=state_update)


######################################################################
# ツールの定義２
# TravilySearchAPIに対してクエリを実行し、Web検索を行った結果をJSONで取得
######################################################################
tool = TavilySearchResults(max_results=2)
tools = [tool, human_assistance]

######################################################################
# 言語モデル（Anthropic LLM）の初期化
# bind_tools()でLLMにツール(TavilySearchResults, human_assistant)を統合
######################################################################
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm_with_tools = llm.bind_tools(tools)

######################################################################
# チャットボットのノード関数定義
# llm_with_tools.invoke() -> Stateのメッセージ履歴を元にLLMを呼び出し、
#                            応答を生成
# tool_calls <= 1         -> ツール呼び出しを一回に制限
######################################################################
def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}

######################################################################
# グラフの構築
######################################################################
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

######################################################################
# メモリ管理定義
# グラフの状態を保存し、セッションをまたいでも状態を維持可能に
######################################################################
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

######################################################################
# グラフ実行
######################################################################
user_input = (
    "Can you look up when LangGraph was released? "
    "When you have the answer, use the human_assistance tool for review."
)
config = {"configurable": {"thread_id": "1"}}

events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

######################################################################
# 人間の介入
######################################################################
human_command = Command(
    resume={
        "name": "LangGraph",
        "birthday": "Jan 17, 2024",
    },
)
events = graph.stream(human_command, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

# 以下実行時のログ
# ================================ Human Message =================================

# Can you look up when LangGraph was released? When you have the answer, use the human_assistance tool for review.
# ================================== Ai Message ==================================

# [{'text': "Certainly! I'll first use the search function to look up information about LangGraph's release, and then I'll use the human_assistance tool for review. Let's start with the search.", 'type': 'text'}, {'id': 'toolu_01AMpUkbUcB9XpWp8cCGq57N', 'input': {'query': 'When was LangGraph released'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]     
# Tool Calls:
#   tavily_search_results_json (toolu_01AMpUkbUcB9XpWp8cCGq57N)
#  Call ID: toolu_01AMpUkbUcB9XpWp8cCGq57N
#   Args:
#     query: When was LangGraph released
# ================================= Tool Message =================================
# Name: tavily_search_results_json

# [{"url": "https://medium.com/mitb-for-all/a-gentle-introduction-to-the-llm-multi-agents-multiverse-part-1-langgraph-2ac56f1b5b3c", "content": "Langgraph was released in January 2024 (“this year” at the time of writing) by the creators of LangChain, aiming to empower developers to build stateful, reliable multi-agent applications extending the capabilities of the LangChain framework. Just as the ecosystem of LLM orchestration libraries often takes LangChain as a reference point, the multi-agent systems landscape frequently looks to Langgraph, building their frameworks on similar core principles. In this example, we only need two keys: messages, which stores the conversation history (including intermediate outputs), and next, which helps the graph decide the next action—either to route to another agent or finish. For instance, if one of your nodes invokes another Langgraph object, you’ll need to define a second state for the nested Langgraph and create a mapping function to sync the main graph’s state with the subgraph’s state."}, {"url": "https://blog.langchain.dev/langgraph-studio-the-first-agent-ide/", "content": "In January 2023, we launched LangGraph, a highly controllable, low-level orchestration framework for building agentic applications. Since then, we've seen teams build more complex agentic applications for production; in turn, we've heavily invested in LangGraph, leading to a stable 0.1 release this past June."}]
# ================================== Ai Message ==================================

# [{'text': "Thank you for providing that information. It appears there's some conflicting information about the release date of LangGraph. Let me summarize what I found:\n\n1. One source suggests that LangGraph was released in January 2024.\n2. Another source, which seems to be from the official LangChain blog, states that LangGraph was launched in January 2023, with a stable 0.1 release in June 2023.\n\nGiven this discrepancy, it would be best to use the human_assistance tool to clarify the correct release date. I'll do that now.", 'type': 'text'}, {'id': 'toolu_019DstSx9xCYDUTPA8z24eY9', 'input': {'name': 'Assistant', 'birthday': '2023-01-01'}, 'name': 'human_assistance', 'type': 'tool_use'}]
# Tool Calls:
#   human_assistance (toolu_019DstSx9xCYDUTPA8z24eY9)
#  Call ID: toolu_019DstSx9xCYDUTPA8z24eY9
#   Args:
#     name: Assistant
#     birthday: 2023-01-01
# ================================== Ai Message ==================================

# [{'text': "Thank you for providing that information. It appears there's some conflicting information about the release date of LangGraph. Let me summarize what I found:\n\n1. One source suggests that LangGraph was released in January 2024.\n2. Another source, which seems to be from the official LangChain blog, states that LangGraph was launched in January 2023, with a stable 0.1 release in June 2023.\n\nGiven this discrepancy, it would be best to use the human_assistance tool to clarify the correct release date. I'll do that now.", 'type': 'text'}, {'id': 'toolu_019DstSx9xCYDUTPA8z24eY9', 'input': {'name': 'Assistant', 'birthday': '2023-01-01'}, 'name': 'human_assistance', 'type': 'tool_use'}]
# Tool Calls:
#   human_assistance (toolu_019DstSx9xCYDUTPA8z24eY9)
#  Call ID: toolu_019DstSx9xCYDUTPA8z24eY9
#   Args:
#     name: Assistant
#     birthday: 2023-01-01
# ================================= Tool Message =================================
# Name: human_assistance

# Made a correction: {'name': 'LangGraph', 'birthday': 'Jan 17, 2024'}
# ================================== Ai Message ==================================

# Thank you for the human assistance. The correction provided clarifies that:

# LangGraph was released on January 17, 2024.

# This aligns more closely with the first source I found, which mentioned January 2024. The second source I found earlier seems to have been incorrect or possibly confused LangGraph with a different product.

# To summarize the final answer to your question:
# LangGraph was released on January 17, 2024. This information has been verified through human assistance, correcting the conflicting information found in the initial search results.