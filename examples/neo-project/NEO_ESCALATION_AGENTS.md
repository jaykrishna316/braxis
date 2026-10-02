# Neo Escalation Manager - Agent Context

Read this file when working in `escalation/`.  
Then refer to root AGENTS.md for repo-wide patterns.

## Purpose & Ownership

This subsystem implements multi-tier escalation routing and decision logic.

**Owns:**
- Escalation path configuration per ConflictType
- Escalation routing logic (which handler at each tier)
- Handler assignment and availability tracking
- Escalation decision criteria (when to escalate)

**Consumes from:**
- `api/` for conflict state, handler directory
- `resolution/` for resolution proposals (to decide: apply or escalate?)
- `packages/shared` for type definitions

**Never:**
- Modifies handler status or availability (read-only)
- Stores escalation history (api/ owns this)
- Adds new escalation levels dynamically (must be pre-configured)

## Quick Reference

### Commands (from repo root)

```bash
# Escalation tests
make test-escalation                # Run escalation tests only
make test-escalation-unit           # Unit tests (fast)
make test-escalation-integration    # With services

# Type checking
mypy escalation/src/

# Code quality
black --check escalation/
pylint escalation/src/
flake8 escalation/src/
```

### Escalation Flow

```
1. resolution/ proposes resolution with score
   ↓
2. escalation/ queries: should_escalate(conflict, proposal)?
   ↓
3. Escalation router checks:
   - Proposal score (below threshold → escalate)
   - Conflict complexity (complex → escalate)
   - Handler availability (unavailable → escalate next tier)
   ↓
4. If escalate: Pick handler at next tier
   ↓
5. Emit escalation_triggered event to api/
   ↓
6. api/ updates conflict with escalation metadata
   ↓
7. Handler notified and takes over
```

## Core Data Structures

### ConflictType (static configuration)

```python
@dataclass
class ConflictType:
    name: str                        # e.g., "payment_dispute"
    max_escalation_level: int        # Max tiers (0 = no escalation)
    escalation_path: list[EscalationTier]  # Ordered tiers
    escalation_thresholds: dict      # When to escalate
```

**Ownership:** Configured once at startup. Never changes at runtime.

### EscalationTier (per conflict type)

```python
@dataclass
class EscalationTier:
    level: int                       # 0 = initial, 1 = first escalation, etc.
    handler_type: str                # e.g., "mediator", "arbitrator", "executive"
    required_expertise: set[str]     # e.g., {"finance", "negotiation"}
    sla_hours: int                   # Time to respond
    max_concurrent: int              # Max cases per handler
```

**Example:**
```python
payment_dispute = ConflictType(
    name="payment_dispute",
    max_escalation_level=2,
    escalation_path=[
        EscalationTier(level=0, handler_type="resolution_engine", ...),
        EscalationTier(level=1, handler_type="mediator", required_expertise={"finance"}, sla_hours=24, max_concurrent=50),
        EscalationTier(level=2, handler_type="arbitrator", required_expertise={"finance", "law"}, sla_hours=48, max_concurrent=10),
    ],
    escalation_thresholds={
        "proposal_score_min": 0.7,    # Escalate if score < 0.7
        "complexity_high": True,      # Escalate complex disputes
        "handler_unavailable": True,  # Escalate if current handler full
    }
)
```

### EscalationDecision (output)

```python
@dataclass
class EscalationDecision:
    should_escalate: bool            # True/False
    reasoning: str                   # Why this decision
    target_tier: int | None          # Which tier to escalate to (None if not escalating)
    target_handler_type: str | None  # e.g., "mediator"
    metadata: dict                   # Additional context
```

## Architecture & Boundaries

### Decision Logic

```
Input (conflict + resolution proposal)
  ↓
Evaluate Thresholds (score, complexity, etc.)
  ↓
Check Handler Availability
  ↓
Route to Handler (at appropriate tier)
  ↓
Output (escalation decision)
```

### Threshold Evaluation

**Score-based:** If proposal_score < threshold, escalate
```python
if proposal.score < thresholds["proposal_score_min"]:
    return EscalationDecision(should_escalate=True, target_tier=1, ...)
```

**Complexity-based:** If conflict is complex, escalate sooner
```python
if is_complex(conflict) and proposal.score < thresholds["complex_min_score"]:
    return EscalationDecision(should_escalate=True, target_tier=2, ...)
```

**Availability-based:** If current tier full, escalate
```python
handlers = get_handlers(conflict_type, current_tier)
if all_handlers_at_capacity(handlers):
    return EscalationDecision(should_escalate=True, target_tier=current_tier+1, ...)
```

### Handler Routing

```python
def route_to_handler(conflict, tier) -> Handler:
    """Find best handler at tier for conflict."""
    
    handlers = get_available_handlers(conflict.conflict_type, tier)
    
    # Filter by required expertise
    qualified = [h for h in handlers if conflict.required_expertise ⊆ h.expertise]
    
    if not qualified:
        raise NoQualifiedHandlerError(f"No handlers with {conflict.required_expertise}")
    
    # Pick handler with lowest load
    return min(qualified, key=lambda h: h.current_load)
```

### Key Rules

✅ **DO:**
- Read conflict state fresh (no caching)
- Read handler availability fresh (no caching)
- Document escalation thresholds clearly
- Test each threshold independently
- Fail safe (escalate if unsure)
- Log every escalation decision

