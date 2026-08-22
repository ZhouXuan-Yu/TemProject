# Backend Rules

- Preserve existing module and dependency boundaries.
- Validate external input at trust boundaries.
- Keep authorization checks close to protected operations.
- Do not expose internal exceptions or sensitive implementation details to clients.
- Use established service/repository patterns before introducing new abstractions.
- Keep API contract changes backward compatible unless explicitly approved.
- Use transactions where multi-step state changes must be atomic.
