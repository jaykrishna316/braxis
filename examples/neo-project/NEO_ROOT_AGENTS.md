# Neo - Conflict Management Platform

**Project Description:** Neo is a distributed conflict management and resolution platform. This monorepo contains the API backend (`api/`), analytics engine (`analytics/`), escalation manager (`escalation/`), and resolution workflow engine (`resolution/`).

## Critical Instruction

When modifying files, **follow the nearest scoped AGENTS.md** for that subsystem.

This file contains global patterns and monorepo-wide gotchas.  
Scoped files contain subsystem-specific rules, commands, and boundary rules.

## Repository Gotchas

These are common traps when working on Neo:

1. **Conflict State Mutations**  
   *Symptom:* Race conditions or ghost conflicts in the system  
   *Problem:* Conflict state is immutable; direct mutations break distributed consistency  
   *Solution:* Always create new Conflict objects; never mutate existing ones. Use `conflict.with_status(new_status)` not `conflict.status = new_status`

2. **Missing Audit Trail**  
   *Symptom:* Cannot trace why a conflict was resolved or escalated  
   *Problem:* Every state change must be recorded for compliance  
   *Solution:* All mutations go through `StateTransition` events. Never update conflict directly without creating an event.

3. **Escalation Without Bounds**  
   *Symptom:* Conflicts escalate infinitely or to wrong handlers  
   *Problem:* Escalation chain not declared upfront  
   *Solution:* Define escalation_path in ConflictType before creating conflicts. See escalation/AGENTS.md

4. **Synchronous I/O in Resolution Flow**  
   *Symptom:* Resolution hangs when external system is slow  
   *Problem:* Resolution must be async-first for remote notifications  
   *Solution:* Use AsyncResolution pattern. Never block on external calls. See resolution/AGENTS.md

5. **Analytics Data Staleness**  
   *Symptom:* Dashboard shows old resolution counts  
   *Problem:* Analytics is eventually consistent; writes are async  
   *Solution:* Don't query analytics for single-conflict decisions. Use conflict state directly for immediate needs.

## Subsystems & Ownership

| Subsystem | Owner | Purpose | Link |
|-----------|-------|---------|------|
| `api/` | Backend team | REST API and core conflict logic | [api/AGENTS.md](api/AGENTS.md) |
| `resolution/` | Resolution team | Workflow resolution engine | [resolution/AGENTS.md](resolution/AGENTS.md) |
| `escalation/` | Escalation team | Multi-tier escalation system | [escalation/AGENTS.md](escalation/AGENTS.md) |
| `analytics/` | Analytics team | Metrics and insights | [analytics/AGENTS.md](analytics/AGENTS.md) |
| `packages/shared` | Platform team | Type definitions, utilities | [packages/AGENTS.md](packages/AGENTS.md) |

## Shared Architecture Patterns

### Conflict Lifecycle

```
Created (new_conflict event) 
  ↓
Investigating (investigation_started event)
  ↓
Resolved (conflict_resolved event) [OR] Escalated (escalation_triggered event)
  ↓
Closed (conflict_closed event)
```

Each arrow is an **immutable StateTransition event** with audit trail.

### Data Flow Between Subsystems

```
api/ (creates conflicts)
  ↓
resolution/ (proposes resolutions)
  ↓
escalation/ (escalates if needed)
  ↓
analytics/ (aggregates for insights)
```

