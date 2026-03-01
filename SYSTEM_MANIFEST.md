# SYSTEM MANIFEST — containers-template
# For AI agents picking up this project. Full architectural context.
# Generated: 2026-03-01
# Branch: claude/claude-md-mkwtjrbl2esmei8u-axiUw
# Repo: Vagblasterxl/containers-template

---

## PROJECT IDENTITY

| Field | Value |
|-------|-------|
| Name | containers-template |
| Codename | Borg Engine — Persistent Backend |
| Version | 0.0.1 (starter template, barely modified) |
| Stage | **embryonic** — only CLAUDE.md added on top of stock template |
| Deployed | false |
| Builds clean | true (TypeScript compiles, Docker builds) |
| Runs locally | true (npm run dev → localhost:8787) |
| Lines of code | 706 total (70 worker, 61 container, 184 docs, rest config) |

---

## TECH STACK

| Component | Technology | Version |
|-----------|------------|---------|
| Runtime | Cloudflare Workers | — |
| Server framework | Hono | 4.11.1 |
| Language (Worker) | TypeScript | 5.9.3 |
| Language (Container) | Go | 1.24 |
| Container runtime | Cloudflare Containers | 0.0.30 |
| State management | Durable Objects + SQLite | — |
| CLI | Wrangler | 4.56.0 |
| Container base | golang:1.24-alpine → scratch | — |

---

## SCRIPTS

| Name | Command | What it does |
|------|---------|-------------|
| dev | `wrangler dev` | Local dev server at localhost:8787 |
| start | `wrangler dev` | Same as dev |
| deploy | `wrangler deploy` | Deploy worker + container to Cloudflare |
| cf-typegen | `wrangler types` | Regenerate TypeScript types from wrangler config |

---

## FILE MAP

```
containers-template/           (706 lines total)
├── src/
│   └── index.ts               (70 lines) Worker entry: Container class + Hono routes
├── container_src/
│   ├── main.go                (61 lines) Go HTTP server inside the container
│   └── go.mod                 Go module definition
├── Dockerfile                 (24 lines) Multi-stage: golang:1.24-alpine → scratch
├── wrangler.jsonc             (32 lines) Workers + Containers + DO config
├── tsconfig.json              (44 lines) TypeScript strict, ES2021, Bundler resolution
├── worker-configuration.d.ts  (10848 lines) Auto-generated Cloudflare types
├── package.json               (33 lines) Dependencies and scripts
├── CLAUDE.md                  (184 lines) AI assistant context doc
├── README.md                  (59 lines) User-facing docs
└── .gitignore                 (199 lines) Standard Node + Cloudflare ignores
```

---

## ARCHITECTURE

### Worker Layer (src/index.ts — 70 lines)

**Container class:**
```
MyContainer extends Container<Env>
  defaultPort = 8080
  sleepAfter = "2m"
  envVars = { MESSAGE: "I was passed in via the container class!" }
  onStart()  → console.log
  onStop()   → console.log
  onError()  → console.log
```

**Routes:**

| Method | Path | What it does |
|--------|------|-------------|
| GET | `/` | Lists available endpoints (plain text) |
| GET | `/container/:id` | Routes to named container instance |
| GET | `/lb` | Load balances across 3 random containers |
| GET | `/error` | Forces container panic (error handling demo) |
| GET | `/singleton` | Gets single persistent container instance |

### Container Layer (container_src/main.go — 61 lines)

Go HTTP server on port 8080 with graceful shutdown (SIGINT/SIGTERM, 5s timeout).

| Path | What it does |
|------|-------------|
| `/` | Echo MESSAGE env var + Durable Object ID |
| `/container` | Same as `/` |
| `/error` | `panic("This is a panic")` |

### Cloudflare Bindings (wrangler.jsonc)

| Binding | Type | Value |
|---------|------|-------|
| MY_CONTAINER | Durable Object | MyContainer class |
| — | Container | MyContainer, max 10 instances, ./Dockerfile |
| — | SQLite migration | MyContainer class, tag v1 |

### Docker Build (Dockerfile — 24 lines)

```
Stage 1 (build): golang:1.24-alpine
  → copy go.mod, download deps
  → copy *.go, build static binary (CGO_ENABLED=0)

Stage 2 (runtime): scratch
  → copy CA certs + binary only
  → EXPOSE 8080
  → CMD ["/server"]
```

---

## WHAT THIS REPO IS

