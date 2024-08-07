import pytest
from src.common import get_necessary_fields_from_payload
from src.dtos import RequiredFieldsScriptReading

payload_1 = {
    "user_id": "test_1",
    "email": "test1@test.com",
    "record_id": "recewqewq123",
    "audio_url": "https://aa946349afe37ac713ba0d29ea52cce6.cdn.bubble.io/f1722966844301x460290914585556300/guianacaballeda304%40gmail.com.mp3",
    "script_id": "script-0002",
    "given_transcription": "The forest trail was blanketed in autumn leaves, their crunch underfoot a constant companion to the hikers exploring the serene path. The local farmers' market bustled with activity as vendors proudly displayed the fruits of their labor under colorful canopies. The village square came alive at dusk, children playing tag while parents chatted amiably, enjoying the cool evening breeze. In the art gallery, viewers moved from painting to painting, deeply engrossed in the stories that each brushstroke told. The community garden was a patchwork of vibrant colors and fragrances, where neighbors shared both seeds and stories under the afternoon sun. The moonlit beach was a haven for late-night wanderers, the waves whispering secrets to the shore under a star-studded sky. On the city rooftop, friends gathered for a sunset barbecue, the skyline offering a stunning backdrop to their laughter and conversations. The small, rustic cabin by the lake served as a perfect retreat for the writer, her only interruption the call of the loons. The school playground echoed with the joyful shouts of children during recess, a lively break from the day's lessons. The amateur astronomer set up his telescope in the backyard, the night sky a canvas for his passion and curiosity about the universe.",
    "name": "test test",
    "no_of_retries": 0
}



def test_necessary_payload_for_assessment():
    assert get_necessary_fields_from_payload(payload_1) == RequiredFieldsScriptReading(
        user_id=payload_1['user_id'],
        email=payload_1['email'],
        record_id=payload_1['record_id'],
        audio_url=payload_1['audio_url'],
        script_id=payload_1['script_id'],
        given_transcription=payload_1['given_transcription'],
        name=payload_1['name'],
        no_of_retries=payload_1['no_of_retries']
    )
    
    # user_id = payload['user_id']
    # email = payload['email']
    # record_id = payload['record_id']
    # audio_url = payload['audio_url']
    # script_id = payload['script_id']
    # given_transcription = payload['given_transcription']
    # name = payload['name']
    # no_of_retries = payload['no_of_retries']