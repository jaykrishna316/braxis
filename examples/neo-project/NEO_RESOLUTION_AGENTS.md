# Neo Resolution Engine - Agent Context

Read this file when working in `resolution/`.  
Then refer to root AGENTS.md for repo-wide patterns.

## Purpose & Ownership

This subsystem implements the conflict resolution workflow engine.

**Owns:**
- Resolution algorithm and scoring
- Proposal generation and validation
- Proof-of-work for resolution quality
- Resolution lifecycle (proposed → applied → finalized)

**Consumes from:**
- `api/` for conflict state, conflict types
- `escalation/` for escalation decisions
- `packages/shared` for type definitions

**Never:**
- Modifies conflict state directly (only via API events)
- Stores resolution history (delegate to api/)
- Makes external API calls in blocking code (use async)

## Quick Reference

### Commands (from repo root)

```bash
# Resolution subsystem tests
make test-resolution                # Run resolution tests only
make test-resolution-unit           # Unit tests (fast)
make test-resolution-integration    # With services

# Type checking
mypy resolution/src/

# Code quality
black --check resolution/
pylint resolution/src/
flake8 resolution/src/
```

### Resolution Lifecycle

```
1. Conflict created (api/ emits new_conflict event)
   ↓
2. Resolution engine receives conflict
   ↓
3. Engine generates proposals (1-N candidates)
   ↓
4. Validator checks proof-of-work for each proposal
   ↓
5. Best proposal selected (highest score passing validation)
   ↓
6. Proposal emitted as resolution_proposed event
   ↓
7. Escalation engine decides: apply now or escalate?
   ↓
8. If apply: api/ applies resolution via resolution_applied event
```

## Core Data Structures

### Conflict Object (read-only from api/)

```python
@dataclass
class Conflict:
    id: str                          # Unique identifier
    conflict_type: ConflictType      # Type determines escalation rules
    status: ConflictStatus           # open, investigating, resolved, escalated, closed
    parties: list[Party]             # Involved entities
    context: dict[str, Any]          # Domain-specific context
    created_at: datetime             # Immutable
    updated_at: datetime             # Last state change
    audit_trail: list[StateTransition]  # Complete history
```

**Never mutate.** Read only. Immutable after creation.

### ResolutionProposal (owned by resolution/)

```python
@dataclass
class ResolutionProposal:
    id: str                          # Unique proposal ID
    conflict_id: str                 # Link to conflict
    proposal_type: str               # Type of resolution (settlement, mediation, etc.)
    score: float                     # 0.0-1.0 confidence
    proof_of_work: dict              # Evidence supporting this proposal
    summary: str                     # Human-readable explanation
    actions: list[Action]            # Steps to apply if approved
    metadata: dict                   # Additional context
```

**Ownership:** Proposals live in resolution/. Never exposed to api/ as mutable objects.

### StateTransition (managed by api/)

```python
@dataclass  
class StateTransition:
    id: str                          # Event ID
    conflict_id: str                 # Which conflict
    event_type: str                  # e.g., "resolution_proposed"
    from_status: ConflictStatus      # Previous state
    to_status: ConflictStatus        # New state
    timestamp: datetime              # When it happened
    actor_id: str                    # Who/what triggered it
    metadata: dict                   # Event-specific data
    audit_data: dict                 # For compliance
```

**Creation:** Only api/ creates these. resolution/ requests via API.

## Architecture & Boundaries

### Layers

```
Input (conflicts from api/)
  ↓
Proposal Generation (multiple candidate proposals)
  ↓
Validation (proof-of-work, score checking)
  ↓
Selection (pick best)
  ↓
Output (emit resolution_proposed event via API)
```

### Layer Responsibilities

| Layer | Responsibility | Rules |
|-------|----------------|-------|
| **Input** | Receive conflicts | Only read via API queries; never direct DB access |
| **Generation** | Create proposals | Pure functions; no I/O; test each algorithm separately |
| **Validation** | Check quality | Proof-of-work must be verifiable; scoring deterministic |
| **Selection** | Pick best | Based on score + validation; document tie-breaking |
| **Output** | Emit proposals | Via StateTransition events to api/; never direct mutation |

### Key Rules

✅ **DO:**
- Read conflicts from api/ (fresh each time)
- Keep proposal generation stateless
- Use async for external calls (if any)
- Test algorithms independently
- Document scoring rationale
- Verify proof-of-work is reproducible

❌ **DON'T:**
- Mutate conflicts directly
- Cache conflict state longer than a turn
- Call blocking I/O inside generator
- Skip validation (every proposal must have proof-of-work)
- Assume proposal will be applied (escalation might override)
- Modify api/ tables directly

## Proof-of-Work Requirement

Every ResolutionProposal must include proof-of-work: evidence that the proposal is sound.

