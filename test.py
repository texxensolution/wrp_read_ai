from transformers import pipeline


analyzer = pipeline(model="models/pronunciation_v3", task="audio-classification")

input_path = "data/sample1.mp3"
result = analyzer(input_path)
print(result)

# analyzer.calculate_score(input_path)