transcription = '[0.18s -> 8.52s] : :  As fresh snow blanketed the grounds of the kingdom, the White Knight gazed out upon the sprawling valley, sighed to himself, and said,\n[9.14s -> 12.7s] : :  I must be the loneliest knight in all of the land.\n[13.61s -> 19.63s] : :  All of a sudden, the White Knight spotted a strange creature wandering up the snowy path towards him.\n[20.15s -> 24.93s] : :  As the distance between the knight and the creature shrank, he saw that it was a cow.\n[25.63s -> 28.73s] : :  Who g-goes there? the White Knight stammered.\n[28.73s -> 32.25s] : :  To his surprise, a gentle voice responded,\n[33.05s -> 38.17s] : :  It is I, Maria, a calf who has found herself far from home.'
# single_line = "[13.61s -> 19.63s] : :  All of a sudden, the White Knight spotted a strange creature wandering up the snowy path towards him.\n"
def get_transcription(transcription: str):
    transcripts = []
    lines = transcription.split('\n')
    # timestamp, transcript = transcription.split(' : : ')
    for line in lines:
        timestamp, transcript = line.split(' : : ')
        transcript = transcript.strip()
        transcripts.append(transcript)

    return "\n".join(transcripts)

def combined_splitted_transcription_and_timestamp(segments):
    return "\n".join(segments)

def word_count(transcription: str):
    return len(transcription.split(' '))
    
transcripts = get_transcription(transcription)

count = word_count(transcripts)

print(count / 2)