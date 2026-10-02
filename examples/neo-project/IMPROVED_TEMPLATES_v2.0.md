# Improved AGENTS.md Templates v2.0

---

## Template 1: Root AGENTS.md (Monorepo)

```markdown
# Project Name - Agent Context

**Monorepo Overview:** [1-2 sentence description of the monorepo structure]

## Critical Instruction

When modifying files, **follow the nearest scoped AGENTS.md** for that subsystem.

This file contains global patterns and monorepo-wide gotchas.  
Scoped files contain subsystem-specific rules, commands, and boundary rules.

## Repository Gotchas

[Top 5 traps that contributors fall into]

- **Gotcha 1:** Symptom → Impact → Solution
- **Gotcha 2:** ...

## Subsystems & Ownership

| Subsystem | Owner | Purpose | Link |
|-----------|-------|---------|------|
| `api/` | Backend team | API and business logic | [api/AGENTS.md](api/AGENTS.md) |
| `web/` | Frontend team | Web application | [web/AGENTS.md](web/AGENTS.md) |
| `cli/` | Platform team | Command-line interface | [cli/AGENTS.md](cli/AGENTS.md) |
| `packages/` | Shared team | Reusable libraries | [packages/AGENTS.md](packages/AGENTS.md) |

## Shared Architecture Patterns

### Data Flow
[How data flows between subsystems]

### State Management
[Where state lives, who owns it]

### Cross-Subsystem Contracts
[What subsystems expect from each other]

## Building & Testing (from repo root)

```bash
# Run all checks
make all                    # format, lint, type-check, test

# Individual commands
make format                 # Format code
make lint                   # Static checks
make type-check            # Type validation
make test                  # Run all tests
```

## What Each Subsystem Owns

[Declare ownership to prevent scope creep and conflicts]

Example:
- **api/** owns: Business logic, database schema, API contracts
- **api/** consumes from: packages/ (shared types), shared config
- **web/** owns: UI components, page layouts, user interaction
- **web/** consumes from: api/ (API client), packages/ (shared UI)

---

## Template 2: Subsystem AGENTS.md (Backend/API)

```markdown
# API Subsystem - Agent Context

Read this file when working in `api/`.  
Then refer to root AGENTS.md for repo-wide patterns.

## Purpose & Ownership

This subsystem implements the backend API and business logic.

**Owns:**
- Database schema and migrations
- REST/GraphQL API contracts
- Business logic and validation rules
- Service orchestration

**Consumes from:**
- `packages/` for shared types and utilities
- Configuration from root level

## Quick Reference

### Commands (from repo root)

```bash
# Backend development commands
uv run --project api python -m pytest          # Run tests
uv run --project api make lint                 # Lint code
uv run --project api make format               # Format code
uv run --project api make type-check           # Type checking

# Targeted testing
uv run --project api pytest api/tests/service/test_resolution.py -v
uv run --project api pytest -k test_name       # Run single test
```

⚠️ Do not start long-running services (uvicorn, celery workers) in dev mode

### Architecture & Boundaries

**Layer Structure:**
```
Controllers (HTTP/transport layer)
    ↓
Services (business logic orchestration)
    ↓
Domain Models (core business logic)
    ↓
Data Access (database operations)
```

**Key Rules:**
- Keep HTTP parsing/serialization in controllers only
- Never call database directly from service layer (use data layer)
- Keep domain logic out of controllers
- Transaction boundaries: explicit and small

**Architectural Areas:**

| Area | Purpose | Rules |
|------|---------|-------|
| `controllers/` | HTTP handlers | Parse input, orchestrate services, format response |
| `services/` | Business logic | Implement core logic, call data layer, return domain models |
| `models/` | Domain objects | Pure data, minimal methods, no I/O |
| `db/` | Database access | All SQL, transaction management |
| `utils/` | Shared utilities | Keep business-agnostic |

### Common Mistakes & Fixes

**❌ Mistake:** Performing I/O inside database transactions
```python
# Wrong - can cause deadlocks
with db.transaction():
    user = db.get_user(id)
    response = external_api.call()  # ← I/O inside transaction!
    db.update_user(user, response)
```

**✅ Correct:** Do I/O outside transaction
```python
response = external_api.call()      # Outside transaction
with db.transaction():
    user = db.get_user(id)
    db.update_user(user, response)  # Only I/O is database
```

**❌ Mistake:** Leaking database objects to service layer
```python
# Wrong - SQLAlchemy object escapes transaction context
def get_user(id):
    with db.session():
        return db.query(User).get(id)  # ← Returns detached object
```

**✅ Correct:** Convert to domain model
```python
def get_user(id) -> UserModel:
    with db.session():
        user = db.query(User).get(id)
        return UserModel.from_db(user)  # ← Returns clean model
```

