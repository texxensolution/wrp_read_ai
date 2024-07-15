from src.modules.common import ScriptExtractor


extractor = ScriptExtractor("dictionary1.0.1.csv")

script = extractor.get_script("script-0006")
print(script)