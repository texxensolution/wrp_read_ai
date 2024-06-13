from src.modules.common import Task
from src.modules.lark import FileManager, BitableManager
from src.modules.ollama import EloquentOpenAI
from dataclasses import dataclass

@dataclass
class QuoteTranslationEvaluator:
    file_manager: FileManager
    base_manager: BitableManager
    openai: EloquentOpenAI

    def process(self, task: Task):
        payload = task.payload
        record_id = payload['record_id']
        audio_path = payload['audio_path']

        # upload the audio file to base
        file_token = self.file_manager.upload(audio_path)
    
    def ai_grading(self, transcription: str, given_quote: str):
        combined_prompt = self.generate_prompt(
            transcription=transcription,
            given_quote=given_quote
        )
        evaluation = self.openai.evaluate(
            combined_prompt_answer=combined_prompt
        )
        print('evaluation', evaluation)


    def generate_prompt(self, transcription: str, given_quote: str):
        return f"""
            Instruction: Grade and evaluate the transcription interpretation of the given quote based on the criteria I set below and give a json response output:
            Criterias:
            1. Understanding of the Quote (5 points)
            Clarity: Does the applicant clearly understand the meaning of the quote?
            Accuracy: Is the interpretation accurate and faithful to the original context and intent of the quote?
            
            2. Relevance to the Question/Context (5 points)
            Contextual Fit: How well does the interpretation fit within the context of the question asked?
            Applicability: Is the interpretation relevant to the broader topic or issue being discussed?
            
            3. Depth of Analysis (5 points)
            Insight: Does the applicant provide insightful analysis and go beyond a surface-level interpretation?
            Nuance: Are the complexities and subtleties of the quote explored?
            
            4. Support and Justification (5 points)
            Evidence: Does the applicant support their interpretation with evidence or examples?
            Reasoning: Is the interpretation logically justified and well-argued?
            
            5. Originality and Creativity (5 points)
            Original Thought: Does the applicant bring original ideas or perspectives to their interpretation?
            Creativity: Is the interpretation creative and engaging?

            Given Quote: {given_quote}

            Interpretation: {transcription}
        """





