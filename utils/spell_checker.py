from spellchecker import SpellChecker
import string # Import string module for punctuation characters

class SpellCheckerUtil:
    def __init__(self):
        self.spell = SpellChecker()

    def find_misspelled(self, text_content):
        """
        Finds misspelled words in the given text content.
        Returns a list of misspelled words.
        """
        words = text_content.lower().split()

        processed_words = []
        for word in words:
            cleaned_word = word.strip(string.punctuation)
            # Filter out empty strings or strings that were purely punctuation
            if cleaned_word:
                processed_words.append(cleaned_word)

        if not processed_words:
            return []

        misspelled_info = []
        # Using a set for unique words to check, as a word might be misspelled multiple times
        # Also, filter out any words that became empty after stripping all possible punctuation.
        unique_processed_words = sorted(list(set(p_word for p_word in processed_words if p_word)))


        for word in unique_processed_words:
            # Additional check: ensure the word itself is not just punctuation remains,
            # though strip(string.punctuation) should handle most cases.
            # An example could be a word like "---" if '-' is not in string.punctuation by default.
            # However, string.punctuation is quite comprehensive.
            if not word: # Skip if word became empty after aggressive stripping (should be rare now)
                continue

            # Check if the word is known or not by the spellchecker
            if not self.spell.correction(word) == word :
                 # correction() returns the word itself if it's known/correct.
                 # We are interested in words where correction() is different or it's unknown.
                 # The method `unknown` returns a set of words that are not in the dictionary.
                 # The method `candidates` returns a set of possible candidates for a given word.
                if word in self.spell.unknown([word]): # Double check it's unknown
                    suggestions = list(self.spell.candidates(word))
                    # Prioritize the direct correction if it's among candidates or valid
                    # direct_correction = self.spell.correction(word)
                    # if direct_correction and direct_correction != word:
                    #     if direct_correction in suggestions:
                    #         suggestions.remove(direct_correction)
                    #     suggestions.insert(0, direct_correction)
                    # else: # if no direct correction or it's same as word, ensure suggestions are reasonable
                    #     suggestions = list(self.spell.candidates(word)) if self.spell.candidates(word) else []
                    misspelled_info.append({"word": word, "suggestions": suggestions[:5]}) # Return top 5 suggestions

        return misspelled_info


if __name__ == '__main__':
    # Example Usage
    checker = SpellCheckerUtil()
    sample_text = "This is a sample text with some mispeled wrds. And anothr mispeled wrd."
    errors_info = checker.find_misspelled(sample_text)
    print(f"Misspelled words info: {errors_info}")

    for info in errors_info:
        print(f"Word: {info['word']}, Suggestions: {info['suggestions']}")

    sample_text_2 = "ths is anothr exampl with errrs. tst."
    errors_info_2 = checker.find_misspelled(sample_text_2)
    print(f"Misspelled words info in second sample: {errors_info_2}")
    for info in errors_info_2:
        print(f"Word: {info['word']}, Suggestions: {info['suggestions']}")

    sample_text_3 = "All words in this sentence are correctly spelled."
    errors_info_3 = checker.find_misspelled(sample_text_3)
    print(f"Misspelled words info in third sample (should be empty): {errors_info_3}")
