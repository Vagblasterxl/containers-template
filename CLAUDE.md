# CLAUDE.md - Cloudflare Containers Template

This document provides essential context for AI assistants working with this codebase.

## Project Overview

This is a **Cloudflare Containers Starter Template** demonstrating how to build and deploy containerized applications using Cloudflare's Workers, Containers, and Durable Objects services. It combines a TypeScript-based Cloudflare Worker for orchestration with a Go-based container for workload execution.

## Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Worker Runtime | Cloudflare Workers | - |
| Web Framework | Hono | 4.11.1 |
| Language (Worker) | TypeScript | 5.9.3 |
| Language (Container) | Go | 1.24 |
| Container Runtime | Cloudflare Containers | 0.0.30 |
| State Management | Durable Objects | - |
| CLI Tool | Wrangler | 4.56.0 |

## Project Structure

```
containers-template/
├── src/
│   └── index.ts              # Main Worker code with Hono app and Container class
├── container_src/
│   ├── main.go               # Go HTTP server running inside the container
│   └── go.mod                # Go module definition
├── Dockerfile                # Multi-stage Docker build for Go container
├── wrangler.jsonc            # Wrangler configuration (Workers, Containers, DOs)
├── tsconfig.json             # TypeScript configuration
├── worker-configuration.d.ts # Auto-generated Cloudflare types
├── package.json              # Node.js dependencies and scripts
└── README.md                 # User-facing documentation
```

## Key Files

### `src/index.ts` - Worker Entry Point
- Defines `MyContainer` class extending `Container<Env>` base class
- Configures container port (8080), sleep timeout (2m), and environment variables
- Implements lifecycle hooks: `onStart()`, `onStop()`, `onError()`
- Creates Hono web app with routing patterns for container orchestration

### `container_src/main.go` - Container Application
- Go HTTP server listening on port 8080
- Implements graceful shutdown (SIGINT/SIGTERM with 5s timeout)
- Routes: `/` and `/container` for normal requests, `/error` for panic testing
- Accesses `MESSAGE` and `CLOUDFLARE_DURABLE_OBJECT_ID` environment variables

### `wrangler.jsonc` - Cloudflare Configuration
- Defines container class `MyContainer` with max 10 instances
- Binds Durable Object `MY_CONTAINER` to the container class
- Enables observability and source map uploads
- Sets compatibility date 2025-10-08 with `nodejs_compat` flag

### `Dockerfile` - Container Build
- Multi-stage build: `golang:1.24-alpine` for build, `scratch` for runtime
- Produces minimal image with only the Go binary and CA certificates
- Exposes port 8080

## Development Commands

```bash
# Install dependencies
npm install

# Start local development server (http://localhost:8787)
npm run dev
# or
npm run start

# Deploy to Cloudflare
npm run deploy

# Regenerate TypeScript types from wrangler config
npm run cf-typegen
```

## Architecture Patterns

### Container Class Pattern
```typescript
export class MyContainer extends Container<Env> {
  defaultPort = 8080;           // Container listening port
  sleepAfter = "2m";            // Auto-sleep after inactivity
  envVars = { ... };            // Environment variables to pass

  override onStart() { ... }    // Called when container starts
  override onStop() { ... }     // Called when container stops
  override onError(error) { ... } // Called on container error
}
```

### Routing Patterns

| Route | Pattern | Helper Function |
|-------|---------|-----------------|
| `/container/:id` | Parameterized routing | `c.env.MY_CONTAINER.idFromName()` |
| `/singleton` | Single instance | `getContainer(env.MY_CONTAINER)` |
| `/lb` | Load balancing (3 instances) | `getRandom(env.MY_CONTAINER, 3)` |
| `/error` | Error handling demo | `getContainer(env.MY_CONTAINER, "error-test")` |

### Hono App Pattern
```typescript
const app = new Hono<{ Bindings: Env }>();
app.get("/route", async (c) => {
  // c.env - access bindings (MY_CONTAINER, etc.)
  // c.req - request object
  // c.text(), c.json(), etc. - response helpers
});
export default app;
```

## Code Conventions

### TypeScript (Worker)
- Use `Env` type from auto-generated `worker-configuration.d.ts`
- Use generic typing: `Hono<{ Bindings: Env }>`, `Container<Env>`
- Use `override` keyword for lifecycle hooks
- Prefer Hono's context helpers (`c.text()`, `c.json()`) for responses
- Use async/await for container fetch operations

### Go (Container)
- Use standard library `net/http` for HTTP handling
- Implement graceful shutdown with signal handling
- Access configuration via `os.Getenv()`
- Use `http.NewServeMux()` for routing

### General
- Keep dependencies minimal
- Use multi-stage Docker builds for small images
- Configure container behavior through class properties, not hardcoded values
- Use Durable Object IDs for container instance routing

## Important Environment Variables

### Automatically Injected (Container)
- `CLOUDFLARE_DURABLE_OBJECT_ID` - Unique ID of the Durable Object instance

### Configurable (via Container class)
- `MESSAGE` - Example custom variable passed to container

## Testing

No testing framework is currently configured. When adding tests:
- Consider Vitest for Worker/TypeScript tests
- Consider Go's built-in `testing` package for container tests
- Mock Cloudflare bindings using `miniflare` or `@cloudflare/vitest-pool-workers`

## Deployment

1. Ensure you have Cloudflare account with Containers access
2. Run `npm run deploy`
3. Wrangler builds TypeScript, Docker image, and deploys both
4. Container images are stored in Cloudflare's container registry

## Common Tasks

### Adding a New Route
1. Add route handler in `src/index.ts` using Hono's `app.get()`, `app.post()`, etc.
2. Use `getContainer()` or `getRandom()` helpers for container access
3. Call `container.fetch()` to forward requests to the container

### Adding Container Endpoints
1. Add handler function in `container_src/main.go`
2. Register route with `router.HandleFunc("/path", handler)`
3. Rebuild and deploy

### Modifying Container Configuration
- Edit class properties in `MyContainer` (port, sleep timeout, env vars)
- For max instances, edit `wrangler.jsonc` containers config

### Regenerating Types
Run `npm run cf-typegen` after modifying `wrangler.jsonc` to update TypeScript types.

## Gotchas

- Container sleep timeout uses string format: `"30s"`, `"2m"`, `"1h"`
- Durable Object bindings must match between `wrangler.jsonc` and class exports
- Container must export from the same file as the Hono app (`src/index.ts`)
- Docker build context is the project root, not `container_src/`
- The `scratch` base image has no shell - debug by switching to `alpine` temporarily
