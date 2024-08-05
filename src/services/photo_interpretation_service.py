from langchain_groq import ChatGroq
from pydantic.v1 import BaseModel


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
            temperature=1,
            max_retries=2
        )
        self.structured_llm = self.client.with_structured_output(PhotoInterpretationResult)

    async def evaluate(self, transcription: str, description: str) -> PhotoInterpretationResult:
        prompt = f"""
        language allowed: tagalog, english
        You are an AI Evaluator that compare person interpretation to the hidden meaning of image based on description. 
        You need to return the score based on the criteria I set below and return only json format:

        give low score to those who violate rules below:
            - if the interpretation is not related to image description give low score {{"Analytical Thinking": `score`, "Originality": `score`, "Language": `score`, "Organization": `score`, "Support": `score`, "Focus Point": `score`, "evaluation": `evaluation is text not quantized`}}:

        Criterias:
        - Analytical Thinking (1-5) = Critically examine, evaluate, and interpret information, ideas, or concepts demonstrated in the work you submit.
        - Originality (1-5) = Grade the extent to which the content or ideas presented in the work demonstrate creativity, novelty, or uniqueness, reflecting independent thought or expression.
        - Language (1-5) = Check the overall quality and effectiveness of the written or verbal communication, including factors such as grammar, vocabulary, sentence structure, clarity, and appropriate language usage
        - Organization (1-5) = Evaluate the structure and coherence of the overall work, including logical sequencing of ideas, smooth transitions between sections, and a clear and effective arrangement of content.
        - Support (1-5) = Examine the provision of evidence, examples, or relevant information to back up and strengthen the main points or arguments made in your work.
        - Focus Point (1-5) = Assess the central or main idea of the work that is consistently maintained and developed throughout, ensuring that the content remains relevant and on-topic.

        Interpretation: {transcription}
        Image Description: {description}

        ```json{{analytical_thinking: `1-5`, originality: `1-5`, language: `1-5`, organization: `1-5`, support: `1-5`, focus_point: `1-5`, evaluation: `explanation`}}```
        """
        return await self.structured_llm.ainvoke(prompt)