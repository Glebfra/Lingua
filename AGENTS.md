# AGENTS.md

Project-wide instructions for AI coding agents working in this repository.

This document is the shared engineering contract for all agents. Follow it together
with the instructions in the active agent definition under `.opencode/agents/`.
If instructions conflict, follow the more restrictive rule and ask the project owner
when the conflict affects architecture, security, data integrity, or public API behavior.

---

## 1. Project Context

This repository contains a new Python backend built with Django and Django REST Framework.

The product domain and business requirements must be discovered from the project owner's
requirements and approved decisions. Do not invent domain entities, user roles, workflows,
tenant boundaries, or business rules.

### Initial technology direction

The expected default stack is:

- Python: a currently supported version selected when the project is initialized.
- Django.
- Django REST Framework.
- PostgreSQL for production-oriented relational persistence.
- `uv` for dependency and virtual-environment management.
- Ruff for formatting and linting.
- Pytest and `pytest-django` for automated tests.
- Pyright or mypy for static type checking.
- Docker and Docker Compose when reproducible containerized development is required.
- OpenAPI schema generation compatible with the selected DRF and Django versions.

These are defaults, not permission to install or upgrade packages automatically.
Inspect the repository first and get approval before making material dependency decisions.

---

## 2. Core Engineering Principles

1. **Understand before changing.** Inspect the relevant code, configuration, tests,
   repository state, and existing conventions before implementing a task.
2. **Do not invent requirements.** Ask when missing information changes data ownership,
   permissions, API contracts, persistence, or user-visible behavior.
3. **Prefer the simplest sufficient design.** Avoid speculative abstractions and
   infrastructure that do not solve a current requirement.
4. **Keep responsibilities explicit.** Separate HTTP concerns, application workflows,
   domain rules, and persistence concerns when the complexity justifies it.
5. **Preserve behavior.** Treat existing API contracts and persisted data as important
   compatibility boundaries.
6. **Make changes verifiable.** Add or update tests and run relevant checks.
7. **Optimize with evidence.** Measure before claiming performance improvements.
8. **Security is part of correctness.** Every endpoint and data access path must enforce
   appropriate authentication, authorization, and data isolation.
9. **Keep changes focused.** Do not modify unrelated files or reformat entire modules
   without a reason.
10. **Explain important decisions.** Record meaningful architectural decisions and
    non-obvious trade-offs.

---

## 3. Repository and Change Safety

Before editing:

- Inspect the repository structure and relevant files.
- Read this document and the active agent's instructions.
- Inspect `git status` and preserve all pre-existing user changes.
- Check the project's Python version, dependencies, settings, test configuration,
  and formatting/type-checking configuration.
- Identify whether the task changes a public API, database schema, security boundary,
  or deployment behavior.

Never do the following without explicit approval:

- Delete or overwrite user work.
- Run destructive commands or remove data.
- Rewrite Git history, force-push, commit, or push changes.
- Deploy to any environment.
- Run migrations against production.
- Change production infrastructure or incur cloud costs.
- Introduce a breaking API change.
- Perform an irreversible or potentially data-losing migration.
- Upgrade, remove, or replace important dependencies when the change has material impact.

Do not assume that a clean-looking working tree means there are no user-owned changes.
Review the actual diff before finishing.

---

## 4. Python Standards

### 4.1 Language and typing

- Use the Python version declared by the project.
- Do not use syntax or standard-library APIs newer than the configured minimum version.
- Add type annotations to public functions, methods, and important module-level interfaces.
- Prefer precise types over `Any`.
- If `Any` is necessary, keep its scope narrow and explain why.
- Use `Protocol` for structural interfaces when they clarify boundaries.
- Use generics when they improve correctness and reuse, not merely to make code look abstract.
- Prefer immutable data structures where practical.
- Avoid untyped dictionaries for stable structured data; use dataclasses, TypedDict,
  enums, or dedicated models where appropriate.
- Avoid unnecessary casts and `type: ignore`. If unavoidable, explain the reason and
  narrow the ignored expression.

### 4.2 Code style

- Follow PEP 8 and the repository's Ruff configuration.
- Use descriptive names and small, cohesive functions.
- Prefer early returns over deeply nested conditionals.
- Avoid boolean parameters when they make a function's behavior ambiguous.
- Avoid mutable default arguments.
- Do not catch broad exceptions unless the boundary can handle them meaningfully.
- Never silently swallow exceptions.
- Raise domain-appropriate exceptions and translate them at the appropriate application
  or API boundary.
