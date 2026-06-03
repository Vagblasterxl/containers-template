---
name: claude-dreaming
description: >
  Explain and configure Claude Managed Agents "dreaming" — the scheduled
  memory consolidation feature released May 2026. Use this skill when the user
  asks about: "dreaming", "Claude dreaming", "enable dreaming", "memory
  consolidation", "persistent agent memory", "agent learns between sessions",
  "Claude dreaming feature", "how does Claude remember between sessions",
  "agent memory across sessions", "session memory consolidation".
---

# Claude Dreaming Skill

You are explaining and helping the user configure **dreaming** — a Claude
Managed Agents feature for persistent memory consolidation released in May 2026
(research preview).

## What is dreaming?

Dreaming is a scheduled background process that consolidates an agent's
persistent memory between sessions. It works by:

1. Reviewing transcripts from recent sessions
2. Merging duplicate or redundant memory entries
3. Removing stale or outdated entries
4. Surfacing recurring patterns into higher-level generalizations
5. Writing the consolidated result back to the agent's memory store

The analogy is hippocampal memory consolidation in humans — the process by which
short-term experiences are compressed into long-term knowledge during sleep.

**Real-world impact:** Harvey (legal AI company) reported a **6x increase** in
task completion rates after enabling dreaming for their agents.

## When does dreaming help?

Dreaming is most valuable when:

- An agent runs **across many sessions** and needs to retain what it has learned
- The agent encounters **recurring patterns** (same document types, same errors,
  same user preferences) that should inform future behavior
- You want the agent to **self-improve** over time without manual prompt tuning
- Memory stores are growing large and need periodic pruning

Dreaming is **less useful** for:
- Single-session or stateless agents
- Agents with no persistent memory store configured
- Simple task runners that don't need to generalize from experience

## Requirements

Dreaming requires the **Claude Managed Agents SDK** — it is not available via
the plain Anthropic Messages API. You need:

1. An agent configured with a `memory_store` (the persistent store dreaming
   reads from and writes back to)
2. Claude Managed Agents SDK (`anthropic-agents` package or equivalent)
3. A dream schedule defined in your agent configuration

Dreaming does **not** work with:
- Plain `anthropic.messages.create()` API calls
- Claude.ai web interface sessions
- Claude Code sessions (these are ephemeral by design)

## How to enable it

### Step 1 — Ensure you have a memory store

Your agent must have persistent memory configured. Example:

```python
from anthropic_agents import Agent, MemoryStore

store = MemoryStore(backend="postgres", connection_string="...")

agent = Agent(
    model="claude-opus-4-8",
    memory_store=store,
)
```

### Step 2 — Configure a dream schedule

Add a `dream_config` to your agent:

```python
from anthropic_agents import Agent, MemoryStore, DreamConfig

agent = Agent(
    model="claude-opus-4-8",
    memory_store=store,
    dream_config=DreamConfig(
        schedule="0 3 * * *",       # cron: daily at 3 AM
        max_memory_age_days=30,     # prune entries older than 30 days
        consolidation_threshold=5,  # merge when 5+ similar entries exist
        scope="session_transcripts" # what to read: session_transcripts | tool_outputs | both
    ),
)
```

### Step 3 — Run the dream cycle manually (optional)

To trigger dreaming on demand rather than waiting for the schedule:

```python
await agent.dream()
# or synchronously:
agent.dream_sync()
```

### Step 4 — Inspect dream output

After dreaming, inspect what was consolidated:

```python
report = await agent.last_dream_report()
print(report.merged_count)      # entries merged
print(report.pruned_count)      # entries removed
print(report.patterns_surfaced) # new generalizations added
```

## Applying dreaming to image analysis workflows

If you are using the `gemma-vision` or `image-analyze` skills across many
sessions, dreaming can help your agent remember:

- Which document types it has seen and their common schemas
- User preferences for output format (JSON vs markdown, verbosity level)
- Recurring anomaly patterns in your specific data
- Which prompts work best for particular image categories

Example: An agent processing invoices daily will, after dreaming, have a
consolidated memory entry like:
> "Invoices from Vendor X always use EUR and have a 'Tax ID' field in the
> header that maps to the `vendor.tax_id` schema field."

This means future sessions start with that knowledge without re-deriving it.

## Limitations (as of June 2026)

- **Research preview**: API shape may change; check the changelog before
  pinning to a specific version
- **Transcript access required**: Dreaming reads session transcripts — ensure
  your data retention policy allows this
- **Not real-time**: Dream cycles run on a schedule; the agent won't
  consolidate mid-session
- **Model cost**: Each dream cycle uses model tokens to process transcripts;
  size the schedule to your budget
- **No cross-agent sharing**: Each agent dreams independently; memory is not
  shared across agent instances

## Official documentation

`platform.claude.com/docs/en/managed-agents/dreams`