A **stock Cloudflare Containers starter template** with one addition (CLAUDE.md). The demo code routes HTTP requests to Go containers via Durable Objects. It demonstrates parameterized routing, singleton instances, load balancing, and error handling.

## WHAT THIS REPO IS NOT

- Not a real application — it's a hello-world echo server
- Not deployed — no live URL exists
- Not using its own SQLite — migrations declared, zero queries written
- Not connected to any other project in the system

---

## UNIQUE CAPABILITIES (what no other project in the system has)

1. **Go containers** — long-running processes with real compute power. Every other project is JavaScript/TypeScript only.
2. **Durable Objects with SQLite** — declared and migration-ready. No other project has persistent per-instance SQL storage.
3. **Container lifecycle management** — onStart/onStop/onError hooks, sleep timeout, auto-scaling up to 10 instances.
4. **Multi-stage Docker builds** — produces minimal scratch images. The only project with a Dockerfile.
5. **Load balancing** — getRandom() distributes across container instances. No other project has this.

---

## GIT HISTORY

| Hash | Date | Message |
|------|------|---------|
| e644c4b | 2026-03-01 | Add comprehensive CLAUDE.md for AI assistant context |
| 46bde8e | — | source repo import |

Branch: `claude/claude-md-mkwtjrbl2esmei8u-axiUw` (2 commits ahead of import)

---

## BROADER SYSTEM — THE BORG ENGINE

This project is one piece of a multi-repo system being built across separate Claude Code sessions. Here is every known piece:

### Piece 1: HUD:OS (the face)
- **Repo:** Vagblasterxl/vite-react-template
- **Branch:** claude/hud-touchscreen-ai-comms-LvCe4
- **Stack:** Cloudflare Workers + Hono + React 19 + Vite
- **Lines:** 5,344 (2,284 CSS alone)
- **Status:** Built, runs locally, not deployed
- **What it is:** Cyberpunk operator workstation with 6 panels — comms, debate, audiobook, AI NPC companions, virtual filesystem, Llama terminal
- **Storage:** In-memory (all state lost on refresh)
- **LLM:** Simulated (hardcoded fake responses, no real AI wired)
- **12 commits, 10 components, 11 API routes**

### Piece 2: Polar MCP (the skill/instruction engine)
- **Repo:** Vagblasterxl/vite-react-template (SAME repo, different branch)
- **Branch:** claude/polar-ncp-dynamic-variables-xIZK2
- **Stack:** Cloudflare Workers + Hono + React 19 + Vite
- **Status:** Built, not deployed
- **What it is:** Custom MCP server with dynamic variables (scoped: global/dev/staging/prod), programmable skills with template interpolation, webhooks with HMAC, audit log, SSE streaming, full MCP JSON-RPC 2.0
- **Storage:** In-memory (needs KV/D1 swap)
- **7 API endpoint groups, 9 MCP methods, 5 management tools**

### Piece 3: Brain/Memory System (the shared memory)
- **Repo:** Vagblasterxl/llm-chat-app-template
- **Branch:** (unknown — built in a different session)
- **Stack:** Cloudflare Workers + Hono
- **Status:** Code written, R2 bucket not created, not deployed
- **What it is:** R2-backed document store with 7 CRUD endpoints (read/write/append/delete/list/search/dump). Designed as shared brain for cross-session Claude coordination.
- **Seed docs:** orientation.md, architecture.json, decisions.md, session logs, templates
- **Storage:** R2 bucket "shared-brain" (not yet created)

### Piece 4: Captain Proton (the webhook trigger)
- **Status:** Exists (minimal detail available)
- **What it is:** Cloudflare Worker that catches Polar.sh webhooks (product created, order completed) and triggers downstream actions

### Piece 5: DesktopCommander (local machine control)
- **Status:** Exists/configured
- **What it is:** Local MCP server for executing system commands on the operator's Windows machine

### Piece 6: Claude Desktop (the MCP client)
- **Status:** Configured
- **Config:** C:\Users\kenws\AppData\Roaming\Claude\claude_desktop_config.json
- **What it is:** Hardwired to official Polar MCP (mcp.polar.sh) via mcp-remote