### Type Hints

- Use strict types: `str | None` not `Optional[str]`
- Document semantic meaning: `active_user: User | None  # None if not activated`
- Avoid unnecessary defaults: they can mask unsafe states

### Testing

```bash
# All tests
uv run --project api pytest

# Specific directory
uv run --project api pytest api/tests/service/

# Verbose with output
uv run --project api pytest -vv -s

# With coverage
uv run --project api pytest --cov=api/src
```

Focus tests on behavior, not implementation.

---

## Template 3: Subsystem AGENTS.md (Frontend/Web)

```markdown
# Web Subsystem - Agent Context

Read this file when working in `web/`.  
Then refer to root AGENTS.md for repo-wide patterns.

## Purpose & Ownership

This subsystem implements the user-facing web application.

**Owns:**
- User interface and components
- User-facing strings and localization
- Page layouts and navigation
- User interaction patterns

**Consumes from:**
- `packages/shared-ui/` for UI primitives
- `api/` for API client
- Configuration from root level

## Quick Reference

### Commands (from repo root)

```bash
# Development
cd web && npm run dev              # Start dev server (port 3000)
cd web && npm run build            # Production build
cd web && npm run lint             # Check code quality
cd web && npm test                 # Run tests

# Format and type-check
cd web && npm run format           # Format with Prettier
cd web && npm run type-check       # TypeScript check
```

### Component Guidelines

**Component Ownership:** Use shared UI primitives from `packages/shared-ui/`

Don't create custom wrappers around shared primitives.

```tsx
// ✅ Correct - use primitive directly
import { Button } from '@/shared-ui/button'

export function SaveButton() {
  return <Button onClick={save}>Save</Button>
}

// ❌ Wrong - don't wrap primitives
import { Button as SharedButton } from '@/shared-ui/button'
export function SaveButton() {
  return <CustomButton onClick={save}>Save</CustomButton>
}
```

**Localization:** Always use i18n keys for user-facing text

```tsx
// ✅ Correct
import { useI18n } from '@/i18n'
export function SaveButton() {
  const t = useI18n()
  return <button>{t('buttons.save')}</button>
}

// ❌ Wrong
return <button>Save</button>  // Hardcoded text
```

**State Management:** API state lives in `@/api/client`, not in components

```tsx
// ✅ Correct
const { data: conflict } = useConflict(id)

// ❌ Wrong
const [conflict, setConflict] = useState(null)
fetch('/api/conflicts/' + id)  // Don't re-implement client
```

### Package Contracts

Link to contract owners instead of redefining:

- **UI Components:** See [shared-ui/README.md](../packages/shared-ui/README.md)
- **API Client:** See [api/client/README.md](../packages/api-client/README.md)
- **i18n Keys:** See [i18n/locales/](../i18n/locales/)

### Testing

```bash
cd web && npm test                 # Run all tests
cd web && npm test -- --watch      # Watch mode
cd web && npm test components/**   # Test specific directory
```

Test user behavior, not implementation:

```tsx
// ✅ Test behavior
test('shows error when save fails', () => {
  api.mockReject('error')
  render(<SaveButton />)
  userEvent.click(screen.getByText('Save'))
  expect(screen.getByText('Error occurred')).toBeInTheDocument()
})

// ❌ Test implementation
test('sets error state', () => {
  render(<SaveButton />)
  expect(component.state.error).toBe(null)  // Don't test state
})
```

### Common Mistakes

**❌ Hardcoding API endpoints**
```tsx
const response = await fetch('/api/conflicts')  // ← Use client instead
```

**✅ Use API client**
```tsx
const { data } = useConflict()  // ← Uses centralized client
```

---

## Template 4: Feature-Level AGENTS.md (Optional)

```markdown
# [Feature Name] - Agent Context

This feature handles [description].

## Scope

- What this feature does
- What it does NOT do (clear boundaries)

## Data Structures

### [Main Object Name]
```python
class Conflict:
    id: str                    # Unique identifier
    status: ConflictStatus     # One of: open, resolved, escalated
    created_at: datetime       # When created (immutable)
    updated_at: datetime       # Last update
    context: dict              # Contextual data
```

## Integration Points

**Consumes from:**
- [Feature/module name]: [what data, how]

**Provides to:**
- [Feature/module name]: [what data, how]

## State Transitions

```
[State diagram or flow description]

Open → Investigating → Resolved
Open → Investigating → Escalated → Resolved
```

## Common Mistakes

❌ [Mistake]: [Why it's a problem]
✅ [Correct approach]

## Testing

[Feature-specific testing patterns]
```

