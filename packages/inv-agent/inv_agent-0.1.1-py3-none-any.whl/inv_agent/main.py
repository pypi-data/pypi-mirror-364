from agent import create_agent
from langchain_core.messages import HumanMessage, AIMessage
from inventory_tools import init_db
from logger import log

def chat_with_agent():
    print("🏥 Clinic Inventory Assistant")
    print("Type 'exit', 'quit', or 'bye' to end the conversation")
    print("=" * 50)

    agent = create_agent()
    state = {
        "messages": [],
        "current_input": "",
        "tool_call": {},
        "continue_conversation": True
    }

    try:
        while True:
            user_input = input("\n👤 You: ").strip()
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n🤖 Assistant: Goodbye! Take care of your inventory! 👋")
                break
            if not user_input:
                continue

            state["current_input"] = user_input
            state["messages"].append(HumanMessage(content=user_input))

            try:
                result = agent.invoke(state)

                # Filter out only AIMessage and print the last one
                ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
                if ai_messages:
                    last = ai_messages[-1].content
                    print(f"\n🤖 Assistant: {last}")

                state = result

            except Exception as e:
                print(f"\n⚠️ Error: {e}")
                print("Let me try to help you in a different way...")

    except KeyboardInterrupt:
        print("\n\n🤖 Assistant: Goodbye! Take care of your inventory! 👋")
        return

if __name__ == "__main__":
    print("🚀 Starting Medicine Inventory Assistant...")
    print("- Make sure ollama is running & inventory_tools is available")
    log("Database Intialising")
    init_db()
    print("-" * 50)
    chat_with_agent()
