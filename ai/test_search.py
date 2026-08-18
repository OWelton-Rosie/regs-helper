# Run with:
# python3 -m ai.test_search


from ai.search import search


# -------------------------
# Regression test cases
# -------------------------

TEST_CASES = [
    {
        "name": "Multi-Blind minimum",
        "question": "What is the minimum number of cubes allowed in Multi-blind?",
        "expected": ["H1a"],
    },
    {
        "name": "Multi-Blind maximum",
        "question": "What is the maximum number of cubes allowed in Multi-blind?",
        "expected": ["H1a"],
    },
    {
        "name": "Multi-Blind number cannot change",
        "question": "Can I change my mind about the number of Multi-blind cubes?",
        "expected": ["H1a1"],
    },
    {
        "name": "Multi-Blind center cap",
        "question": (
            "If a center cap falls off during 3x3x3 Multi-Blind, "
            "is the attempt disqualified?"
        ),
        "expected": ["H1e"],
    },
    {
        "name": "Dual Rounds tiebreaker",
        "question": "What is the tie breaker method for dual rounds?",
        "expected": ["9v", "9v4"],
    },
    {
        "name": "Judge resets timer",
        "question": "Does the judge reset the timer or the competitor?",
        "expected": ["B2a", "A3b"],
    }
]


# -------------------------
# Run tests
# -------------------------

passed = 0
failed = 0


print()
print("WCA Regulations Assistant — Search Regression Tests")
print("=" * 60)


for test in TEST_CASES:

    print()
    print(f"Test: {test['name']}")
    print(f"Question: {test['question']}")

    try:
        results = search(
            test["question"],
            top_k=5
        )

        result_ids = [
            result["id"]
            for result in results
        ]

        found = [
            regulation
            for regulation in test["expected"]
            if regulation in result_ids
        ]

        if found:

            print("PASS")
            print(f"Retrieved: {', '.join(result_ids)}")
            print(f"Expected: {', '.join(test['expected'])}")

            passed += 1

        else:

            print("FAIL")
            print(f"Retrieved: {', '.join(result_ids)}")
            print(f"Expected one of: {', '.join(test['expected'])}")

            failed += 1

    except Exception as error:

        print("ERROR")
        print(error)

        failed += 1


# -------------------------
# Summary
# -------------------------

print()
print("=" * 60)
print(
    f"Results: {passed} passed, "
    f"{failed} failed"
)

if failed:
    raise SystemExit(1)

print("All search regression tests passed.")