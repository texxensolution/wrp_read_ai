def get_total_word_correct(base_text: str, other_text: str):
    base_words = base_text.split(" ")
    other_text_words = other_text.split(" ")
    base_words_map = {}
    base_words_count = 0
    correct_word_count = 0

    for word in base_words:
        if word in base_words_map:
            base_words_map[word] += 1
        else:
            base_words_map[word] = 1
        base_words_count += 1
    
    for word in other_text_words:
        if word in base_words_map:
            if base_words_map[word] > 0:
                correct_word_count += 1
                base_words_map[word] -= 1
   
    return correct_word_count, base_words_count