- Do not use `print()` for application logging.
- Do not add comments that merely repeat the code. Explain intent, constraints, and
  non-obvious decisions.

### 4.3 Async code

- Do not introduce asynchronous code by default.
- Use async only when the framework integration and I/O workload justify it.
- Do not call blocking I/O from async execution paths without an appropriate strategy.
- Verify the async support and limitations of the selected Django/DRF versions and
  third-party libraries before relying on them.

---

## 5. Django and DRF Architecture

### 5.1 Django apps

- Organize code by business capability or bounded feature, not only by technical file type.
- Keep Django apps cohesive and give each app a clear responsibility.
- Avoid circular dependencies between apps.
- Do not create an app for every model or a generic `core` app containing unrelated logic.
- Shared modules must contain genuinely shared concepts, not code moved there merely
  because multiple modules import it.

### 5.2 HTTP/API layer

- Keep views and ViewSets focused on HTTP orchestration.
- Use serializers for input validation and output representation.
- Keep complex business workflows out of views, serializers, model signals, and
  `Model.save()` methods.
- Put non-trivial application workflows into explicit service/use-case functions or
  classes when that improves testability and clarity.
- Do not create service classes for trivial one-line operations without a real benefit.
- Use separate read and write serializers when their contracts or permissions differ.
- Validate untrusted input at the API boundary.
- Return appropriate HTTP status codes and consistent error structures.
- Do not expose internal model fields by default.
- Avoid hidden behavior in serializer hooks and signals.

### 5.3 Business logic

- Business rules must be explicit, testable, and independent of HTTP request details.
- Do not make domain logic depend directly on `request`, `Response`, or DRF serializer
  internals.
- Use transactions for multi-step operations that must be atomic.
- Consider race conditions and concurrent requests for operations involving balances,
  counters, inventory, unique claims, state transitions, or other shared resources.
- Enforce critical invariants in the database when possible, not only in Python validation.
- Do not duplicate the same business rule across serializers, views, and model methods.

### 5.4 QuerySets and ORM

- Filter querysets by the current user's access rights and relevant ownership boundaries.
- Use `select_related()` and `prefetch_related()` when they prevent unnecessary queries.
- Avoid evaluating querysets earlier than necessary.
- Avoid unbounded list endpoints; use pagination for collections.
- Use `bulk_create()` and `bulk_update()` only after considering skipped model hooks,
  signals, validation, and database behavior.
- Avoid raw SQL unless the ORM cannot express the operation clearly or efficiently.
  Parameterize all raw SQL values.
- Never build SQL by concatenating untrusted input.

### 5.5 API design

- Use resource-oriented, predictable URL patterns.
- Use consistent naming, filtering, pagination, ordering, and error conventions.
- Define authentication and permission behavior explicitly for every endpoint.
- Keep API schema/documentation aligned with actual serializer and view behavior.
- Treat response schemas as public contracts.
- Do not add API versioning automatically. Decide based on client and compatibility needs.
- Discuss breaking changes with the project owner before implementing them.
- Do not expose stack traces, internal exception messages, or sensitive implementation
  details in API responses.

---

## 6. Database and Migrations

- Use the database selected by the project owner; PostgreSQL is the default direction.
- Choose field types, nullability, uniqueness, deletion behavior, and indexes deliberately.
- Use `DecimalField` for monetary values; never use binary floating point for exact money.
- Use timezone-aware datetimes and the project's configured timezone policy.
- Add database constraints for invariants that must remain true under concurrent writes.
- Add indexes based on known query patterns and measured needs.
- Consider query plans and data volume before adding complex indexes.
- Generate schema changes through Django migrations.
- Never edit a migration that may already have been applied in a shared environment.
- Create a new migration to amend an existing schema.
- Data migrations should be safe, bounded, and reversible where practical.
- For large tables, consider lock duration, table rewrites, backfills, and deployment order.
- Do not run migrations against production without explicit approval.
- Before proposing a destructive migration, explain affected data and a recovery strategy.

---

## 7. Authentication, Authorization, and Multi-Tenancy

The authentication mechanism and tenancy model are product decisions. Do not assume JWT,
session authentication, OAuth, or multi-tenancy without requirements.

For every endpoint, determine:

- Is the endpoint public or authenticated?
- Which roles or permissions are required?
- Which objects can the current principal access?
- Can the caller change ownership, role, status, or other protected fields?
- Is access restricted by organization, tenant, workspace, or another boundary?
- Can related objects leak information through nested serializers or error responses?

