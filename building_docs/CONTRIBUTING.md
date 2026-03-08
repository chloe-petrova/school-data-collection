# CONTRIBUTING.md

Guidelines for Claude Code when working in this repository.

## Audience

The user is not a developer. Do not assume familiarity with programming concepts, tooling, or terminology. When explaining what you are doing or why, use plain English. If a technical term is unavoidable, briefly define it in context. Prefer showing concrete examples over abstract descriptions.

## Commits

Never add co-author attribution or "Generated with Claude Code" footers to commit messages. Commit messages should be plain and descriptive — written as if the user wrote them.

## Task tracking

Use `TodoWrite` to track progress whenever you are working on a multi-step task. Mark each item done as soon as it is complete, not in a batch at the end. This keeps the user informed of where things stand without them having to ask.

## Test-driven development

When implementing logic that can be tested (database queries, data parsing, tool behaviour), follow the red-green-refactor cycle:
1. **Red** — write a failing test first that describes the expected behaviour
2. **Green** — write the minimum code needed to make it pass
3. **Refactor** — clean up without changing behaviour, keeping tests green

Apply TDD where it adds value. Don't write tests for boilerplate or configuration that cannot meaningfully fail.

## Completing a ticket

When a ticket's acceptance criteria are met:
1. Update the ticket file's `**Status**` field from `todo` to `done`.
2. Update the status column in `building_docs/tickets_index.md` to match.
3. Stop and ask the user whether they want to commit before moving on. Do not auto-commit or assume they want to proceed.
4. After the commit, create `building_docs/prompts/ticket-{next number}-prompt.md` for the next ticket (see format below).

## Prompt file format

`building_docs/prompts/ticket-{N}-prompt.md` is a short starter prompt for the next Claude Code session. Keep it to 10 lines or fewer:

```
Verify `building_docs/tickets/TICKET-{N-1}.md` has **Status**: done before proceeding.
Read `building_docs/tickets/TICKET-{N}.md` in full.
Use `TodoWrite` to track every step. Mark each item done immediately — never batch completions.
Follow all guidelines in `building_docs/CONTRIBUTING.md`.
When acceptance criteria are met, update the ticket status and index, then stop and ask before committing.
```

## Accuracy

Never state something as fact unless it is grounded in the codebase, the documentation in this repo, or verified behaviour. If you are uncertain, say so. Do not fill gaps with plausible-sounding guesses.

## No positive validation

Do not tell the user their idea was good, smart, or well-structured. They do not need reassurance — just get on with the work.
