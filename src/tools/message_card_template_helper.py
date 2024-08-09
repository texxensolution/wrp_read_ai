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

def reading_notification_template_card(variables: ReadingTemplateVariables):
    given_script = variables.given_script.replace('"', '\"')
    evaluation = variables.evaluation.replace("\n", "\\n")

    if variables.calculated_score >= 80:
        return f"{{\"type\": \"template\", \"data\": {{\"template_id\": \"ctp_AA0LqcGe6YqZ\", \"template_variable\": {{\"calculated_score\": {variables.calculated_score}, \"voice_quality\": {variables.voice_quality}, \"pacing_score\": {variables.pacing_score}, \"wpm_category\": {variables.wpm_category}, \"fluency_score\": {variables.fluency_score}, \"accuracy_score\": {int(variables.accuracy_score)}, \"evaluation\": \"{evaluation}\", \"given_script\": \"{given_script}\", \"name\": \"{variables.name}\", \"correct_count\": {variables.correct_count}, \"total_words_count\": {variables.total_words_count}, \"view_link\": \"{variables.view_link}\"}}}}}}"

    return f"{{\"type\": \"template\", \"data\": {{\"template_id\": \"ctp_AA0bLLpfBbac\", \"template_variable\": {{\"calculated_score\": {variables.calculated_score}, \"voice_quality\": {variables.voice_quality}, \"pacing_score\": {variables.pacing_score}, \"wpm_category\": {variables.wpm_category}, \"fluency_score\": {variables.fluency_score}, \"accuracy_score\": {int(variables.accuracy_score)}, \"evaluation\": \"{evaluation}\", \"given_script\": \"{given_script}\", \"name\": \"{variables.name}\", \"correct_count\": {variables.correct_count}, \"total_words_count\": {variables.total_words_count}, \"view_link\": \"{variables.view_link}\"}}}}}}"
        