Rules:

- Enforce permissions on the server.
- Do not rely on frontend visibility or client-side checks.
- Use queryset scoping and object-level checks where required.
- Prevent IDOR/BOLA vulnerabilities.
- Do not trust client-supplied ownership, privilege, role, or tenant identifiers.
- Test access denial as carefully as successful access.
- Keep authentication credentials and tokens out of logs and responses.

---

## 8. Security and Privacy

Treat all client input, uploaded files, external responses, and imported data as untrusted.

### Required security considerations

- Keep `SECRET_KEY`, database credentials, API tokens, and private keys outside source control.
- Use environment variables or a dedicated secret manager.
- Keep `.env` out of Git; provide `.env.example` with placeholders only.
- Production must not run with `DEBUG=True`.
- Configure `ALLOWED_HOSTS` explicitly.
- Configure HTTPS, secure cookies, CSRF, CORS, and trusted origins according to deployment
  architecture. Do not use permissive wildcard settings as a shortcut.
- Use Django's password hashing and established authentication mechanisms.
- Validate and constrain uploaded file size, type, storage location, and access.
- Protect outbound requests against SSRF where user-controlled URLs are involved.
- Avoid unsafe deserialization and dynamic code execution.
- Avoid logging passwords, tokens, session identifiers, secrets, or sensitive personal data.
- Return generic external errors while keeping safe diagnostic details in internal logs.
- Review dependency security and maintenance status when adding packages.

Do not claim that an application is secure or OWASP-compliant based only on automated
checks or a limited code review.

---

## 9. Testing and Quality Gates

### 9.1 Test levels

Use the project's configured test framework. The expected default is Pytest with
`pytest-django`.

- **Unit tests:** isolated business rules and pure functions.
- **Integration tests:** interactions with Django models, database, and services.
- **API tests:** request/response behavior, validation, authentication, and permissions.
- **Regression tests:** previously fixed defects and important edge cases.

### 9.2 Test expectations

For a changed API feature, consider:

- Successful requests and response structure.
- Missing, malformed, and boundary input.
- Authentication failures.
- Permission failures.
- Object ownership and tenant isolation.
- Not-found behavior.
- Database constraints and transaction behavior.
- Pagination and filtering behavior where relevant.
- Side effects and state transitions.
- Duplicate requests and concurrency where relevant.

### 9.3 Test rules

- Test observable behavior, not private implementation details.
- Keep tests deterministic and independent.
- Use factories or fixtures consistently.
- Do not use production data or credentials.
- Do not weaken, skip, or delete a failing test just to obtain a green suite.
- Mock external systems at clear boundaries; do not mock the behavior under test.
- Run focused tests first, then broader checks when feasible.
- Report environment failures separately from code failures.
- Never claim that tests passed unless they were actually executed and the result was observed.

### 9.4 Quality checks

Use the checks configured in the repository. Typical checks include:

- Ruff formatting check.
- Ruff lint.
- Static type checking.
- Django system checks.
- Migration consistency check.
- Pytest suite.
- OpenAPI schema validation, if configured.

Do not invent command names. Inspect `pyproject.toml`, CI configuration, and project scripts
to determine the actual commands.

---

## 10. Performance and Reliability

- Avoid optimizing code without identifying a bottleneck.
- Check query counts and query plans for database-heavy endpoints.
- Prevent N+1 queries and unbounded data loading.
- Use pagination and enforce reasonable request/response sizes.
- Consider timeouts and failure handling for external services.
- Use retries only when operations are safe to retry or idempotency is guaranteed.
- Use caching only with a clear invalidation and consistency strategy.
- Do not introduce Celery, Redis, message brokers, or distributed systems without a
  requirement that justifies their operational complexity.
- For background work, define retry, idempotency, observability, and failure semantics.
- Do not claim a performance improvement without measurement.

---

## 11. Dependencies and Configuration

- Use `uv` unless the project owner chooses another tool.
- Keep dependency declarations in `pyproject.toml` and the lockfile consistent.
- Separate runtime dependencies from development dependencies.
- Do not add a package for functionality already provided adequately by the standard
  library or existing project dependencies.
- Before adding a dependency, explain its purpose, maintenance status, license concerns
  where relevant, and alternatives.
- Do not upgrade dependencies as unrelated cleanup.
- Keep settings explicit and environment-aware.
- Never place secrets or environment-specific production values in committed defaults.

---

## 12. Logging and Observability

