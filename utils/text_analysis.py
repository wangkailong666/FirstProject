import re
import string

def parse_line_ranges(line_input_str, total_lines):
    """
    Parses a string of line numbers and ranges (1-indexed) into a sorted list of unique 0-indexed line numbers.
    Example input: "1-3,5,all,10-12", total_lines=20
    Output: [0, 1, 2, 4, 9, 10, 11] (and all lines if "all" is present)
    Raises ValueError for invalid formats or out-of-range numbers.
    """
    if not isinstance(total_lines, int) or total_lines < 0:
        raise ValueError("total_lines must be a non-negative integer.")

    if not line_input_str.strip():
        raise ValueError("Line input string cannot be empty.")

    target_lines_0_indexed = set()
    parts = line_input_str.split(',')

    for part in parts:
        part = part.strip().lower()
        if not part:
            continue # Skip empty parts resulting from multiple commas, e.g., "1,,2"

        if part == "all":
            if total_lines == 0: # No lines to add if document is empty
                continue
            for i in range(total_lines):
                target_lines_0_indexed.add(i)
            # If "all" is specified, no need to process other parts, as it covers everything.
            # However, the problem asks for unique lines, so processing others and adding to set is fine.
            # Let's assume "all" means all lines, and other numbers are just redundant if "all" is present.
            # For simplicity, if "all" is found, we can just return all lines.
            return sorted(list(range(total_lines)))


        if '-' in part: # Range
            try:
                start, end = map(int, part.split('-'))
                if not (1 <= start <= end <= total_lines):
                    raise ValueError(f"Invalid range '{part}': values out of bounds (1-{total_lines}). Start must be <= End.")
                for i in range(start - 1, end): # Convert to 0-indexed range
                    target_lines_0_indexed.add(i)
            except ValueError as e: # Catches non-integer parts in split, or if map fails
                if "out of bounds" in str(e): raise # Re-raise our specific error
                raise ValueError(f"Invalid range format: '{part}'. Must be 'start-end'.") from e
        else: # Single number
            try:
                line_num = int(part)
                if not (1 <= line_num <= total_lines):
                    if total_lines == 0 and line_num == 1: # Special case: user inputs '1' for an empty doc
                         raise ValueError(f"Invalid line number '{part}': document is empty.")
                    raise ValueError(f"Invalid line number '{part}': out of bounds (1-{total_lines}).")
                target_lines_0_indexed.add(line_num - 1) # Convert to 0-indexed
            except ValueError as e: # Catches non-integer part
                if "out of bounds" in str(e) or "document is empty" in str(e): raise
                raise ValueError(f"Invalid line number format: '{part}'. Must be an integer.") from e

    if not target_lines_0_indexed and total_lines > 0 : # Input was not empty, but no valid lines were parsed
        # This can happen if input is e.g., "abc" for a non-empty doc
        is_potentially_valid_non_numeric = any(p.isalpha() for p_component in parts for p in p_component.split('-'))
        if is_potentially_valid_non_numeric and not any(p == "all" for p in parts): # avoid double error if 'all' was there but doc was empty
             raise ValueError("No valid line numbers or 'all' keyword found in input.")


    return sorted(list(target_lines_0_indexed))


def find_space_around_period_anomalies(text_content):
    """
    Finds occurrences of " ." (space before period) and ". " (space after period).
    Returns a list of (start_index, end_index) tuples for each anomaly.
    Overlapping anomalies for " . " will be reported separately.
    Indices are character-based from the start of the text_content.
    """
    anomalies = []

    # Find " ." - space before period
    # Using regex to find occurrences and their positions
    # Pattern: a space followed by a literal period
    for match in re.finditer(r" \.", text_content):
        start_index, end_index = match.span()
        anomalies.append((start_index, end_index))

    # Find ". " - period followed by a space
    # Pattern: a literal period followed by a space
    for match in re.finditer(r"\. ", text_content):
        start_index, end_index = match.span()
        anomalies.append((start_index, end_index))

    # The problem description also mentioned iterating char by char.
    # The regex approach is generally more efficient for finding patterns.
    # Let's stick to the refined detection logic from the prompt for clarity if needed,
    # but re.finditer is quite good.
    # The prompt's refined logic:
    # Iterate char by char. If char is '.', check char before and char after.
    # If text[i] == '.':
    #     If i > 0 and text[i-1] == ' ': anomaly from i-1 to i+1 (for " .")
    #     If i < len(text)-1 and text[i+1] == ' ': anomaly from i to i+2 (for ". ")
    # This refined logic will find " ." as a 2-char anomaly and ". " as a 2-char anomaly.
    # " . " will yield (" .", from i-1 to i+1) and (". ", from i to i+2).
    # The regex approach finds these same 2-char anomalies.

    # Example: "test . com"
    # " ." is at index 4 (char ' '), period at 5. match.span() for " \." is (4, 6)
    # ". " is at index 5 (char '.'), space at 6. match.span() for "\. " is (5, 7)
    # This seems correct and matches the refined logic's output structure.

    # Sort anomalies by start index to process them in order if necessary,
    # though for highlighting, the order might not matter as much as applying all tags.
    anomalies.sort(key=lambda x: x[0])

    return anomalies

