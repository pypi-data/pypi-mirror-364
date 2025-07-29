import textwrap
from typing import override

from commitizen.cz.conventional_commits.conventional_commits import (
    ConventionalCommitsCz,
)
from commitizen.defaults import Questions

# How long a line of the body or footer should be before wrapping.
TEXT_WIDTH = 72


class ExtendedConventionalCz(ConventionalCommitsCz):
    @override
    def questions(self) -> Questions:
        questions = list(super().questions())
        prefix_question = questions[0]
        assert (
            prefix_question["name"] == "prefix"
        ), "Expected the first question to be 'prefix'"
        prefix_question["choices"] += [
            {
                "value": "deps",
                "name": "deps: Dependency updates that do not change the behavior; use feat "
                + "changes that cause user-facing changes.",
                "key": "e",
            },
            {
                "value": "chore",
                "name": "chore: General maintenance tasks that do not change the "
                + "behavior",
                "key": "o",
            },
        ]
        return questions

    @override
    def message(self, answers: dict[str, str]) -> str:
        def fill(text):
            return textwrap.fill(text, width=TEXT_WIDTH, break_on_hyphens=False)

        prefix = answers["prefix"]
        scope = answers["scope"]
        subject = answers["subject"]
        body = answers["body"]
        footer = answers["footer"]
        is_breaking_change = answers["is_breaking_change"]

        if scope:
            scope = f"({scope})"
        if body:
            body = f"\n\n{fill(body)}"
        if is_breaking_change:
            footer = f"BREAKING CHANGE: {footer}"
        if footer:
            footer = f"\n\n{fill(footer)}"

        message = f"{prefix}{scope}: {subject}{body}{footer}"

        return message

    @override
    def schema_pattern(self) -> str:
        PATTERN = (
            r"(?s)"  # To explicitly make . match new line
            r"(build|chore|ci|deps|docs|feat|fix|perf|refactor|style|test|revert|bump)"  # type
            r"(\(\S+\))?!?:"  # scope
            r"( [^\n\r]+)"  # subject
            r"((\n\n.*)|(\s*))?$"
        )
        return PATTERN
