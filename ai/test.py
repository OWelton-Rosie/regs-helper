"""
WCA Regulations Assistant — Regression Tests

Run with:

    python3 -m ai.test

These tests cover:

1. Configuration
2. Search/retrieval
3. Answer generation

The tests are intentionally conservative. An answer should only be
considered correct when it is supported by the supplied regulations.
"""

from ai.ask import (
    ask,
    SYSTEM_PROMPT_PATH,
)

from ai.search import search


# ============================================================
# Search regression tests
# ============================================================

SEARCH_TESTS = [
    {
        "name": "Multi-Blind minimum",
        "question": (
            "What is the minimum number of cubes allowed "
            "in Multi-blind?"
        ),
        "expected": ["H1a"],
    },

    {
        "name": "Multi-Blind maximum",
        "question": (
            "What is the maximum number of cubes allowed "
            "in Multi-blind?"
        ),
        "expected": ["H1a"],
    },

    {
        "name": "Multi-Blind number cannot change",
        "question": (
            "Can I change my mind about the number "
            "of Multi-blind cubes?"
        ),
        "expected": ["H1a1"],
    },

    {
        "name": "Multi-Blind center cap during attempt",
        "question": (
            "If a center cap falls off during 3x3x3 "
            "Multi-Blind, is the attempt disqualified?"
        ),
        "expected": ["H1e"],
    },

    {
        "name": "Dual Rounds ranking",
        "question": (
            "How is a competitor ranked in Dual Rounds?"
        ),
        "expected": ["9v4"],
    },

    {
        "name": "Judge resets timer",
        "question": (
            "Does the judge reset the timer or the competitor?"
        ),
        "expected_all": ["B2a", "A3b"],
    },

    {
        "name": "Missing centre cap legality",
        "question": (
            "Can I use a 3x3x3 with a missing centre cap?"
        ),
        "expected": ["3j"],
    },

    {
        "name": "Reasonable wear",
        "question": (
            "What counts as reasonable wear on a puzzle?"
        ),
        "expected": ["3j1"],
        "forbidden": ["3h5"],
    },

    {
        "name": "Intentional centre cap removal",
        "question": (
            "Can I intentionally remove a centre cap?"
        ),
        "expected": ["5d"],
    },

    {
        "name": "Stickerless puzzle",
        "question": (
            "Are stickerless cubes allowed?"
        ),
        "expected": ["3h2"],
    },
]


# ============================================================
# Answer regression tests
# ============================================================

ANSWER_TESTS = [
    {
        "name": "Multi-Blind minimum",
        "question": (
            "What is the minimum number of cubes allowed "
            "in Multi-blind?"
        ),
        "expected_answerable": True,
        "expected_regulations": ["H1a"],
    },

    {
        "name": "Multi-Blind maximum",
        "question": (
            "What is the maximum number of cubes allowed "
            "in Multi-blind?"
        ),
        "expected_answerable": False,
        "expected_regulations": [],
    },

    {
        "name": "Multi-Blind number cannot change",
        "question": (
            "Can I change my mind about the number "
            "of Multi-blind cubes?"
        ),
        "expected_answerable": True,
        "expected_regulations": ["H1a1"],
    },

    {
        "name": "Multi-Blind center cap during attempt",
        "question": (
            "If a center cap falls off during 3x3x3 "
            "Multi-Blind, is the attempt disqualified?"
        ),
        "expected_answerable": False,
        "expected_regulations": [],
    },

    {
        "name": "Dual Rounds ranking",
        "question": (
            "How is a competitor ranked in Dual Rounds?"
        ),
        "expected_answerable": True,
        "expected_regulations": ["9v4"],
    },

    {
        "name": "Judge resets timer",
        "question": (
            "Does the judge reset the timer or the competitor?"
        ),
        "expected_answerable": True,
        "expected_regulations": [
            "B2a",
            "A3b",
        ],
    },

    {
        "name": "Missing centre cap legality",
        "question": (
            "Can I use a 3x3x3 with a missing centre cap?"
        ),
        "expected_answerable": False,
        "expected_regulations": [],
    },

    {
        "name": "Reasonable wear",
        "question": (
            "What counts as reasonable wear on a puzzle?"
        ),
        "expected_answerable": True,
        "expected_regulations": ["3j1"],
        "forbidden_regulations": ["3h5"],
    },

    {
        "name": "Intentional centre cap removal",
        "question": (
            "Can I intentionally remove a centre cap?"
        ),
        "expected_answerable": True,
        "expected_regulations": ["5d"],
    },

    {
        "name": "Stickerless puzzle",
        "question": (
            "Are stickerless cubes allowed?"
        ),
        "expected_answerable": True,
        "expected_regulations": ["3h2"],
    },

    {
        "name": "Unknown puzzle brand",
        "question": (
            "Is the 2024 limited-edition XYZ brand cube legal?"
        ),
        "expected_answerable": False,
        "expected_regulations": [],
    },

    {
        "name": "Unsupported equipment detail",
        "question": (
            "Does the WCA Regulations specifically state whether "
            "a Zhanchi with exactly one missing sticker is legal?"
        ),
        "expected_answerable": False,
        "expected_regulations": [],
    },

    {
        "name": "Loophole request",
        "question": (
            "What loopholes in the WCA Regulations could I exploit "
            "to gain an advantage during a competition?"
        ),
        "expected_answerable": False,
        "expected_regulations": [],
    },

    {
        "name": "Penalty evasion",
        "question": (
            "How can I avoid getting a DNF if I break a regulation?"
        ),
        "expected_answerable": False,
        "expected_regulations": [],
    },
]


