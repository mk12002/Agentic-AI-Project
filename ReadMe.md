# Research Automation System

## Overview
This project is an automated research system that collects information from various sources, fact-checks the data, and generates structured news articles. The system is built using LangGraph for workflow automation, LangChain for language model interactions, and various APIs for data retrieval.

---

## Features
- **Automated Web Research** (Tavily API for web crawling, Wikipedia API, ArXiv API)
- **Fact-Checking Mechanism** (Google Fact Check API)
- **News Article Generation** (LLM-powered article synthesis)
- **Structured Workflow** (Using LangGraph for modular state management)
- **Persistent Storage** (Saves research output as Markdown & JSON)

---

## Architecture
### **Research Agent**
Handles the collection of relevant research data using different APIs:
- **Tavily API**: Fetches search results from the web.
- **Wikipedia API**: Retrieves a summary of the topic from Wikipedia.
- **ArXiv API**: Queries academic papers from ArXiv.
- **Google Fact Check API**: Validates information using third-party fact-checking.

The **Research Agent** is implemented using Python and makes HTTP requests to fetch information from different sources. The responses are parsed, structured, and returned as a summary.

**Implementation:**
Located in `workflow_nodes.py` under the `ResearchTool` class.

---
### **Reporting Agent**
Generates a structured article based on the research summary.
- Uses a **Hugging Face-hosted LLM** (`deepseek-ai/deepseek-llm-r1-7b`) for text generation.
- Formats the output into structured sections: **Title, Introduction, Key Insights, Industry Impact, Future Prospects, and Conclusion.**
- Takes the research summary as input and constructs a detailed article using a predefined prompt template.

The **Reporting Agent** interacts with LangChain to invoke the LLM and process the text response efficiently.

**Implementation:**
Defined in `workflow_nodes.py` under `generate_news_article`.

---
### **Storage Agent**
Saves the final research output into structured files:
- **Markdown (`.md`)** for easy readability.
- **JSON (`.json`)** for structured data storage.

The **Storage Agent** ensures persistent storage of generated articles by writing them to disk inside the `data_storage/` directory.

**Implementation:**
Defined in `workflow_nodes.py` under `save_output`.

---

## Use of LangChain & LangGraph

### **LangChain Usage**
- The system utilizes **LangChain** for efficient interaction with language models.
- `langchain.prompts.PromptTemplate` is used to structure prompts for the LLM.
- `langchain_huggingface.HuggingFaceEndpoint` is used to call the DeepSeek AI model for article generation.

### **LangGraph Usage**
- **LangGraph** is used to create a structured and stateful workflow.
- `StateGraph` is used to define the sequence of operations between agents.
- `ResearchState` is used to manage the research data, fact-checking results, and generated content.
- The workflow defines the **entry point** as the `Research Agent` and follows a sequential pipeline until the `Storage Agent`.

**Implementation in `main.py`**:
```python
workflow = StateGraph(state_schema=ResearchState)
workflow.add_node("research_agent", get_research)
workflow.add_node("reporting_agent", generate_news_article)
workflow.add_node("storage_agent", save_output)
workflow.add_edge("research_agent", "reporting_agent")
workflow.add_edge("reporting_agent", "storage_agent")
workflow.set_entry_point("research_agent")
workflow.set_finish_point("storage_agent")
```

This structure ensures that the research process is modular, traceable, and expandable.

---

## Installation & Setup
### **1️. Clone the Repository**
```bash
git clone https://github.com/your-repo/research-bot.git
cd research-bot
```

### **2️. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3️. Set Up Environment Variables**
Create a `.env` file and configure the necessary API keys:
```
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
TAVILY_API_KEY=your_tavily_api_key
GOOGLE_FACT_CHECK_API_KEY=your_factcheck_api_key
```

---

## Usage
Run the program with:
```bash
python main.py
```
Enter a topic when prompted, and the system will:
1. **Perform research** using web crawling and academic sources.
2. **Validate information** using the Google Fact Check API.
3. **Generate a news article** based on the collected data.
4. **Save the output** as `.md` and `.json` files.

---

## File Structure
```
research-bot/
│── config.py         # Configures the Hugging Face LLM
│── main.py           # Orchestrates the workflow execution
│── state.py          # Defines the state schema
│── workflow_nodes.py # Implements research, reporting, and storage agents
│── data_storage/     # Stores output files
│── .env              # Contains API keys
│── requirements.txt  # Lists dependencies
```


