import unittest
from utils.spell_checker import SpellCheckerUtil

class TestSpellCheckerUtil(unittest.TestCase):

    def setUp(self):
        self.checker = SpellCheckerUtil()

    def test_find_misspelled_with_errors_and_suggestions(self):
        text = "This is a smple txt with mispeled wrds."
        # Expected words might vary slightly based on the dictionary version/language setting.
        # We are checking if it finds known misspellings and provides suggestions.
        results = self.checker.find_misspelled(text)

        misspelled_words_found = [item["word"] for item in results]

        self.assertIn("smple", misspelled_words_found)
        self.assertIn("txt", misspelled_words_found) # Often considered a word, but can be 'misspelled' by some checkers
        self.assertIn("mispeled", misspelled_words_found)
        self.assertIn("wrds", misspelled_words_found)

        for item in results:
            if item["word"] == "smple":
                self.assertTrue(len(item["suggestions"]) > 0, "Suggestions should be found for 'smple'")
            if item["word"] == "mispeled":
                self.assertTrue(len(item["suggestions"]) > 0, "Suggestions should be found for 'mispeled'")
                # Example: self.assertIn("misspelled", item["suggestions"]) # This is too specific

    def test_find_misspelled_no_errors(self):
        text = "This is a sample text with correctly spelled words."
        results = self.checker.find_misspelled(text)
        self.assertEqual(len(results), 0, "Should find no misspelled words")

    def test_find_misspelled_with_punctuation(self):
        text = "Hello, wrld! This is a tst."
        results = self.checker.find_misspelled(text)
        misspelled_words_found = [item["word"] for item in results]

        self.assertIn("wrld", misspelled_words_found)
        self.assertIn("tst", misspelled_words_found)

        for item in results:
            if item["word"] == "wrld":
                self.assertTrue(len(item["suggestions"]) > 0)

    def test_find_misspelled_empty_string(self):
        text = ""
        results = self.checker.find_misspelled(text)
        self.assertEqual(len(results), 0)

    def test_find_misspelled_only_punctuation(self):
        text = "!!! ,, ."
        results = self.checker.find_misspelled(text)
        self.assertEqual(len(results), 0)

    def test_find_misspelled_numbers(self):
        text = "123 4567 890" # Numbers are not misspelled
        results = self.checker.find_misspelled(text)
        self.assertEqual(len(results), 0)

    def test_find_misspelled_mixed_case(self):
        text = "Ths is a MiSpelEd word."
        results = self.checker.find_misspelled(text)
        misspelled_words_found = [item["word"] for item in results]
        # pyspellchecker typically works with lowercase
        self.assertIn("ths", misspelled_words_found)
        self.assertIn("mispeled", misspelled_words_found) # Corrected: "MiSpelEd" -> "mispeled"

        # A more robust test might need to check for "mispeled" after cleaning.
        # The current spell_checker.py implementation does text.lower().split()
        # and then word.strip() for punctuation.
        # If "MiSpelEd" is split into "mispel" and "ed", then the behavior is as expected.
        # Let's check the actual output of the current spell_checker for "MiSpelEd"
        # If it splits "MiSpelEd" into "mispel" and "ed", and "ed" is a word, then "mispel" would be the misspelling.
        # The current `find_misspelled` does `text_content.lower().split()`,
        # then `cleaned_words = [word.strip('.,!?;:"\'()[]{}') for word in words]`
        # So "MiSpelEd" -> "mispeled" -> "mispeled" (if no punctuation)
        # Let's refine the test based on this.
        text_refined = "Ths is a MiSpelLed word." # Using a more common misspelling
        results_refined = self.checker.find_misspelled(text_refined)
        misspelled_words_found_refined = [item["word"] for item in results_refined]
        self.assertIn("ths", misspelled_words_found_refined)
        self.assertIn("mispelled", misspelled_words_found_refined) # pyspellchecker should handle this

if __name__ == '__main__':
    unittest.main()