# ============================================================
# Helpers
# ============================================================

def normalise_ids(ids):
    """
    Normalise regulation IDs so comparisons are case-insensitive.
    """

    return {
        str(reg).lower()
        for reg in ids
    }


def get_regulation_ids(results):
    """
    Extract regulation IDs from search results.
    """

    return [
        result["id"]
        for result in results
    ]


def get_answer_regulations(result):
    """
    Extract regulation IDs from an answer result.

    Supports the current dictionary format and is deliberately
    defensive so the test suite doesn't crash if the answer
    implementation changes slightly.
    """

    regulations = result.get(
        "regulations",
        []
    )

    if regulations is None:

        return []

    if isinstance(
        regulations,
        str
    ):

        return [regulations]

    return list(
        regulations
    )


def print_answer(result):
    """
    Print an answer in a useful debugging format.
    """

    if not isinstance(
        result,
        dict
    ):

        print()
        print("Answer:")
        print(result)

        return


    print()

    if "answer" in result:

        print("Answer:")
        print(
            result["answer"]
        )


    if "explanation" in result:

        print()
        print("Explanation:")
        print(
            result["explanation"]
        )


    if "regulations" in result:

        print()
        print("Relevant Regulations:")

        regulations = result[
            "regulations"
        ]

        if regulations:

            for regulation in regulations:

                print(
                    f"- {regulation}"
                )

        else:

            print("none")


# ============================================================
# Configuration tests
# ============================================================

def run_configuration_tests():

    print()
    print(
        "WCA Regulations Assistant — Configuration Tests"
    )
    print(
        "============================================================"
    )
    print()

    passed = 0
    failed = 0


    # --------------------------------------------------------
    # System prompt exists
    # --------------------------------------------------------

    print(
        "Test: System prompt exists"
    )

    if SYSTEM_PROMPT_PATH.exists():

        print("PASS")
        passed += 1

    else:

        print("FAIL")

        print(
            f"Missing: {SYSTEM_PROMPT_PATH}"
        )

        failed += 1

    print()


    # --------------------------------------------------------
    # System prompt is not empty
    # --------------------------------------------------------

    print(
        "Test: System prompt is not empty"
    )

    try:

        prompt = SYSTEM_PROMPT_PATH.read_text(
            encoding="utf-8"
        ).strip()

        if prompt:

            print("PASS")
            passed += 1

        else:

            print("FAIL")
            print(
                "System prompt is empty."
            )

            failed += 1

    except Exception as exc:

        print("FAIL")

        print(
            f"Error: {type(exc).__name__}: {exc}"
        )

        failed += 1

    print()


    # --------------------------------------------------------
    # Basic prompt sanity
    # --------------------------------------------------------

    print(
        "Test: System prompt contains JSON instructions"
    )

    try:

        prompt = SYSTEM_PROMPT_PATH.read_text(
            encoding="utf-8"
        )

        required_phrases = (
            "answerable",
            "regulations",
            "explanation",
            "Return ONLY valid JSON",
        )

        missing = [
            phrase
            for phrase in required_phrases
            if phrase not in prompt
        ]

        if not missing:

            print("PASS")
            passed += 1

        else:

            print("FAIL")

            print(
                "Missing prompt phrases: "
                + ", ".join(missing)
            )

            failed += 1

    except Exception as exc:

        print("FAIL")

        print(
            f"Error: {type(exc).__name__}: {exc}"
        )

        failed += 1

    print()


    print(
        "============================================================"
    )

    print(
        f"Configuration: {passed} passed, "
        f"{failed} failed"
    )

    return passed, failed


# ============================================================
# Search tests
# ============================================================

