from migration_kit.reconcile import compare_values


def test_compare_values():
    assert compare_values(10, 10, "0") is True
    assert compare_values(10, 12, "2") is True
    assert compare_values(10, 12, "1") is False
    assert compare_values("abc", "abc", "0") is True
    assert compare_values("abc", "abd", "0") is False
