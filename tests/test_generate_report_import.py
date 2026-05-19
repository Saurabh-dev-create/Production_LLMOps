from evaluator.generate_report import generate_markdown_report


def test_generate_markdown_report_exists():
    assert callable(generate_markdown_report)