from pydantic import BaseModel

class ReadingTemplateVariables(BaseModel):
    calculated_score: int
    voice_quality: int
    pacing_score: int
    wpm_category: int
    fluency_score: int
    accuracy_score: float 
    correct_count: int
    total_words_count: int
    name: str
    view_link: str
    given_script: str
    evaluation: str

class QuoteInterpretationVariables(BaseModel):
    name: str # check
    interpretation: str #check
    quote: str # check
    feedback: str 
    understanding: int
    insightfulness: int
    personal_connection: int
    practical_application: int
    total_score: int # check
    view_link: str

class EnhancedReadingTemplateVariables(BaseModel):
    calculated_score: int
    correct_word_count: int
    total_words_count: int
    name: str
    view_link: str
    evaluation: str
    similarity_score: int
    
def reading_notification_template_card(variables: ReadingTemplateVariables):
    given_script = variables.given_script.replace('"', '\"')
    evaluation = variables.evaluation.replace("\n", "\\n")

    if variables.calculated_score >= 80:
        return f"{{\"type\": \"template\", \"data\": {{\"template_id\": \"ctp_AA0LqcGe6YqZ\", \"template_variable\": {{\"calculated_score\": {variables.calculated_score}, \"voice_quality\": {variables.voice_quality}, \"pacing_score\": {variables.pacing_score}, \"wpm_category\": {variables.wpm_category}, \"fluency_score\": {variables.fluency_score}, \"accuracy_score\": {int(variables.accuracy_score)}, \"evaluation\": \"{evaluation}\", \"given_script\": \"{given_script}\", \"name\": \"{variables.name}\", \"correct_count\": {variables.correct_count}, \"total_words_count\": {variables.total_words_count}, \"view_link\": \"{variables.view_link}\"}}}}}}"

    return f"{{\"type\": \"template\", \"data\": {{\"template_id\": \"ctp_AA0bLLpfBbac\", \"template_variable\": {{\"calculated_score\": {variables.calculated_score}, \"voice_quality\": {variables.voice_quality}, \"pacing_score\": {variables.pacing_score}, \"wpm_category\": {variables.wpm_category}, \"fluency_score\": {variables.fluency_score}, \"accuracy_score\": {int(variables.accuracy_score)}, \"evaluation\": \"{evaluation}\", \"given_script\": \"{given_script}\", \"name\": \"{variables.name}\", \"correct_count\": {variables.correct_count}, \"total_words_count\": {variables.total_words_count}, \"view_link\": \"{variables.view_link}\"}}}}}}"

def enhanced_reading_notification_template_card(variables: EnhancedReadingTemplateVariables):
    evaluation = variables.evaluation.replace("\n", "\\n")
   
    if variables.calculated_score >= 80:
        return f"""{{
            "type": "template",
            "data": {{
                "template_id": "ctp_AARhT2svnupq",
                "template_variable": {{
                    "assessment_status": "Congratulations,",
                    "calculated_score": "{variables.calculated_score}",
                    "evaluation": "{evaluation}",
                    "name": "{variables.name}",
                    "correct_word_count": {variables.correct_word_count},
                    "total_words_count": {variables.total_words_count},
                    "view_link": "{variables.view_link}",
                    "similarity_score": "{variables.similarity_score}"
                }}
            }}
        }}"""
    
    return f"""{{
            "type": "template",
            "data": {{
                "template_id": "ctp_AARXrrO6LOXe",
                "template_variable": {{
                    "assessment_status": "Failed assessment,",
                    "calculated_score": "{variables.calculated_score}",
                    "evaluation": "{evaluation}",
                    "name": "{variables.name}",
                    "correct_word_count": {variables.correct_word_count},
                    "total_words_count": {variables.total_words_count},
                    "view_link": "{variables.view_link}",
                    "similarity_score": "{variables.similarity_score}"
                }}
            }}
        }}"""

def quote_interpretation_template_card(variables: QuoteInterpretationVariables):
    feedback = variables.feedback.replace("\n", "\\n")
    if variables.total_score >= 7:
        return f"{{\"type\": \"template\", \"data\": {{\"template_id\": \"ctp_AA0Q5yF98Bl5\", \"template_variable\": {{\"total_score\": {variables.total_score}, \"name\": \"{variables.name}\", \"interpretation\": \"{variables.interpretation}\", \"quote\": \"{variables.quote}\", \"feedback\": \"{feedback}\", \"understanding\": {variables.understanding}, \"insightfulness\": {variables.insightfulness}, \"personal_connection\": {variables.personal_connection}, \"practical_application\": {variables.practical_application}, \"view_link\": \"{variables.view_link}\"}}}}}}"

    return f"{{\"type\": \"template\", \"data\": {{\"template_id\": \"ctp_AA0L3KyhmXXh\", \"template_variable\": {{\"total_score\": {variables.total_score}, \"name\": \"{variables.name}\", \"interpretation\": \"{variables.interpretation}\", \"quote\": \"{variables.quote}\", \"feedback\": \"{feedback}\", \"understanding\": {variables.understanding}, \"insightfulness\": {variables.insightfulness}, \"personal_connection\": {variables.personal_connection}, \"practical_application\": {variables.practical_application}, \"view_link\": \"{variables.view_link}\"}}}}}}"