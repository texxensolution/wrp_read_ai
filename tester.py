from langchain_groq import ChatGroq
from pydantic import BaseModel

class QuoteTranslationResult(BaseModel):
    analytical_thinking: int
    originality: int
    language: int
    organization: int
    support: int
    focus_point: int
    evaluation: str

model = ChatGroq(model_name='llama3-70b-8192', api_key='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', temperature=0)

structured_llm = model.with_structured_output(QuoteTranslationResult)

response = structured_llm.invoke("""
You are an AI Evaluator that compare applicant transcription to the hidden meaning of quotes. I only need you to return the score based on the criteria I set below and return only json format without any explanatory answer {"analytical_thinking": `score`, "originality": `score`, "language": `score`, "organization": `score`, "support": `score`, "focus_point": `score`, "evaluation": `evaluation is text not quantized`}:
Criterias:
- Analytical Thinking (1-5) = Critically examine, evaluate, and interpret information, ideas, or concepts demonstrated in the work you submit.
- Originality (0-5) = Grade the extent to which the content or ideas presented in the work demonstrate creativity, novelty, or uniqueness, reflecting independent thought or expression.
- Language (0-5) = Check the overall quality and effectiveness of the written or verbal communication, including factors such as grammar, vocabulary, sentence structure, clarity, and appropriate language usage
- Organization (0-5) = Evaluate the structure and coherence of the overall work, including logical sequencing of ideas, smooth transitions between sections, and a clear and effective arrangement of content.
- Support (0-5) = Examine the provision of evidence, examples, or relevant information to back up and strengthen the main points or arguments made in your work.
- Focus Point (0-5) = Assess the central or main idea of the work that is consistently maintained and developed throughout, ensuring that the content remains relevant and on-topic.

transcription: {Minsan, kailangan mong lumingon sa nakaraan para maintindihan ang mga bagay na naghihintay sa hinaharap.}
quote: {Sometimes, you have to look back in order to understand the things that lie ahead.}
""")

print(response)