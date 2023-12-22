from queryguard.exceptions import RuleViolation


class TestExceptions:
    def test_rule_violation(self) -> None:
        try:
            raise RuleViolation("TestRule", "S001", "Test message")
        except RuleViolation as e:
            assert e.rule == "TestRule"
            assert e.id == "S001"
            assert e.__str__() == "TestRule (S001)"
