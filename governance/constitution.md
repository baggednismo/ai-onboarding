# Constitution

These rules apply to all new development.

## MUST

- Keep this repository the canonical source of truth.
- Use Clean Architecture: keep domain rules independent of frameworks, transport, and persistence.
- Apply DRY to real duplicated business rules and workflows only.
- Prefer deep modules with narrow, stable interfaces.
- Use TDD: write the first useful test before implementation.
- Keep legacy changes surgical.

## DO NOT

- Add speculative abstractions.
- Leak infrastructure concerns into domain logic.
- Change unrelated code for compliance or style.
