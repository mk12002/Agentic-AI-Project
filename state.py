from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class ResearchState:
    topic: str = ""  
    research_summary: str = ""
    fact_check_results: Dict[str, str] = field(default_factory=dict)
    article: str = ""
    output_saved: bool = False
    message: str = ""
    llm: Optional[object] = field(default=None)
