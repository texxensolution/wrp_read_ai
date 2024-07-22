from langchain_groq import ChatGroq
from pydantic.v1 import BaseModel

from src.common import TextPreprocessor


class PhotoInterpretationResult(BaseModel):
    analytical_thinking: int
    originality: int
    language: int
    organization: int
    support: int
    focus_point: int
    evaluation: str

class PhotoInterpretationService:
    def __init__(self, token: str, model: str = 'llama3-70b-8192'):
        self.client = ChatGroq(
            model_name=model,
            api_key=token,
            temperature=0,
            max_retries=2
        )
        self.structured_llm = self.client.with_structured_output(PhotoInterpretationResult)

    async def evaluate(self, transcription: str, description: str) -> PhotoInterpretationResult:
        prompt = """
        You are an AI Evaluator that compare applicant transcription to the hidden meaning of image based on description. I only need you to return the score based on the criteria I set below and return only json format without any explanatory answer and if the interpretation is not related to image description give low score {{"Analytical Thinking": `score`, "Originality": `score`, "Language": `score`, "Organization": `score`, "Support": `score`, "Focus Point": `score`, "evaluation": `evaluation is text not quantized`}}:
        Criterias:
        - Analytical Thinking (1-5) = Critically examine, evaluate, and interpret information, ideas, or concepts demonstrated in the work you submit.
        - Originality (0-5) = Grade the extent to which the content or ideas presented in the work demonstrate creativity, novelty, or uniqueness, reflecting independent thought or expression.
        - Language (0-5) = Check the overall quality and effectiveness of the written or verbal communication, including factors such as grammar, vocabulary, sentence structure, clarity, and appropriate language usage
        - Organization (0-5) = Evaluate the structure and coherence of the overall work, including logical sequencing of ideas, smooth transitions between sections, and a clear and effective arrangement of content.
        - Support (0-5) = Examine the provision of evidence, examples, or relevant information to back up and strengthen the main points or arguments made in your work.
        - Focus Point (0-5) = Assess the central or main idea of the work that is consistently maintained and developed throughout, ensuring that the content remains relevant and on-topic.

        Interpretation: {}
        Image Description: {}
        """.format(transcription, description)
        return await self.structured_llm.ainvoke(prompt)