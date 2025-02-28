import os
import json
import requests
from langchain.prompts import PromptTemplate
from state import ResearchState
from config import BASE_DIR, llm
from dataclasses import asdict
import urllib.parse
from tavily import TavilyClient

class ResearchTool:
    def __init__(self):
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.fact_check_api_key = os.getenv("GOOGLE_FACT_CHECK_API_KEY")
        self.fact_check_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

    def search_google(self, query: str) -> str:
        try:
            client = TavilyClient(api_key=self.tavily_api_key)
            results = client.search(query=query, search_depth="advanced", include_answers=True)
            
            snippets = [item["content"] for item in results["results"][:3] if "content" in item]
            return " ".join(snippets) if snippets else ""
        except Exception as e:
            print(f"⚠️ Error in Tavily search: {e}")
            return ""

    def search_wikipedia(self, query: str) -> str:
        try:
            formatted_query = urllib.parse.quote(query.replace(" ", "_"))  # Convert spaces to underscores
            response = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_query}")
            response.raise_for_status()
            data = response.json()
            return data.get("extract", "No Wikipedia data found.")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                return f"No Wikipedia page found for '{query}'. Try refining your search."
            return f"⚠️ Wikipedia API error: {e}"

    def search_arxiv(self, query: str) -> str:
        try:
            response = requests.get(f"http://export.arxiv.org/api/query?search_query=all:{query}&max_results=1")
            response.raise_for_status()
            return response.text[:1000]  # Limit text length
        except Exception as e:
            print(f"⚠️ Arxiv API error: {e}")
            return ""

    def fact_check(self, claim: str) -> str:
        try:
            params = {"query": claim, "key": self.fact_check_api_key}
            response = requests.get(self.fact_check_url, params=params)
            response.raise_for_status()
            data = response.json()
            if "claims" in data:
                return data["claims"][0]["text"]
            return "No fact-check available."
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                return "⚠️ Google Fact Check API access denied. Check your API key and permissions."
            return f"⚠️ Fact-check API error: {e}"


def get_research(state: dict) -> dict:
    research_tool = ResearchTool()
    topic = state.topic
    
    google_results = research_tool.search_google(topic)
    wiki_results = research_tool.search_wikipedia(topic)
    arxiv_results = research_tool.search_arxiv(topic)
    
    fact_check = research_tool.fact_check(topic)

    research_summary = f"Google: {google_results}\n\nWikipedia: {wiki_results}\n\nArxiv: {arxiv_results}"
    
    return {"research_summary": research_summary, "fact_check_results": fact_check}

def generate_news_article(state: dict) -> dict:
    research_state = state

    if not research_state.research_summary.strip():
        research_state.article = "No research data available."
        return asdict(research_state)  

    article_prompt = f"""
    Based on the following research, write a compelling and detailed news article:
    
    {research_state.research_summary}
    
    **Ensure the article follows this format:**
    - **Title**
    - **Introduction**
    - **Key Insights**
    - **Industry Impact**
    - **Future Prospects**
    - **Conclusion**
    
    Include relevant facts and ensure clarity.
    """

    response = llm.invoke(article_prompt)
    article_text = response.get("text", "").strip() if isinstance(response, dict) else str(response).strip()

    research_state.article = article_text
    return asdict(research_state)

def save_output(state: ResearchState) -> dict:
    topic = state.topic.replace(" ", "_")
    article = state.article
    research_summary = state.research_summary

    if not article.strip():
        state.message = "⚠️ No article content to save."
        return vars(state)

    article_path = os.path.join(BASE_DIR, f"{topic}.md")
    json_path = os.path.join(BASE_DIR, f"{topic}.json")

    os.makedirs(BASE_DIR, exist_ok=True)

    try:
        # Save Markdown file
        with open(article_path, "w", encoding="utf-8") as f:
            f.write(f"# {topic}\n\n{article}")

        # Save JSON file
        json_data = {
            "topic": topic,
            "research_summary": research_summary,
            "article": article
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4)

        state.output_saved = True
        state.message = f"✅ Research and article saved as {topic}.md and {topic}.json!"
    except Exception as e:
        state.output_saved = False
        state.message = f"❌ Error saving output: {str(e)}"

    return vars(state)