### Piece 7: MCPB System (the protocol engine)
- **Location:** C:\Users\kenws\Downloads\mcpb-system\ (zip + extracted folder)
- **Status:** 35 files, 56 tests passing, not deployed
- **What it is:** Model Context Protocol Builder with 5 kits (Vision/Action/Network/Security/Meta), 12 extensions (Resilience + Performance stacks), 3 protocols (gRPC Python, gRPC Go QUIC, ZeroMQ), 3 Cloudflare Workers (auto-heal, scaler, Durable Object with SQLite)
- **Caveat:** Vision and Action kits are stubs. Go QUIC server not compiled. Only gRPC Python path actually runs.

### Piece 8: THIS PROJECT — containers-template (the persistent backend)
- **Repo:** Vagblasterxl/containers-template
- **Branch:** claude/claude-md-mkwtjrbl2esmei8u-axiUw
- **Status:** Stock template + CLAUDE.md. No real functionality built yet.
- **What it SHOULD be:** The persistent state and compute layer for the entire system.

---

## CLOUDFLARE ACCOUNT TOPOLOGY

| Account | Email | Status | Role |
|---------|-------|--------|------|
| Vagblaster | vagblasterxl@gmail.com | Most loaded, original, messy | Production (legacy) |
| KW Simmons | (grandfathered Gmail) | $25 Workers paid plan | Main backend |
| Roger Dodger | (Gmail) | Empty, connected | Staging/utilities |
| 4th, 5th, 6th | Available | Not active | Reserve |

All connected via Cloudflare Tunnels. Authority routing: Vagblaster owns Cloudflare/Workers conflicts, ASS authority owns GCP/Vertex conflicts.

---

## GOOGLE CLOUD STACK (UNUSED — CREDITS EXPIRING)

| Resource | Status | Expiry |
|----------|--------|--------|
| $300 free server credit | Unused | ~1.5 months |
| $1,000 GUI Builder tokens | Barely touched | Unknown |
| Chirp (voice AI) | Available, not wired | — |
| BigQuery | Available, not used | Tied to $300 credit |
| Full GCP stack | Server sitting idle | Tied to $300 credit |

---

## CROSS-SYSTEM CONNECTION MAP

```
                    ┌─────────────┐
                    │  Claude      │
                    │  Desktop     │
                    │  (MCP client)│
                    └──────┬──────┘
                           │ mcp-remote
                    ┌──────▼──────┐
                    │  Polar MCP  │──────── webhooks ────┐
                    │  (skills)   │                      │
                    └──────┬──────┘               ┌──────▼──────┐
                           │                      │  Captain    │
                    ┌──────▼──────┐               │  Proton     │
                    │  HUD:OS     │               └─────────────┘
                    │  (face)     │
                    └──────┬──────┘
                           │ needs persistent state
                           │ needs real LLM
                    ┌──────▼──────────────────┐
                    │  containers-template    │◄── THIS REPO
                    │  (persistent backend)   │
                    │  Go containers + SQLite │
                    │  + Durable Objects      │
                    └──────┬──────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Brain/R2   │
                    │  (memory)   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  MCPB       │
                    │  (protocol  │
                    │   engine)   │
                    └─────────────┘
```

**Status of every connection: NONE BUILT. All are planned.**

---

## GAP ANALYSIS — WHAT'S MISSING ACROSS THE ENTIRE SYSTEM

### CRITICAL (blocks everything else)

| # | Gap | Where | Impact |
|---|-----|-------|--------|
| 1 | **Nothing is deployed** | All projects | No live URLs. Nothing works outside localhost. |
| 2 | **No persistent storage anywhere** | HUD, Polar MCP, Brain | Page refresh = total data loss. Every piece is in-memory. |
| 3 | **SQLite declared but unused** | This repo | The one project with real persistence capability isn't using it. |
| 4 | **No authentication on any endpoint** | All projects | Every API is wide open. |
| 5 | **Memory bridge auth missing** | KW Simmons account | Listed as #2 on the constitution's own triage list. Foundation of the coordination system has no auth. |

### HIGH (causes duplicate work and lost context)

| # | Gap | Where | Impact |
|---|-----|-------|--------|
| 6 | **No cross-project discovery** | All repos | Each Claude session starts blind. Builds duplicates of what other sessions already made. |
| 7 | **No shared state between sessions** | All repos | The Brain/R2 system was designed to fix this but was never deployed. |
| 8 | **MCPB system is a zip on the desktop** | C:\Users\kenws\Downloads\ | 35 files, 56 tests, not in any repo, not deployed. Could get deleted accidentally. |
| 9 | **HUD and Polar MCP share a repo but different branches** | vite-react-template | Merging them will conflict. They should either be combined intentionally or separated into their own repos. |
| 10 | **Google Cloud credits expiring unused** | GCP | $1,300+ in free compute/tokens going to waste. |

