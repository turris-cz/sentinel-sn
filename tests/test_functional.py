import pytest

from turris_sentinel_template_box.template_box import add2


@pytest.mark.parametrize(
    ("input", "expected_count"),
    (
        (0, 2),
        (10, 12),
        (-6, -4),
    ),
)
def test_add_2(input, expected_count):
    assert add2(input) == expected_count
