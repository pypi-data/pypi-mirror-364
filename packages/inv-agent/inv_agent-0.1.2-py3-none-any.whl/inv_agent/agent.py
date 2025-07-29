import json, re
from json import JSONDecoder
from typing_extensions import TypedDict as TE_TypedDict
from typing import Annotated, Literal
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from inventory_tools import TOOLS
from logger import log
import os
from dotenv import load_dotenv

load_dotenv()

class AgentState(TE_TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    current_input: str
    tool_call: dict
    continue_conversation: bool

# Initialize Ollama model
llm = ChatOllama(model="llama3.1:latest", temperature=0)

SYSTEM_PROMPT = f"""You are a helpful clinic inventory assistant. You help users manage medicine inventory and can have normal conversations.

Available inventory tools and Requirements:
{json.dumps({name: {"description": info["description"], "required_args": info["required_args"]} for name, info in TOOLS.items()}, indent=2)}

When users ask about inventory operations, medicines, stock, or health conditions that need medicine recommendations, analyze if a tool would be helpful. Otherwise, respond normally.

Be natural, helpful, and only suggest tools when they would genuinely help the user's request."""

def intelligent_response(state: AgentState) -> dict:
    """Main response handler using LLM for all decision making and argument extraction"""
    user_input = state["current_input"].strip()
    history = state["messages"][-6:]

    # Create comprehensive prompt for LLM to handle everything
    comprehensive_prompt = f"""{SYSTEM_PROMPT}
Conversation History:
{chr(10).join([f"{msg.__class__.__name__}: {msg.content}" for msg in history])}

Current User Input: "{user_input}"

TASK: Analyze the user's request and respond with JSON in ONE of these formats:

1. IF NO TOOL IS NEEDED (casual conversation, greetings, etc.):
{{"response": "your conversational response here"}}

2. IF A TOOL IS NEEDED BUT ARGUMENTS ARE MISSING:
{{"tool": "tool_name", "missing_args": ["arg1", "arg2"], "extracted_args": {{"arg1": "value1"}}, "question": "Natural question to ask user for missing arguments"}}

3. IF A TOOL IS NEEDED AND ALL ARGUMENTS ARE AVAILABLE:
{{"tool": "tool_name", "args": {{"arg1": "value1", "arg2": "value2"}}, "explanation": "what you will do"}}

ARGUMENT EXTRACTION GUIDELINES:
- For "input" (medicine name): Extract from phrases like "amoxcillin", "check paracetamol", "i want aspirin", "status of ibuprofen"
- For "quantity": Extract numbers from "10 tablets", "remove 5", "add 20 units", "fifty capsules"
- For "stock_alert_threshold": Extract numbers from "set alert to 15", "threshold 20", "alert at 5 units"
- For restock requests: medicine_name, requested_stock

EXAMPLES:
- "amoxcillin" → {{"tool": "read_med", "args": {{"input": "amoxcillin"}}, "explanation": "I'll check the details for amoxcillin"}}
- "remove 10 paracetamol" → {{"tool": "remove_med", "args": {{"input": "paracetamol", "quantity": 10}}, "explanation": "I'll remove 10 units of paracetamol from inventory"}}
- "set alert for aspirin to 15" → {{"tool": "set_alert", "args": {{"input": "aspirin", "stock_alert_threshold": 15}}, "explanation": "I'll set the stock alert threshold for aspirin to 15 units"}}
- "add new medicine" → {{"tool": "add_med", "missing_args":["drugId", "name", "genericName", "manufacturer", "batchNumber", "expiryDate", "quantity", "unit", "pricePerUnit", "location"] , "extracted_args": {{}}, "question": "I need the complete medicine information to add it. Please provide: Drug ID, Medicine name, Generic name, Manufacturer, Batch number, Expiry date (YYYY-MM-DD), Quantity, Unit, Price per unit, and Storage location."}}
- "hello" → {{"response": "Hello! I'm here to help you manage your clinic inventory. What can I assist you with today?"}}

Be intelligent about extracting arguments from natural language. Users might say things like:
- "what's the status of amoxcillin" → extract "amoxcillin" as input for read_med
- "i need to check aspirin stock" → extract "aspirin" as input for read_med
- "use 5 tablets of paracetamol" → extract "paracetamol" as input and 5 as quantity for remove_med
- "set low stock alert for ibuprofen at 20" → extract "ibuprofen" as input and 20 as stock_alert_threshold for set_alert

Your response:"""

    try:
        response = llm.invoke([HumanMessage(content=comprehensive_prompt)])
        response_text = response.content.strip()

        # Attempt to extract JSON object from LLM response
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            try:
                cleaned = re.sub(r'[\x00-\x1f]+', '', match.group(0))
                analysis = json.loads(cleaned)

                if "response" in analysis:
                    return {
                        "messages": [AIMessage(content=analysis["response"])],
                        "tool_call": {},
                        "continue_conversation": True
                    }

                elif "tool" in analysis and "args" in analysis:
                    tool_name = analysis["tool"]
                    args = analysis["args"]
                    explanation = analysis.get("explanation", "executing requested operation")

                    if tool_name not in TOOLS:
                        return {
                            "messages": [AIMessage(content=f"I don't have access to a tool named '{tool_name}'.")],
                            "tool_call": {},
                            "continue_conversation": True
                        }

                    return {
                        "messages": [AIMessage(content=f"Understood. {explanation.capitalize()} now.")],
                        "tool_call": {"tool": tool_name, "args": args},
                        "continue_conversation": True
                    }

                elif "tool" in analysis and "missing_args" in analysis:
                    return {
                        "messages": [AIMessage(content=analysis.get("question", "I need more info to proceed."))],
                        "tool_call": {},
                        "continue_conversation": True
                    }

            except json.JSONDecodeError as json_err:
                log("JSON Decode Error", f"{json_err} — Raw: {response_text}")

        # Fallback to conversational response on parsing failure or unexpected output
        fallback_msg = (
            "I couldn't fully process that as an action. Here's what I understood:\n\n"
            f"{response_text}\n\n"
            "Could you clarify or confirm what you'd like me to do?"
        )
        return {
            "messages": [AIMessage(content=fallback_msg)],
            "tool_call": {},
            "continue_conversation": True
        }

    except Exception as e:
        log("Error in intelligent_response", f"{e}")
        return {
            "messages": [AIMessage(content="Something went wrong while processing your request. Could you please rephrase it?")],
            "tool_call": {},
            "continue_conversation": True
        }

def execute_tool_node(state: AgentState) -> dict:
    """Execute the tool and process results"""
    tool_call = state["tool_call"]
    tool_name = tool_call["tool"]
    args = tool_call["args"]
    
    try:
        log("Executing Tool", f"Tool: {tool_name}, Arguments: {json.dumps(args, indent=2)}")

        # Execute the tool
        result = TOOLS[tool_name]["func"](args)
        
        # Use LLM to generate a natural response based on the result
        response_prompt = f"""You are a helpful pharmacy inventory assistant. Based on the following tool execution result, provide a natural, conversational response to the user.

Tool Executed: {tool_name}
Parameters Used: {json.dumps(args, indent=2)}
Results: {json.dumps(result, indent=2)}

Response Guidelines:
- Speak in natural and conversational tone
- Start with the key information from the results
- Use bullet points for structured data when helpful
- Be friendly but professional
- For errors: explain what went wrong clearly
- For success: highlight important information like stock levels, dates, prices, expiry days
- Show alerts if stock is low or if email notifications were sent
- For expiring medicines, mention expiry dates and days remaining
- Never mention "tool execution" or technical details

Example Response Styles:
Success: "
Great! I found the information for Paracetamol 500mg: 
• Drug ID: MED-00123 
• Current Stock: 150 tablets 
• Stock Alert Threshold: 50 tablets 
• Expiry: 2025-12-31 (365 days remaining) 
• Price: ₹0.25 per tablet 
• Location: Shelf A-2
"
Error: "I couldn't find that medicine in our inventory. Please check the spelling or try a different name."
Stock Update: "Perfect! I've updated the stock. Paracetamol now has 140 tablets remaining (reduced by 10). Current stock level is adequate."
Alert Set: "Stock alert threshold for Aspirin has been set to 15 units. You'll be notified when stock drops to this level."
Low Stock Alert: "⚠️ WARNING: Stock is now below the alert threshold! Alert email has been sent to the manager."
"""
        
        llm_response = llm.invoke([HumanMessage(content=response_prompt)])
        
        response_content = llm_response.content
        
        log("Tool Execution Complete", f"Tool: {tool_name}, Success: {result.get('status') == 'success'}")
        
        return {
            "messages": [AIMessage(content=response_content)],
            "tool_call": {},
            "continue_conversation": True
        }
    
    except Exception as e:
        log("Tool Execution Error", f"Tool: {tool_name}, Error: {str(e)}")
        return {
            "messages": [AIMessage(content=f"I encountered an error while processing your request: {str(e)}. Please try again or let me know if you need help with something else.")],
            "tool_call": {},
            "continue_conversation": True
        }

def should_execute_tool(state: AgentState) -> Literal["execute_tool", "__end__"]:
    """Determine if we should execute a tool"""
    return "execute_tool" if state["tool_call"].get("tool") else "__end__"

def create_agent():
    """Create the agent workflow"""
    # Create the graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("intelligent_response", intelligent_response)
    graph.add_node("execute_tool", execute_tool_node)
    
    # Add edges
    graph.add_edge(START, "intelligent_response")
    graph.add_conditional_edges(
        "intelligent_response",
        should_execute_tool,
        {
            "execute_tool": "execute_tool",
            "__end__": END
        }
    )
    graph.add_edge("execute_tool", END)

    log("Medical Inventory Management Agent Created")
    
    return graph.compile()