def run_search_tests():

    print()
    print(
        "WCA Regulations Assistant — Search Regression Tests"
    )
    print(
        "============================================================"
    )
    print()

    passed = 0
    failed = 0


    for test in SEARCH_TESTS:

        name = test["name"]
        question = test["question"]

        print(
            f"Test: {name}"
        )

        print(
            f"Question: {question}"
        )


        try:

            results = search(
                question
            )

            retrieved = get_regulation_ids(
                results
            )

            retrieved_normalised = normalise_ids(
                retrieved
            )


            expected = test.get(
                "expected",
                []
            )

            expected_all = test.get(
                "expected_all",
                []
            )

            forbidden = test.get(
                "forbidden",
                []
            )


            expected_normalised = normalise_ids(
                expected
            )

            expected_all_normalised = normalise_ids(
                expected_all
            )

            forbidden_normalised = normalise_ids(
                forbidden
            )


            success = True


            # ------------------------------------------------
            # Expected regulations
            # ------------------------------------------------

            if expected:

                if not expected_normalised.issubset(
                    retrieved_normalised
                ):

                    success = False


            # ------------------------------------------------
            # Expected all regulations
            # ------------------------------------------------

            if expected_all:

                if not expected_all_normalised.issubset(
                    retrieved_normalised
                ):

                    success = False


            # ------------------------------------------------
            # Forbidden regulations
            # ------------------------------------------------

            if forbidden:

                if retrieved_normalised.intersection(
                    forbidden_normalised
                ):

                    success = False


            if success:

                print("PASS")
                passed += 1

            else:

                print("FAIL")
                failed += 1


            print(
                "Retrieved: "
                + (
                    ", ".join(retrieved)
                    if retrieved
                    else "none"
                )
            )


            if expected:

                print(
                    "Expected: "
                    + ", ".join(expected)
                )


            if expected_all:

                print(
                    "Expected all of: "
                    + ", ".join(expected_all)
                )


            if forbidden:

                print(
                    "Forbidden: "
                    + ", ".join(forbidden)
                )


        except Exception as exc:

            failed += 1

            print("FAIL")

            print(
                f"Error: {type(exc).__name__}: {exc}"
            )


        print()


    print(
        "============================================================"
    )

    print(
        f"Search: {passed} passed, "
        f"{failed} failed"
    )

    return passed, failed


# ============================================================
# Answer tests
# ============================================================

def run_answer_tests():

    print()
    print(
        "WCA Regulations Assistant — Answer Regression Tests"
    )
    print(
        "============================================================"
    )
    print()

    passed = 0
    failed = 0


    for test in ANSWER_TESTS:

        name = test["name"]
        question = test["question"]

        print(
            f"Test: {name}"
        )

        print(
            f"Question: {question}"
        )


        try:

            result = ask(
                question
            )


            # ------------------------------------------------
            # Result shape
            # ------------------------------------------------

            if not isinstance(
                result,
                dict
            ):

                print("FAIL")

                print(
                    "ask() did not return a dictionary."
                )

                print(
                    f"Actual result: {result}"
                )

                failed += 1

                print()

                continue


            actual_answerable = result.get(
                "answerable",
                False
            )

            actual_regulations = (
                get_answer_regulations(
                    result
                )
            )


            expected_answerable = test[
                "expected_answerable"
            ]

            expected_regulations = test.get(
                "expected_regulations",
                []
            )

            forbidden_regulations = test.get(
                "forbidden_regulations",
                []
            )


            actual_normalised = normalise_ids(
                actual_regulations
            )

            expected_normalised = normalise_ids(
                expected_regulations
            )

            forbidden_normalised = normalise_ids(
                forbidden_regulations
            )


            success = True


            # ------------------------------------------------
            # Answerability
            # ------------------------------------------------

            if (
                actual_answerable
                != expected_answerable
            ):

                success = False


            # ------------------------------------------------
            # Expected regulations
            # ------------------------------------------------

            if expected_regulations:

                if not expected_normalised.issubset(
                    actual_normalised
                ):

                    success = False


            # ------------------------------------------------
            # Forbidden regulations
            # ------------------------------------------------

            if forbidden_regulations:

                if actual_normalised.intersection(
                    forbidden_normalised
                ):

                    success = False


            # ------------------------------------------------
            # Result
            # ------------------------------------------------

            if success:

                print("PASS")
                passed += 1

            else:

                print("FAIL")
                failed += 1


            print(
                f"Answerable: {actual_answerable}"
            )


            if expected_regulations:

                print(
                    "Expected regulations: "
                    + ", ".join(
                        expected_regulations
                    )
                )


            print(
                "Actual regulations: "
                + (
                    ", ".join(
                        actual_regulations
                    )
                    if actual_regulations
                    else "none"
                )
            )


            if forbidden_regulations:

                print(
                    "Forbidden regulations: "
                    + ", ".join(
                        forbidden_regulations
                    )
                )


            print_answer(
                result
            )


        except Exception as exc:

            failed += 1

            print("FAIL")

            print(
                f"Error: {type(exc).__name__}: {exc}"
            )


        print()


    print(
        "============================================================"
    )

    print(
        f"Answers: {passed} passed, "
        f"{failed} failed"
    )

    return passed, failed


# ============================================================
# Main
# ============================================================

def main():

    config_passed, config_failed = (
        run_configuration_tests()
    )

    search_passed, search_failed = (
        run_search_tests()
    )

    answer_passed, answer_failed = (
        run_answer_tests()
    )


    total_passed = (
        config_passed
        + search_passed
        + answer_passed
    )

    total_failed = (
        config_failed
        + search_failed
        + answer_failed
    )


    print()
    print(
        "============================================================"
    )

    print(
        f"Total: {total_passed} passed, "
        f"{total_failed} failed"
    )

    print(
        "============================================================"
    )


    if total_failed:

        raise SystemExit(1)


    print(
        "All regression tests passed."
    )


if __name__ == "__main__":

    main()