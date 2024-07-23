from langchain_groq import ChatGroq
from pydantic import BaseModel
from pydantic.v1 import BaseModel

from src.common import TextPreprocessor


class QuoteTranslationResult(BaseModel):
    analytical_thinking: int
    originality: int
    language: int
    organization: int
    support: int
    focus_point: int
    evaluation: str

class QuoteTranslationService:
    def __init__(self, token: str, model: str = 'llama3-70b-8192'):
        self.client = ChatGroq(
            model_name=model,
            api_key=token,
            temperature=1,
            max_retries=3
        )
        self.structured_llm = self.client.with_structured_output(QuoteTranslationResult)

    async def evaluate(self, transcription: str, quote: str) -> QuoteTranslationResult:
        prompt = f"""
            ### Task:
            You will critically examine, evaluate a **quote** and a person's **interpretation** it can be english or tagalog or it can be both. Your task is to rate or score the person's interpretation based on the several criterias stated below and you will also provide a detailed explanation of your reasoning for each criteria:
            
            ### Evaluation Criteria:

            Analytical Thinking (1-5):
                - Superficial vs. Deep: Is the interpretation superficial, or does it delve into deeper meanings, implications, and themes?
                - Underlying Themes: Does the person identify and explore underlying themes or concepts in the quote?

            Originality (1-5):
                - Unique Perspective: Does the interpretation offer a fresh or unique perspective?
                - Avoidance of Clichés: Does the interpretation avoid common or clichéd views? 

            Language (1-5):
                - Clear Explanation: Is the interpretation articulated clearly and logically?
                - Consistent Argument: Does the interpretation present a consistent and well-structured argument?

            Organization (1-5):
                - Evaluate the structure and coherence of the overall work, including logical sequencing of ideas, smooth transitions between sections, and a clear and effective arrangement of content.

            Support (1-5):
                - Evidence and Examples: Is the interpretation supported by relevant evidence, examples, or analogies?
                - Logical Reasoning: Is the reasoning behind the interpretation strong and logical?

            Focus Point (1-5):
                - Personal Relevance: How well does the person relate the quote to their own experiences or beliefs?
                - Broader Relevance: Does the interpretation connect the quote to wider societal, cultural, or philosophical contexts?     

            ### Input:
            **Interpretation**: {transcription}
            **Quote**: {quote}

            ### Output:
            ```json{{
                "analytical_thinking": 0,
                "originality": 0,
                "language": 0,
                "organization": 0,
                "support": 0,
                "focus_point": 0,
                "evaluation": "detailed explanation"
            }}```
        """
        return await self.structured_llm.ainvoke(prompt)