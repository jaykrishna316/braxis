# Documentation Patterns Extraction: v2.0 Templates

**Research Date:** October 2, 2026  
**Source:** Analysis of 20 leading open-source projects  
**Output:** Better AGENTS.md templates for Braxis v1.2+  

---

## Key Patterns Found

### Pattern 1: Hierarchical Guidance with "Follow Nearest File" Rule

**Found in:** Dify, CrewAI, Next.js

**Example (Dify):**
```
Follow the nearest scoped `AGENTS.md` for the files being changed. 
Apply its guidance within the user's requested scope; explicit user 
instructions take precedence over workflow defaults.
```

**Structure:**
```
Root AGENTS.md → Subsystem AGENTS.md → Local guidelines
- Root: General patterns, monorepo gotchas, architecture overview
- Subsystem: Language-specific, tool-specific, domain-specific rules
- Local: Feature-level or module-level guidance
```

**Application:** Should be first thing in every AGENTS.md

---

### Pattern 2: Repository Gotchas Section

**Found in:** Dify, Next.js, CrewAI

**Example (Dify):**
```
## Repository Gotchas

- Run backend commands through `uv run --project api <command>`
- Backend integration tests are CI-only
- Keep docker/.env.example limited to default Docker Compose vars
- Put optional/provider-specific settings in docker/envs/*.env.example
```

**Purpose:** These are the traps contributors fall into first

**Application:** Essential for every repo AGENTS.md

---

### Pattern 3: Language/Tool-Specific Message Handling

**Found in:** CrewAI (multimodal message content), React (JSX specifics)

**Example (CrewAI):**
```
## Message Content Rules

`LLMMessage.content` is `str | list[dict[str, Any]] | None`
- List form is multimodal content parts
- Never `str()` it — puts Python repr in front of model
- Collapse to text with: message_content_text(msg)
```

**Pattern:** Type + why it matters + correct handling + example

**Application:** Every subsystem with special data structures

---

### Pattern 4: Contract & Boundary Documentation

**Found in:** Dify (API subsystem), Next.js (package boundaries), CrewAI (documentation structure)

**Example (Dify API):**
```
## Architecture and Boundaries

- Treat `api/core/` as migration-only: do not add files
- Keep transport parsing in controllers
- Keep orchestration in services
- Keep domain policy in domain owner
- Do not perform I/O inside open transactions
```

**Structure:**
- What to DO
- What NOT to DO
- Why (implicit in scope)
- Owner chain for reads/writes

**Application:** Essential for backend, framework, core subsystems

---

### Pattern 5: Command Reference with Context

**Found in:** Dify, Next.js, CrewAI

**Example (Dify API):**
```
## Commands

Run backend checks from repository root:
- Format and lint: `make lint`
- Type check: `make type-check`
- Unit tests: `make test`
- Targeted tests: `make test TARGET_TESTS=./api/tests/<path>`

Run direct Python commands through `uv run --project api`
```

**Pattern:** 
- Full invocation (including context like "from repo root")
- Common tasks (format, lint, test, type-check)
- Variations and advanced usage
- What NOT to do (e.g., "do not start long-running services")

**Application:** Every subsystem with development commands

---

### Pattern 6: Cross-Module & Cross-Subsystem Links

**Found in:** Dify (web subsystem), Next.js (packages)

**Example (Dify Web):**
```
## Package Contracts

Web owns application-specific requirements and consumes:
- Shared architecture from skills and primitives from Dify UI
- Link to contract owners instead of redefining

[Links to]:
- [Button contract]: ../packages/dify-ui/src/button/README.md
- [Form contract]: ../packages/dify-ui/docs/forms.md
- [Keyboard commands]: docs/hotkeys.md
```

**Pattern:**
- Declare what this subsystem owns
- Declare what it consumes from others
- Link to the contract (not redefine)
- Use markdown reference links for maintainability

**Application:** Monorepos with shared components, APIs, contracts

---

### Pattern 7: Framework-Generated Sections (Auto-Updated)

**Found in:** Dify (Next.js rules auto-regenerated), TypeScript projects