❌ **DON'T:**
- Modify conflict state
- Modify handler availability directly
- Cache escalation decisions (they're per-conflict, per-time)
- Skip handler availability check (might overload)
- Escalate beyond max_escalation_level
- Assume handler will accept (use async notification)

## Common Mistakes & Fixes

**❌ Hardcoded Escalation Levels**
```python
# WRONG - scales change requires code change
def should_escalate(conflict, proposal):
    if conflict.type == "payment_dispute" and proposal.score < 0.7:
        return EscalationTier.level_1  # ← Hardcoded
```

**✅ Configuration-Driven**
```python
# RIGHT - configuration centralizes rules
def should_escalate(conflict, proposal):
    conflict_type = get_conflict_type(conflict.type)
    threshold = conflict_type.escalation_thresholds["proposal_score_min"]
    
    if proposal.score < threshold:
        return conflict_type.escalation_path[1]  # Read from config
```

**❌ Ignoring Handler Load**
```python
# WRONG - may overload handler
def route_to_handler(conflict):
    handlers = get_handlers(conflict.type, tier=1)
    return handlers[0]  # ← Always returns first, regardless of load
```

**✅ Load-Aware Routing**
```python
# RIGHT - routes to least-loaded
def route_to_handler(conflict):
    handlers = get_handlers(conflict.type, tier=1)
    return min(handlers, key=lambda h: h.current_load)
```

**❌ Stale Handler Status**
```python
# WRONG - handler status may have changed
def check_availability():
    handler = get_handler("mediator_123")  # ← Stale if called twice
    return handler.is_available
```

**✅ Fresh Check**
```python
# RIGHT - always fresh
def check_availability():
    handler = api_client.get_handler_fresh("mediator_123")
    return handler.is_available
```

**❌ Escalating Beyond Bounds**
```python
# WRONG - may exceed max tier
def escalate(conflict):
    current_tier = conflict.escalation_level
    next_tier = current_tier + 1  # ← No bounds check!
    return route_to_handler(conflict, next_tier)
```

**✅ Respecting Max Level**
```python
# RIGHT - enforces max
def escalate(conflict):
    conflict_type = get_conflict_type(conflict.type)
    if conflict.escalation_level >= conflict_type.max_escalation_level:
        raise MaxEscalationReachedError("Cannot escalate further")
    
    next_tier = conflict.escalation_level + 1
    return route_to_handler(conflict, next_tier)
```

## Testing

```bash
# All escalation tests
pytest escalation/tests/

# Specific test class
pytest escalation/tests/test_routing.py::TestHandlerRouting

# With verbose output
pytest escalation/tests/ -vv -s

# Coverage report
pytest escalation/tests/ --cov=escalation/src --cov-report=html
```

### Testing Patterns

**Test threshold evaluation:**
```python
def test_score_based_escalation():
    config = ConflictType(escalation_thresholds={"proposal_score_min": 0.7})
    
    proposal_high_score = ResolutionProposal(..., score=0.9)
    assert not should_escalate(conflict, proposal_high_score, config)
    
    proposal_low_score = ResolutionProposal(..., score=0.5)
    assert should_escalate(conflict, proposal_low_score, config)
```

**Test handler routing:**
```python
def test_routes_to_least_loaded():
    handlers = [
        Handler(id="h1", current_load=10),
        Handler(id="h2", current_load=5),
        Handler(id="h3", current_load=15),
    ]
    
    selected = route_to_handler(conflict, handlers)
    assert selected.id == "h2"  # Least loaded
```

**Test escalation path bounds:**
```python
def test_respects_max_escalation_level():
    conflict_type = ConflictType(..., max_escalation_level=2)
    conflict = Conflict(..., escalation_level=2)  # Already at max
    
    with pytest.raises(MaxEscalationReachedError):
        escalate(conflict, conflict_type)
```

**Test with real conflict data:**
```python
@pytest.mark.integration
async def test_escalation_decision_emission():
    conflict = await api_client.get_conflict("conflict_123")
    proposal = ResolutionProposal(..., score=0.5)  # Low score
    
    decision = should_escalate(conflict, proposal)
    
    assert decision.should_escalate is True
    assert decision.target_tier == 1
    
    # Emit to api/
    event = StateTransition.create(
        conflict_id=conflict.id,
        event_type="escalation_triggered",
        metadata={"escalation_decision": decision}
    )
    await api_client.emit_state_transition(event)
```

## Configuration Management

Escalation paths are configured once at startup. Changes require:

1. Update ConflictType definitions
2. Restart escalation service
3. Propagate to api/ if needed

Don't:
- Change escalation_path at runtime
- Modify tier levels dynamically  
- Allow runtime configuration injection without validation

## Type Hints & Validation

```python
def should_escalate(
    conflict: Conflict,
    proposal: ResolutionProposal,
    config: ConflictType
) -> EscalationDecision:
    """Determine if conflict should be escalated.
    
    Args:
        conflict: The conflict to evaluate
        proposal: The resolution proposal being considered
        config: Configuration for this conflict type
        
    Returns:
        EscalationDecision with reasoning
        
    Raises:
        ValueError: If conflict or proposal invalid
    """
    # Validate inputs
    if not conflict.id or not conflict.conflict_type:
        raise ValueError(f"Invalid conflict: {conflict}")
    
    if not proposal.id or not (0 <= proposal.score <= 1):
        raise ValueError(f"Invalid proposal: {proposal}")
    
    # Process...
    return decision
```

---

For resolution/ integration, see [resolution/AGENTS.md](../resolution/AGENTS.md).  
For api/ state management, see [api/AGENTS.md](../api/AGENTS.md).

