"""
Example Chat Agent
==================
A minimal StateGraph chat agent — the entry point referenced in langgraph.json.
Replace this with your own agent graph.

This agent:
1. Receives a MessagesState (list of LangChain messages)
2. Passes messages to an LLM (ChatOpenAI by default)
3. Returns the LLM response

To add tools:
    model = ChatOpenAI(model="gpt-4o").bind_tools([search, calculator])
    # LangGraph will automatically route to tool_node when tool_calls present

Usage in langgraph.json:
    {"graphs": {"chat_agent": "app.agents.chat_agent:graph"}}
"""

from langchain_openai import ChatOpenAI
from langgraph.graph import START, MessagesState, StateGraph

# ============================================================================
# Define the model
# ============================================================================
# In production, read model config from AppConfig (get_config().models[0])
# For the scaffold, we use a simple default.

_model = ChatOpenAI(model="gpt-4o")


# ============================================================================
# Define nodes
# ============================================================================

def chat_node(state: MessagesState) -> dict:
    """Core chat node — invokes the LLM with current message history.

    LangGraph automatically:
    - Routes to a tool_node if the response contains tool_calls
    - Adds the AI response to state.messages
    """
    response = _model.invoke(state["messages"])
    return {"messages": [response]}


# ============================================================================
# Build and compile the graph
# ============================================================================

def build_chat_graph():
    """Build a simple chat agent StateGraph.

    Replace this function with your own graph — add nodes, tools,
    conditional edges, human-in-the-loop interrupts, etc.
    """
    builder = StateGraph(MessagesState)

    # Add nodes
    builder.add_node("chat", chat_node)

    # Add edges — START → chat → END (implicit)
    builder.add_edge(START, "chat")

    return builder.compile()


# Module-level graph instance for langgraph.json
graph = build_chat_graph()
