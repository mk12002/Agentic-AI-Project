from langgraph.graph.state import StateGraph
from config import llm
from state import ResearchState
from dataclasses import asdict
from workflow_nodes import get_research, generate_news_article, save_output

def create_workflow():
    workflow = StateGraph(state_schema=ResearchState)

    workflow.add_node("research_agent", get_research)
    workflow.add_node("reporting_agent", generate_news_article)
    workflow.add_node("storage_agent", save_output)  

    workflow.add_edge("research_agent", "reporting_agent")
    workflow.add_edge("reporting_agent", "storage_agent")  

    workflow.set_entry_point("research_agent")
    workflow.set_finish_point("storage_agent")  

    return workflow.compile()

if __name__ == "__main__":
    topic = input("Enter the topic you want to research: ").strip()

    if not topic:
        print("❌ Error: Topic cannot be empty.")
        exit()

    try:
        executor = create_workflow()

        state = ResearchState(topic=topic)

        state_dict = asdict(state)

        result = executor.invoke(state_dict)

        print(result.get("message", "❌ Error: No output message."))
    except Exception as e:
        print(f"❌ Error running workflow: {str(e)}")
