from starsep_utils import formatFileSize


def test_formatFileSize():
    assert formatFileSize(123) == "123B"
    assert formatFileSize(12345) == "12kB"
    assert formatFileSize(12345, precision=2) == "12.06kB"
    assert formatFileSize(123456789) == "118MB"
    assert formatFileSize(123456789, precision=2) == "117.74MB"
