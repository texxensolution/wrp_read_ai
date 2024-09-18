import os
import logging
from src.services.api_manager import APIManager
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from src.common.utilities import get_prompt_raw

logger = logging.getLogger("script_reading_service")


class ScriptReadingEvaluationResult(BaseModel):
    evaluation: str


class ScriptReadingService:
    def __init__(
        self,
        api_manager: APIManager,
        model: str = 'llama3-70b-8192'
    ):
        self.api_manager = api_manager
        self.client = ChatGroq(
            model_name=model,
            temperature=0.2,
            max_retries=3,
            max_tokens=8192,
            cache=False,
        )
        self.structured_llm = self.client.with_structured_output(
            ScriptReadingEvaluationResult, 
            method='function_calling'
        )

    async def evaluate(
        self,
        transcription: str,
        given_script: str
    ) -> ScriptReadingEvaluationResult:
        groq_api_key = self.api_manager.get_next_key()
        self.client.groq_api_key = groq_api_key
        logger.info("API Used for Script Reading GROQ: %s", groq_api_key)
        parser = PydanticOutputParser(
            pydantic_object=ScriptReadingEvaluationResult
        )
        raw_prompt = get_prompt_raw(
            os.path.join('src', 'prompts', 'script_reading', 'system.md')
        )
        prompt = PromptTemplate(
            template=raw_prompt,
            input_variables=["transcription", "given_script"],
            partial_variables={
                "format_instructions": parser.get_format_instructions()
            },
        )

        # And a query intended to prompt a language model to populate the data structure.
        prompt_and_model = prompt | self.client

        output = await prompt_and_model.ainvoke({
            "transcription": transcription,
            "given_script": given_script 
        })
        response: ScriptReadingEvaluationResult = await parser.ainvoke(output)

        return response