- Use Python's `logging` module or the project's configured logging solution.
- Do not use `print()` as application logging.
- Use appropriate log levels and structured context where supported.
- Include useful request/correlation identifiers when available.
- Do not log secrets, credentials, tokens, or unnecessary personal data.
- Do not expose internal exception details to API clients.
- Preserve enough diagnostic information for operators without violating privacy.

---

## 13. Docker, CI, and Deployment

Infrastructure should remain proportional to project needs.

When Docker is used:

- Prefer reproducible builds and explicit dependency installation.
- Run application processes as a non-root user where practical.
- Keep secrets out of images and build arguments.
- Use health checks and service readiness checks where appropriate.
- Avoid exposing database and cache ports publicly by default.
- Separate development and production configuration.
- Document required environment variables, ports, volumes, and startup commands.

When CI is configured, prefer a predictable pipeline:

1. Install dependencies from the lockfile.
2. Run formatting/lint checks.
3. Run static type checking if configured.
4. Run Django checks.
5. Validate migrations.
6. Run automated tests.
7. Build/package the application if relevant.

Never deploy or alter a live environment without explicit approval.

---

## 14. Documentation

Keep documentation synchronized with the implementation.

Expected documentation, as relevant to project scope:

- `README.md`: project purpose, prerequisites, setup, run, and test instructions.
- `.env.example`: variable names and safe placeholder values.
- Architecture documentation: app boundaries and important decisions.
- API documentation: endpoints, schemas, authentication, permissions, and errors.
- Operational documentation: migrations, background jobs, deployment, and troubleshooting.

Do not document behavior that has not been verified in code or approved requirements.
Do not invent environment variables, commands, endpoints, or configuration options.

---

## 15. AI Agent Collaboration

All agents must follow this document and their own role-specific instructions.

### 15.1 Ownership

- `architect` owns requirements clarification, system design, task decomposition,
  coordination, and integration decisions.
- `backend-developer` owns implementation of Django/DRF application behavior.
- `database-engineer` owns data modeling, ORM design, constraints, and migrations.
- `qa-engineer` owns test design, test implementation, and reporting test execution.
- `code-reviewer` performs independent read-only reviews.
- `security-engineer` performs threat analysis and security reviews.
- `performance-engineer` investigates and validates performance improvements.
- `devops-engineer` owns development infrastructure and CI/CD configuration.
- `documentation-engineer` owns developer and API documentation.

### 15.2 Delegation

For non-trivial tasks, the Architect should delegate bounded work to specialists.

Every delegated task should state:

- Context and intended outcome.
- Relevant files or modules.
- Allowed scope of changes.
- Constraints and non-goals.
- Acceptance criteria.
- Required tests or evidence.
- Expected handoff summary.

Do not assign multiple agents to edit the same files concurrently.
Parallelize only when work is independent or read-only.

### 15.3 Review and integration

- The Architect must inspect the actual diff before accepting delegated changes.
- A specialist's summary is not proof that the implementation is correct.
- Request independent code review for meaningful changes.
- Request security review for authentication, authorization, sensitive data, file handling,
  external requests, and other security-sensitive features.
- Request performance review when measurements or workload justify it.
- Run tests and checks after integration.
- Resolve conflicting changes deliberately; do not silently discard another agent's work.

### 15.4 Agent communication

Agents must distinguish:

- Verified facts from assumptions.
- Implemented changes from recommendations.
- Tests executed from tests merely suggested.
- Confirmed defects from potential risks.
- Required product decisions from technical implementation choices.

Do not report routine progress checklists unless they contain a meaningful blocker,
decision, or result.

---

## 16. Definition of Done

A task is complete only when all applicable conditions are satisfied:

- Requirements and acceptance criteria are understood.
- The implementation is limited to the requested scope.
- Architecture and project conventions are respected.
- API behavior and data access are correct.
- Authentication and authorization are enforced where applicable.
- Relevant tests are added or updated.
- Relevant checks have been run, or unrun checks are explicitly disclosed.
- Migrations are generated and reviewed when schema changes are made.
- Documentation is updated when behavior, setup, or API contracts change.
- No secrets or unrelated user changes are included.
- Important limitations and follow-up work are reported.

### Required completion report

Every implementation task must finish with a concise report:

1. **Implemented:** what changed and where.
2. **Decisions:** important assumptions and trade-offs.
3. **Verification:** exact checks/tests run and their observed results.
4. **Risks:** known limitations, unresolved questions, and follow-up work.

Never claim completion of work that was not performed or verified.
