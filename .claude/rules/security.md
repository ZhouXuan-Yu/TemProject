# Security Rules

Never:

- commit secrets
- expose API keys
- bypass RBAC or authorization checks
- disable authentication
- return password hashes
- log authentication tokens
- expose internal stack traces to clients
- weaken validation merely to make tests pass

Sensitive configuration must use environment variables or approved secret management.