### MEDIUM (quality and completeness)

| # | Gap | Where | Impact |
|---|-----|-------|--------|
| 11 | **HUD LLM responses are fake** | HUD:OS | Simulated hardcoded responses, no real AI. |
| 12 | **2 of 5 MCPB kits are stubs** | MCPB | Vision and Action kits return fake data. Tests pass but test fake behavior. |
| 13 | **Go QUIC server not compiled** | MCPB | Code exists but was never built. |
| 14 | **Constitution v1.1 and v1.2 coexist** | Symphony Architect prompt | Two versions in the same document. Constitutional violations embedded in the constitution itself. |
| 15 | **r2-writer returning 1101** | Vagblaster account | Listed as #1 triage item. Blocks writes to R2. |

### LOW (cleanup and naming)

| # | Gap | Where | Impact |
|---|-----|-------|--------|
| 16 | **Repo named vite-react-template, project is HUD:OS** | vite-react-template | Confusing. |
| 17 | **Polar branch says NCP not MCP** | vite-react-template | Typo in branch name. |
| 18 | **API /api/diag says 8GB, lore says 24GB** | HUD:OS | Inconsistency between code and world-building. |
| 19 | **Duplicate filesystem implementations** | HUD:OS | FileSystemUI.tsx (active) and FileSystemPanel.tsx (standalone). |

---

## WHAT SHOULD BE BUILT IN THIS REPO

This is the only project with Go containers, Durable Objects, and SQLite. It should become the **persistent backend** for the system. Specifically:

### 1. State API (uses the unused SQLite)
```
POST   /api/state/:namespace/:key   → write state
GET    /api/state/:namespace/:key   → read state
DELETE /api/state/:namespace/:key   → delete state
GET    /api/state/:namespace        → list keys in namespace
```
Namespaces: `hud`, `polar`, `brain`, `mcpb`, `sessions`

This gives every other project a persistence layer. HUD saves panel state. Polar MCP saves variables/skills. Brain saves session context.

### 2. Health endpoint (Go container)
```
GET /health → { status: "ok", uptime: "...", container_id: "..." }
```

### 3. Lifecycle event persistence
onStart/onStop/onError write to SQLite instead of console.log. Queryable history of container lifecycle.

### 4. Job queue (async work)
```
POST /api/jobs           → submit job → returns job_id
GET  /api/jobs/:id       → check status/result
GET  /api/jobs?status=pending → list pending jobs
```
Container polls for pending jobs, processes them, writes results back.

---

## OWNER PREFERENCES (for any AI reading this)

- **No fancy names** — no "Illusioner", no "Sandstorm", no metaphor-heavy naming. Plain English.
- **No GitHub explanations** — the owner doesn't use GitHub directly and doesn't want to learn it right now.
- **Outputs must be visible and clickable** — if it can't be opened in a browser or pasted somewhere, it effectively doesn't exist.
- **Don't duplicate work** — check WHAT_WE_BUILT.md or this manifest before building anything. Another Claude probably already made it.
- **Don't waste coins on theory** — build deployable things or don't build.
- **Coordinate across sessions** — write to shared files (brain-seed/, WHAT_WE_BUILT.md, this manifest) so the next session isn't blind.
- **The system has 3 Cloudflare accounts and a full GCP stack** — use them, don't suggest buying more infrastructure.
- **Speech-to-text artifacts are common** — "badge blaster" = vagblaster, "quad code" = Claude Code, etc.

---

## KNOWN BROKEN (from Symphony Architect triage list)

1. r2-writer 1101 (Vagblaster account)
2. Memory bridge auth missing
3. No hydrate/checkpoint automation
4. Binary overcorrection in agents
5. RPTE automation missing
6. GCP service account JSON not deployed
7. Polar MCP not integrated
8. Skills not written
9. Slack bus not wired
10. Vertex pipeline empty

---

## RELAY THIS TO OTHER AIs

Copy this entire file. It contains:
- What this specific project is (containers-template — stock starter, barely modified)
- What the entire system looks like (8 pieces, none connected)
- Every gap across all projects (19 items, prioritized)
- What should be built here specifically (state API, health, lifecycle, job queue)
- Owner preferences and communication style
- Account topology (3 Cloudflare accounts + GCP)
- Credits expiring ($1,300+ in GCP)
