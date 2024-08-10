import os
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from pydantic.v1 import BaseModel, Field
from src.common.utilities import get_prompt, get_prompt_raw

class CriterionFeedback(BaseModel):
    score: int = Field(default=1, ge=1, le=3)
    feedback: str

class QuoteTranslationResult(BaseModel):
    understanding: CriterionFeedback
    personal_connection: CriterionFeedback
    insightfulness: CriterionFeedback
    practical_application: CriterionFeedback
    
    def get_feedback(self):
        return f"""**Feedback** \\n\\n**Understanding**: {self.understanding.feedback} \\n\\n**Personal Connection**: {self.personal_connection.feedback} \\n\\n**Insightfulness**: {self.insightfulness.feedback} \\n\\n**Practical Application**: {self.practical_application.feedback}""".strip()
        

class QuoteTranslationService:
    def __init__(self, token: str, model: str = 'llama3-70b-8192'):
        self.client = ChatGroq(
            model_name=model,
            api_key=token,
            temperature=0.2,
            max_retries=3,
            max_tokens=8192,
            cache=False,
        )
        self.structured_llm = self.client.with_structured_output(QuoteTranslationResult, method='function_calling')

    async def evaluate(self, transcription: str, quote: str) -> QuoteTranslationResult:
        parser = PydanticOutputParser(pydantic_object=QuoteTranslationResult)
        raw_prompt = get_prompt_raw(os.path.join('src', 'prompts', 'quote_translation', 'system.md'))
        prompt = PromptTemplate(
            template=raw_prompt,
            input_variables=["quote", "interpretation"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        # And a query intended to prompt a language model to populate the data structure.
        prompt_and_model = prompt | self.client
        output = await prompt_and_model.ainvoke({
            "quote": quote,
            "interpretation": transcription
        })
        response: QuoteTranslationResult = await parser.ainvoke(output)

        return response