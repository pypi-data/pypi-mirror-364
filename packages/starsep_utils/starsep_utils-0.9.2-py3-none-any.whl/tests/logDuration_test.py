import logging

from starsep_utils import logDuration


def test_logDuration(caplog):
    @logDuration
    def foo():
        pass

    with caplog.at_level(logging.INFO):
        foo()

    assert "s in foo" in caplog.text