**Example (Dify Web):**
```
<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file 
structure may all differ from your training data. Read the relevant 
guide in `node_modules/next/dist/docs/`.

This block is written and re-added by `next dev` — verify at 
`node_modules/next/dist/server/lib/generate-agent-files.js`.

<!-- END:nextjs-agent-rules -->
```

**Pattern:**
- Marked blocks with BEGIN/END comments
- Framework auto-regenerates on update
- Agents know to re-read when framework changes
- Acts as "contract staleness detector"

**Application:** Projects with framework dependencies (Next.js, etc.)

---

### Pattern 8: Before/After Code Examples

**Found in:** Next.js (how NOT to write modules), CrewAI (message handling)

**Example (CrewAI):**
```
# Wrong:
text = str(msg.content)  # Creates Python repr string

# Right:
from crewai.utilities.agent_utils import message_content_text
text = message_content_text(msg)  # Handles str, list, None correctly
```

**Application:** Common mistakes + correct approach

---

### Pattern 9: Subsystem Ownership & Responsibilities

**Found in:** Dify, React (component ownership), Next.js (package ownership)

**Example (Dify Web):**
```
## Package Contracts

Web owns:
- Application-specific requirements
- User-facing strings (i18n keys)
- Page layouts and navigation
- Landmark elements

Web consumes:
- Primitives from @langgenius/dify-ui
- Shared contracts from packages/
- API clients from @/service/console
```

**Application:** Multi-team monorepos where ownership clarity prevents conflicts

---

### Pattern 10: When/How to Refactor or Move Code

**Found in:** Dify, React

**Example (Dify API):**
```
## Architecture and Boundaries

- Move implementations OUT of `api/core/` (migration-only area)
- Keep `libs/` business-agnostic and reuse existing owners before 
  adding abstractions
- Extract domain policy OUT of controllers into domain owners
```

**Application:** Prevents accumulation of technical debt in "core" areas

---

## Template Structure for v2.0

### Tier 1: Root AGENTS.md (Monorepo)
1. "Follow nearest scoped AGENTS.md" rule
2. Repository Gotchas (top 5)
3. Subsystems overview (with links)
4. Shared patterns & architecture overview
5. Cross-subsystem conventions

### Tier 2: Subsystem AGENTS.md (API, Web, CLI, etc.)
1. Purpose & ownership declaration
2. Key Guidelines (3-5 points)
3. Subsystem-specific data structures (with handling rules)
4. Commands reference (format, lint, test, type-check)
5. Architecture & Boundaries
6. Package/Contract ownership links
7. Common mistakes & correct patterns
8. Before/after code examples

### Tier 3: Feature/Module AGENTS.md (Optional)
1. Feature purpose & scope
2. Integration points with other features
3. Data flow expectations
4. Testing patterns specific to feature
5. Links to parent subsystem rules

---

## Patterns NOT to Copy

❌ **Generic guidance** - "Follow Python conventions" (vague)  
❌ **Too much history** - Don't explain how we got here  
❌ **Outdated patterns** - Keep contract-driven, not implementation-driven  
❌ **Dead weight** - No "nice to have" suggestions  

---

## For Neo Project

Based on these patterns, Neo (conflict management) should have:

1. **Root AGENTS.md**
   - Conflict resolution flow overview
   - Multi-subsystem gotchas
   - Key ownership boundaries

2. **Subsystem AGENTS.md** (e.g., `resolution/AGENTS.md`, `escalation/AGENTS.md`)
   - Purpose & ownership
   - Domain-specific data structures (Conflict object, Resolution state)
   - Commands & validation
   - Boundary rules (who owns state transitions)
   - Common mistakes (race conditions in conflict state, etc.)

3. **Feature-level guidance**
   - Specific conflict types and their handling
   - Integration points with other features

---

## Next Steps for Braxis v1.2

1. Update hierarchical generation to use these patterns
2. Add "Repository Gotchas" detection (build system, test runner, env vars)
3. Add "Package Contracts" extraction for monorepos
4. Implement framework-aware auto-update blocks
5. Add subsystem ownership declaration template

