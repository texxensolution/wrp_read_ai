import os
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from pydantic.v1 import BaseModel, Field
from src.common import TextPreprocessor
from src.common.utilities import get_prompt, get_prompt_raw

class QuoteTranslationResult(BaseModel):
    analytical_thinking: int = Field(default=0, description="""
        Critically examine, evaluate, and interpret information, ideas, or concepts demonstrated in the work you submit.
    """)
    originality: int = Field(default=0, description="""
        Grade the extent to which the content or ideas presented in the work demonstrate creativity, novelty, or uniqueness, reflecting independent thought or expression.
    """)
    language: int = Field(default=0, description="""
        Check the overall quality and effectiveness of the written or verbal communication, including factors such as grammar, vocabulary, sentence structure, clarity, and appropriate language usage.
    """)
    organization: int = Field(default=0, description="""
        Evaluate the structure and coherence of the overall work, including logical sequencing of ideas, smooth transitions between sections, and a clear and effective arrangement of content.
    """)
    support: int = Field(default=0, description="""
        Examine the provision of evidence, examples, or relevant information to back up and strengthen the main points or arguments made in your work.
    """)
    focus_point: int = Field(default=0, description="""
        Assess the central or main idea of the work that is consistently maintained and developed throughout, ensuring that the content remains relevant and on-topic.
    """)
    detailed_evaluation_per_criteria: str = Field(default="Detailed evaluation", description="""
        Detailed evaluation explanation per criteria or property include emoji for creativity.             
    """)

class QuoteTranslationService:
    def __init__(self, token: str, model: str = 'llama3-70b-8192'):
        self.client = ChatGroq(
            model_name=model,
            api_key=token,
            temperature=0.2,
            max_retries=3,
            max_tokens=8192,
            cache=False,
            verbose=True
        )
        self.structured_llm = self.client.with_structured_output(QuoteTranslationResult, method='function_calling')

    async def evaluate(self, transcription: str, quote: str) -> QuoteTranslationResult:
        parser = PydanticOutputParser(pydantic_object=QuoteTranslationResult)
        raw_prompt = get_prompt_raw(os.path.join('src', 'prompts', 'quote_translation', 'system.md'))
        prompt = PromptTemplate(
            template=raw_prompt,
            input_variables=["quote", "query"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        # And a query intended to prompt a language model to populate the data structure.
        prompt_and_model = prompt | self.client
        output = await prompt_and_model.ainvoke({
            "quote": quote,
            "query": transcription
        })
        response: QuoteTranslationResult = await parser.ainvoke(output)
        print(response)

        return response

        # system_prompt_path = os.path.join('src', 'prompts', 'quote_translation', 'system.md')
        # user_prompt_path = os.path.join('src', 'prompts', 'quote_translation', 'user.md')
        # input = (("system", get_prompt(system_prompt_path, {"{quote}": quote})), ('user', get_prompt(user_prompt_path, {"{content}": transcription})))
        # return await self.structured_llm.ainvoke(input)