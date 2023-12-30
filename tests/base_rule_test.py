import pytest

from queryguard.rules import BaseRule


class TestBaseRule:
    def test_abstract_base_class(self) -> None:
        with pytest.raises(TypeError):
            BaseRule()  # type: ignore[abstract]
