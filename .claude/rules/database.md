# Database Rules

- All schema changes require migrations.
- Never directly modify production database schema.
- Never silently drop tables or columns.
- Destructive migrations require explicit approval.
- Preserve backward compatibility whenever possible.
- Use database transactions for multi-step atomic operations.
- Never expose database credentials in source code.