```python
# Example: Settlement Proposal
proposal = ResolutionProposal(
    id="prop_123",
    conflict_id="conflict_456",
    proposal_type="settlement",
    score=0.87,
    proof_of_work={
        "method": "party_history_analysis",
        "evidence": {
            "party_a_history": "5 previous settlements, avg duration 2 days",
            "party_b_history": "4 previous settlements, avg duration 3 days",
            "settlement_success_rate": 0.92,
            "estimated_cost_savings": 15000,
        },
        "reasoning": "Both parties have positive settlement history; low-cost proposal"
    },
    summary="Suggest settlement based on party history",
    actions=[
        Action(type="notify_mediator", payload={...}),
        Action(type="schedule_mediation", payload={...}),
    ]
)
```

If proof_of_work is empty or fake, validation fails.

### Common Mistakes & Fixes

**❌ Blocking on External Call**
```python
# WRONG - blocks resolution
def generate_proposals(conflict):
    external_data = requests.get(f"https://api.example.com/history/{conflict.id}")
    # ← Hangs if external service is slow
    return proposals_from_external(external_data)
```

**✅ Async Pattern**
```python
# RIGHT - non-blocking
async def generate_proposals(conflict):
    try:
        external_data = await fetch_external_history(conflict.id)
        return proposals_from_external(external_data)
    except TimeoutError:
        return default_proposals(conflict)  # Fallback
```

**❌ Mutating Conflict**
```python
# WRONG - violates immutability
def apply_proposal(proposal):
    conflict = get_conflict(proposal.conflict_id)
    conflict.status = "resolved"  # ← Mutation!
    conflict.save()
    return conflict
```

**✅ Event-Driven**
```python
# RIGHT - creates event
def apply_proposal(proposal):
    conflict = get_conflict(proposal.conflict_id)
    event = StateTransition.create(
        conflict_id=conflict.id,
        event_type="resolution_applied",
        from_status=conflict.status,
        to_status="resolved",
        metadata={"proposal_id": proposal.id}
    )
    api_client.emit_state_transition(event)
    return event
```

**❌ Trusting Stale Data**
```python
# WRONG - caches conflict
conflict_cache = {}
def cached_get_conflict(conflict_id):
    if conflict_id not in conflict_cache:
        conflict_cache[conflict_id] = api_client.get_conflict(conflict_id)
    return conflict_cache[conflict_id]  # ← May be stale!
```

**✅ Fresh Read**
```python
# RIGHT - always fresh
def get_conflict_fresh(conflict_id):
    return api_client.get_conflict(conflict_id)  # ← Fresh each time
```

## Testing

```bash
# All resolution tests
pytest resolution/tests/

# Specific test class
pytest resolution/tests/test_proposal_generation.py::TestSettlementGenerator

# With verbose output
pytest resolution/tests/ -vv -s

# Coverage report
pytest resolution/tests/ --cov=resolution/src --cov-report=html
```

### Testing Patterns

**Test algorithms independently:**
```python
def test_settlement_generator():
    # Arrange
    conflict = create_test_conflict(parties=[party_a, party_b])
    generator = SettlementGenerator()
    
    # Act
    proposals = generator.generate(conflict)
    
    # Assert
    assert len(proposals) > 0
    assert all(p.proof_of_work for p in proposals)  # All have proof
    assert all(0 <= p.score <= 1 for p in proposals)  # Valid scores
```

**Test proof-of-work validation:**
```python
def test_proposal_validation():
    proposal = ResolutionProposal(
        ...,
        proof_of_work={"method": "...", "evidence": {...}}
    )
    assert ProofOfWorkValidator.is_valid(proposal)  # Passes
    
    invalid_proposal = ResolutionProposal(..., proof_of_work={})
    assert not ProofOfWorkValidator.is_valid(invalid_proposal)  # Fails
```

**Test integration with api/:**
```python
@pytest.mark.integration
async def test_proposal_emission_to_api():
    conflict = await api_client.get_conflict("conflict_123")
    proposal = generate_proposal(conflict)
    
    await api_client.emit_resolution_proposed(proposal)
    
    event = await api_client.get_latest_event(conflict.id)
    assert event.event_type == "resolution_proposed"
    assert event.metadata["proposal_id"] == proposal.id
```

## Type Hints & Safety

- Use strict types: `list[Party]` not `List[Party]`
- Document unions: `status: str | None  # None if unknown`
- Prefer dataclasses over dicts for proposals
- Validate incoming conflicts immediately

```python
def process_conflict(conflict: Conflict) -> list[ResolutionProposal]:
    # Validate immediately
    if not conflict.id or not conflict.conflict_type:
        raise ValueError(f"Invalid conflict: {conflict}")
    
    # Process
    proposals = generate_proposals(conflict)
    return proposals
```

---

For api/ integration details, see [api/AGENTS.md](../api/AGENTS.md).  
For escalation decision flow, see [escalation/AGENTS.md](../escalation/AGENTS.md).

