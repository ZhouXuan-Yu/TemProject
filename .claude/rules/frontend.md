# Frontend Rules

- Reuse existing components, design tokens, state patterns, and API clients before creating alternatives.
- Preserve accessibility, responsive behavior, and existing interaction semantics.
- Do not hardcode backend URLs, secrets, or environment-specific values.
- Keep business logic out of presentation components when an established service/domain layer exists.
- Avoid global state for local-only UI state.
- Handle loading, empty, error, and permission states explicitly for production-facing flows.
