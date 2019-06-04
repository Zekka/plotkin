from enum import Enum
from typing import NamedTuple


class Trigger(Enum):
    # NOTE: instead/check/before are syntaxes for writing the same family of rules in my system
    Instead = "instead"
    Before = "before"
    Perform = "perform"
    After = "after"


class Rule(NamedTuple):
    chapter: str
    procedure: str


class Rulebook(object):
    def __init__(self, item_ref, outcome):
        self.ref = item_ref
        self.rules = {t.value: [] for t in Trigger}
        self._actions = []
        self.outcome = outcome

    # == PRIMITIVES ==
    def add(self, trigger: Trigger, chapter: str, procedure: str):
        assert isinstance(trigger, Trigger)
        assert isinstance(chapter, str)
        assert isinstance(procedure, str)

        dispatch = Rule(chapter, procedure)
        self.rules[trigger.value].append(dispatch)

    def add_action(self, lit):
        self._actions.append(lit)

    def codegen_metadata(self):
        cg_meta = {
            "ref": self.ref,
            "rules": {t: list(rs) for t, rs in self.rules.items()},
            "chapters": {},
            "actions": list(self._actions),
            "outcome": self.outcome,
        }

        for trigger, rules_for_trigger in self.rules.items():
            for rule in rules_for_trigger:
                chapter = cg_meta["chapters"].get(rule.chapter)
                if not chapter:
                    chapter = {
                        "name": rule.chapter,
                        "rules": {t.value: [] for t in Trigger},
                    }
                    cg_meta["chapters"][rule.chapter] = chapter

                chapter["rules"][trigger].append(rule)

        return cg_meta

    # == SHORTHAND ==
    def add_instead(self, chapter: str, procedure: str):
        self.add(Trigger.Instead, chapter, procedure)

    def add_before(self, chapter: str, procedure: str):
        self.add(Trigger.Before, chapter, procedure)

    def add_perform(self, chapter: str, procedure: str):
        self.add(Trigger.Perform, chapter, procedure)

    def add_after(self, chapter: str, procedure: str):
        self.add(Trigger.After, chapter, procedure)