if __name__ == '__main__':
    test_cases = [
        ("No anomalies here.", []),
        ("This is a test .", [(15, 17)]), # " ."
        ("This is a test. Next sentence.", [(16, 18)]), # ". "
        ("This is a test . Next sentence.", [(15, 17), (16, 18)]), # " . "
        (" .period at start", [(0, 2)]),
        ("period at end. ", [(14,16)]),
        ("multiple . spaces . like . this.", [(9,11), (10,12), (18,20), (19,21), (25,27), (26,28)]),
        ("test. .test", [(4,6), (5,7)]), # ". ."
        ("test . . test", [(4,6), (6,8), (7,9)]), # " . . "
        ("Hello world . How are you . Doing good.", [(11,13), (12,14), (26,28), (27,29)])
    ]

    for i, (text, expected) in enumerate(test_cases):
        result = find_space_around_period_anomalies(text)
        print(f"Test Case {i+1}: '{text}'")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        assert result == expected, f"Test Case {i+1} Failed!"
        print("-" * 20)

    print("All basic tests passed.")


if __name__ == '__main__':
    # Tests for parse_line_ranges
    print("\nTesting parse_line_ranges:")
    range_test_cases = [
        ("1-3,5", 5, [0, 1, 2, 4]),
        ("all", 5, [0, 1, 2, 3, 4]),
        ("all", 0, []),
        ("1,3,2", 3, [0, 1, 2]),
        (" 2 - 4 , 1 ", 5, [0, 1, 2, 3]),
        ("", 5, ValueError("Line input string cannot be empty.")),
        ("1-3,abc", 5, ValueError("Invalid line number format: 'abc'. Must be an integer.")),
        ("1-5,3-6", 5, ValueError("Invalid range '3-6': values out of bounds (1-5). Start must be <= End.")),
        ("0-2", 5, ValueError("Invalid range '0-2': values out of bounds (1-5). Start must be <= End.")),
        ("10", 5, ValueError("Invalid line number '10': out of bounds (1-5).")),
        ("1", 0, ValueError("Invalid line number '1': document is empty.")),
        ("2-1", 5, ValueError("Invalid range '2-1': values out of bounds (1-5). Start must be <= End.")), # Start > End
        ("some-text", 5, ValueError("Invalid range format: 'some-text'. Must be 'start-end'.")),
        ("1-3, 1-2", 5, [0,1,2]), # Overlapping ranges, duplicates handled by set
        ("5, 1, 3", 5, [0,2,4]),
        (" , 1 , ,, 2-3, ", 5, [0,1,2]), # Empty parts, extra spaces
        ("all, 1-2", 3, [0,1,2]), # "all" should dominate
        ("invalid", 3, ValueError("No valid line numbers or 'all' keyword found in input."))
    ]

    for i, (line_str, total_ln, expected) in enumerate(range_test_cases):
        print(f"Range Test Case {i+1}: line_str='{line_str}', total_lines={total_ln}")
        try:
            result = parse_line_ranges(line_str, total_ln)
            print(f"  Expected: {expected}, Got: {result}")
            assert result == expected, f"Range Test Case {i+1} FAILED."
        except ValueError as e:
            print(f"  Expected ValueError: '{type(expected)==type(e) and str(expected) == str(e)}', Got ValueError: '{e}'")
            if isinstance(expected, ValueError):
                assert str(e) == str(expected), f"Range Test Case {i+1} FAILED. Expected error: '{expected}', Got: '{e}'"
            else: # Unexpected ValueError
                raise AssertionError(f"Range Test Case {i+1} FAILED. Expected result {expected}, but got ValueError: '{e}'")
        except Exception as e:
             raise AssertionError(f"Range Test Case {i+1} FAILED with unexpected exception {type(e)}: {e}. Expected: {expected}")
        print("-" * 20)
    print("All parse_line_ranges tests completed.")