- **api/** is source of truth for conflict state
- **resolution/** doesn't modify conflicts directly (proposes via API)
- **escalation/** routes to right handler via escalation_path
- **analytics/** reads events, never modifies conflicts

### State Management Ownership

| Data | Owner | Access Pattern |
|------|-------|-----------------|
| Conflict state | api/models | Read-only (via query); write via state_transition events |
| Resolution proposals | resolution/ | Owned by resolution engine; lifecycle managed internally |
| Escalation chain | escalation/config | Static per ConflictType; never changes at runtime |
| Metrics | analytics/ | Async-written from event stream; not real-time |

### Cross-Subsystem Contracts

**api/** → **resolution/**
- Emits: `conflict_created`, `investigation_started` events
- Expects: `resolution_proposed` event with proof-of-work (see resolution/AGENTS.md)

**resolution/** → **escalation/**
- Calls: `should_escalate(conflict, resolution_proposal)` 
- Expects: Escalation path and handler info back

**escalation/** → **api/**
- Calls: `escalate_conflict(conflict_id, escalation_level)`
- Expects: Conflict updated with escalation metadata

**analytics/** → all subsystems
- Reads: Event stream (read-only consumer)
- Never: Modifies state, sends events back

## Building & Testing (from repo root)

```bash
# Run all checks across all subsystems
make all                    # format, lint, type-check, test

# Format code
make format                 # Python Black + isort

# Check code quality  
make lint                   # Flake8 + pylint + mypy

# Type validation
make type-check             # mypy on all subsystems

# Run tests
make test                   # pytest across all subsystems
make test-unit              # Unit tests only (fast)
make test-integration       # Integration tests (requires services)

# Watch mode for development
make test-watch             # Re-run on file changes
```

⚠️ **Do not:** Start running services manually (uvicorn, workers). Use Docker Compose for integration testing.

## Monorepo Structure

```
neo/
├── api/                     # Core REST API and conflict models
│   ├── src/
│   │   ├── models/          # Conflict, StateTransition, etc.
│   │   ├── controllers/      # HTTP endpoints
│   │   ├── services/         # Business logic
│   │   └── db/              # Database layer
│   └── tests/
├── resolution/              # Resolution workflow engine
│   ├── src/
│   │   ├── engine/          # Resolution algorithm
│   │   ├── proposals/       # Proposal generation
│   │   └── validators/      # Proof-of-work validation
│   └── tests/
├── escalation/              # Escalation routing
│   ├── src/
│   │   ├── chain/           # Escalation chain logic
│   │   ├── routing/         # Route to handlers
│   │   └── config/          # Escalation paths
│   └── tests/
├── analytics/               # Metrics and reporting
│   ├── src/
│   │   ├── aggregators/     # Metrics aggregation
│   │   ├── consumers/       # Event consumers
│   │   └── models/          # Analytics models
│   └── tests/
├── packages/
│   ├── shared/              # Shared types, utilities
│   └── proto/               # Protocol buffers (if using gRPC)
└── docker/                  # Docker Compose for local dev
```

## Important: Immutability & Events

**Core principle:** Conflicts are immutable. All changes are events.

Never write:
```python
conflict.status = "resolved"  # ← WRONG
conflict.resolve(...)         # ← WRONG
```

Always write:
```python
StateTransition.create(
    conflict_id=conflict.id,
    event_type="conflict_resolved",
    from_status=conflict.status,
    to_status="resolved",
    metadata={...}
)
```

This ensures:
- Audit trail for compliance
- Distributed consistency
- Event sourcing capability
- Easy debugging

## Dependencies Between Subsystems

```
resolution/ → api/          (reads conflicts, emits events via API)
escalation/ → resolution/   (queries for escalation decision)
escalation/ → api/          (updates escalation metadata)
analytics/ → api/           (consumes event stream)
```

**Never create:**
- Direct database connections between subsystems
- Circular dependencies (A → B → A)
- Shared mutable state

## When to Add New Subsystems

Add a new subsystem when:
- ✅ It has clear ownership and boundaries
- ✅ It provides a distinct service (e.g., notification, audit)
- ✅ It's independent enough for separate deployment

Don't add when:
- ❌ It's just a new feature (add to existing subsystem instead)
- ❌ It requires shared mutable state

---

For subsystem-specific guidance, see:
- [api/AGENTS.md](api/AGENTS.md) - Core API and conflict management
- [resolution/AGENTS.md](resolution/AGENTS.md) - Resolution workflow
- [escalation/AGENTS.md](escalation/AGENTS.md) - Escalation routing
- [analytics/AGENTS.md](analytics/AGENTS.md) - Metrics and insights

