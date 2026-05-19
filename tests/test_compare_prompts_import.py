from evaluator.compare_prompts import compare_prompts


def test_compare_prompts_exists():
    assert callable(compare_prompts)