import os
from dotenv import load_dotenv

from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)

load_dotenv()

# Path to the audio file
AUDIO_FILE = "justine.mp3"

API_KEY = os.getenv("DEEPGRAM_TOKEN")


def main():
    try:
        # STEP 1 Create a Deepgram client using the API key
        deepgram = DeepgramClient(API_KEY)

        with open(AUDIO_FILE, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        #STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=False,
            punctuate=False
        )

        # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram.listen.prerecorded.v("1").transcribe_file(payload, options)
        

        # STEP 4: Print the response
        print(response['results']['channels'][0]['alternatives'][0]['transcript'])

    except Exception as e:
        print(f"Exception: {e}")


if __name__ == "__main__":
    main()

# # import eng_to_ipa as ipa

# # input = "the magical garden once upon a time in a small village there live a young girl named lily lily love exploring the wounds behind her house one sunny afternoon she discovered a hidden part she had never seen before curious she followed it the path led to a beautiful garden filled with flowers of every color in the center stood a large tree with golden leaves as lily approach she noticed a tiny door at the base of the tree she gently knock to her surprise the door crack open and outstand a tiny ferry with shimmering wings hello lily the fairy said with a smile i am flora the garden of this magical garden lily was amazed how do you know my name she asked ive been watching over you since you were born flora replied this garden is hidden and only those with your hearts can find it flour invited lily to explore the garden as they walk during explain that the garden could make dreams come true really wish for her family to be happy and healthy flora wave her wand and a soft glow surrounded lily your wish will come true because it comes from love flora said lily spent the afternoon playing with the fairies and animals in the garden as the sunset flora led her back to the pad remember lily you can visit us anytime you need hope or joy fluorescent lily thanks flora and walk back home her heart filled with happiness from that day on she often visited the magical garden bringing joy and love back to her village and so lily and her village live"
# # tokens = input.split(" ")
# # map = {}
# # for token in tokens:

# #     phonetics = ipa.convert(token, retrieve_all=True, stress_marks=False)
# #     map[token] = phonetics
# # print(map)


# from transformers import pipeline
# import numpy as np
# import os

# accuracy_classifier = pipeline(task="audio-classification", model="JohnJumon/pronunciation_accuracy")
# fluency_classifier = pipeline(task="audio-classification", model="JohnJumon/fluency_accuracy")
# prosodic_classifier = pipeline(task="audio-classification", model="JohnJumon/prosodic_accuracy")

# def pronunciation_scoring(audio):
#     accuracy_description = {
#       'Extremely Poor': 'Extremely poor pronunciation and only one or two words are recognizable',
#       'Poor': 'Poor, clumsy and rigid pronunciation of the sentence as a whole, with serious pronunciation mistakes',
#       'Average': 'The overall pronunciation of the sentence is understandable, with many pronunciation mistakes and accent, but it does not affect the understanding of basic meanings',
#       'Good': 'The overall pronunciation of the sentence is good, with a few pronunciation mistakes',
#       'Excellent': 'The overall pronunciation of the sentence is excellent, with accurate phonology and no obvious pronunciation mistakes'
#     }
#     fluency_description = {
#       'Very Influent': 'Intermittent, very influent speech, with lots of pauses, repetition, and stammering', 
#       'Influent': 'The speech is a little influent, with many pauses, repetition, and stammering', 
#       'Average': 'Fluent in general, with a few pauses, repetition, and stammering', 
#       'Fluent': 'Fluent without noticeable pauses or stammering'
#     }
#     prosodic_description = {
#       'Poor': 'Poor intonation and lots of stammering and pauses, unable to read a complete sentence', 
#       'Unstable': 'Unstable speech speed, speak too fast or too slow, without the sense of rhythm', 
#       'Stable': 'Unstable speech speed, many stammering and pauses with a poor sense of rhythm', 
#       'Almost': 'Nearly correct intonation at a stable speaking speed, nearly smooth and coherent, but with little stammering and few pauses', 
#       'Perfect': 'Correct intonation at a stable speaking speed, speak with cadence, and can speak like a native'
#     }
#     accuracy = accuracy_classifier(audio)
#     fluency = fluency_classifier(audio)
#     prosodic = prosodic_classifier(audio)

#     result = {
#       'accuracy': accuracy,
#       'fluency': fluency,
#       'prosodic': prosodic
#     }
#     print(accuracy)
#     print(fluency)
#     print(prosodic)

#     for category, scores in result.items():
#         max_score_label = max(scores, key=lambda x: x['score'])['label']
#         result[category] = max_score_label

#     return result['accuracy'], accuracy_description[result['accuracy']], result['fluency'], fluency_description[result['fluency']], result['prosodic'], prosodic_description[result['prosodic']]

# pronunciation = pipeline(model="megathil/fluency_prediction", task="audio-classification")
# print(pronunciation("justine.mp3"))
# # pronunciation_scoring("justine.mp3")
