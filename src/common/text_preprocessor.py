import re
import json

class TextPreprocessor:
    @staticmethod
    def normalize(text: str):
        pattern = r'[^a-zA-Z0-9\s]'

        text = re.sub(pattern, '', text)
        # Convert to lowercase
        return text.lower()
    
    @staticmethod
    def normalize_text_with_new_lines(texts: str):
        new_texts = []
        lines = texts.split('\n')

        for line in lines:
            text = line.strip()
            new_texts.append(text)

        return TextPreprocessor.normalize(" ".join(new_texts).lower())
    
    @staticmethod
    def remove_json_object_from_texts(text: str):
        start_index, end_index = text.find('{'), text.find('}') + 1 
        evaluation = text[end_index:]
        return evaluation
    
        
    @staticmethod
    def get_json_from_text(text: str):
        start_index, end_index = text.find('{'), text.find('}') + 1 

        json_data = text[start_index:end_index]

        return json.loads(json_data)