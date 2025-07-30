"""Unit test linting module for enforcing testing best practices."""

import re


def check_test_code(code: str) -> list[str]:
    """Analyzes test code for general principle violations.

    This function takes a string of code as input and applies a series of
    heuristic checks to identify common anti-patterns in unit tests, such as
    branching logic, missing assertions, non-descriptive test names, and
    commented-out tests. The checks are designed to be language-agnostic.
    """
    violations = []

    # Rule 1: No branching logic
    # This is a heuristic and might have false positives/negatives depending on
    # the language. We look for common keywords for branching/looping.
    branching_keywords = r'\b(if|for|while|switch|else if|elif|case)\b'
    if re.search(branching_keywords, code, re.IGNORECASE):
        violations.append(
            'Branching logic found. Tests should be declarative and avoid control flow.'
        )

    # Rule 2: Presence of assertions
    # This is also a heuristic. We look for common assertion keywords.
    assertion_keywords = (
        r'\b(assert|expect|should|test\.assert|t\.ok|ok|equal|deepEqual|'
        r'strictEqual|notEqual|notDeepEqual|notStrictEqual|throws|doesNotThrow|'
        r'match|notMatch|contains|notContains|isTrue|isFalse|isNull|isNotNull|'
        r'isUndefined|isDefined)\b'
    )
    if not re.search(assertion_keywords, code, re.IGNORECASE):
        violations.append('No clear assertion found. Tests should verify outcomes with assertions.')

    # Rule 3: Descriptive test names (heuristic for function/method definitions)
    # This is a very general check. It assumes test functions/methods are defined
    # with 'test' in their name. And checks if the name is very short after 'test_'.
    test_name_pattern = r'(?:func|def|function|it|test)_(?P<name_after_test>[a-zA-Z_][a-zA-Z0-9_]*)'
    for match in re.finditer(test_name_pattern, code, re.IGNORECASE):
        test_name_suffix = match.group('name_after_test')
        # Simple heuristic: if the name after 'test_' is very short (e.g., 'a', '1')
        if len(test_name_suffix) < 3:  # e.g., allows 'test_abc' but flags 'test_a'
            violations.append(
                f"Test name '{match.group(0)}' is too short or not descriptive. "
                'Consider a more meaningful name.'
            )

    # Rule 4: No commented-out tests
    # This is language-agnostic as comments usually start with # or //
    commented_test_patterns = [
        r'^\s*#\s*(def|func|function|it|test)[\s_]',
        r'^\s*//\s*(def|func|function|it|test)[\s_]',
    ]
    for line in code.splitlines():
        for pattern in commented_test_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append(
                    f"Commented-out test found: '{line.strip()}'. Remove or uncomment."
                )
                break  # Only report once per line

    return violations
