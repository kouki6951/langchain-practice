######################################################################
# How to use chat models to call tools
# https://python.langchain.com/docs/how_to/tool_calling/
#
# How to use chat models to call tools
# 
######################################################################

# def add(a: int, b: int) -> int:
#     """Add two integers.

#     Args:
#         a: First integer
#         b: Second integer
#     """
#     return a + b


# def multiply(a: int, b: int) -> int:
#     """Multiply two integers.

#     Args:
#         a: First integer
#         b: Second integer
#     """
#     return a * b

from typing_extensions import Annotated, TypedDict


class add(TypedDict):
    """Add two integers."""

    # Annotations must have the type and can optionally include a default value and description (in that order).
    a: Annotated[int, ..., "First integer"]
    b: Annotated[int, ..., "Second integer"]


class multiply(TypedDict):
    """Multiply two integers."""

    a: Annotated[int, ..., "First integer"]
    b: Annotated[int, ..., "Second integer"]


tools = [add, multiply]

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

llm_with_tools = llm.bind_tools(tools)

query = "What is 3 * 12?"

print(llm_with_tools.invoke(query))
