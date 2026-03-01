import { Container, getContainer, getRandom } from "@cloudflare/containers";
import { Hono } from "hono";

export class MyContainer extends Container<Env> {
	defaultPort = 8080;
	sleepAfter = "2m";
	envVars = {
		MESSAGE: "I was passed in via the container class!",
	};

	private ensureTables() {
		this.ctx.storage.sql.exec(`
			CREATE TABLE IF NOT EXISTS state (
				namespace TEXT NOT NULL,
				key TEXT NOT NULL,
				value TEXT NOT NULL,
				updated_at TEXT NOT NULL DEFAULT (datetime('now')),
				PRIMARY KEY (namespace, key)
			)
		`);
		this.ctx.storage.sql.exec(`
			CREATE TABLE IF NOT EXISTS lifecycle_events (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				event TEXT NOT NULL,
				detail TEXT,
				timestamp TEXT NOT NULL DEFAULT (datetime('now'))
			)
		`);
	}

	override onStart() {
		this.ensureTables();
		this.ctx.storage.sql.exec(
			`INSERT INTO lifecycle_events (event, detail) VALUES ('start', 'Container started')`,
		);
	}

	override onStop() {
		try {
			this.ensureTables();
			this.ctx.storage.sql.exec(
				`INSERT INTO lifecycle_events (event, detail) VALUES ('stop', 'Container stopped')`,
			);
		} catch {
			// DO may be shutting down
		}
	}

	override onError(error: unknown) {
		try {
			this.ensureTables();
			const msg = error instanceof Error ? error.message : String(error);
			this.ctx.storage.sql.exec(
				`INSERT INTO lifecycle_events (event, detail) VALUES ('error', ?)`,
				msg,
			);
		} catch {
			// Best effort
		}
	}

	override async fetch(request: Request): Promise<Response> {
		const url = new URL(request.url);

		if (url.pathname.startsWith("/state/")) {
			return this.handleState(request, url);
		}

		if (url.pathname === "/events") {
			return this.handleEvents(url);
		}

		if (url.pathname === "/do-health") {
			return this.handleHealth();
		}

		return super.fetch(request);
	}

	private async handleState(
		request: Request,
		url: URL,
	): Promise<Response> {
		this.ensureTables();
		const stripped = url.pathname.replace("/state/", "");
		const slashIdx = stripped.indexOf("/");
		const namespace = slashIdx === -1 ? stripped : stripped.substring(0, slashIdx);
		const key = slashIdx === -1 ? "" : stripped.substring(slashIdx + 1);

		if (request.method === "GET") {
			if (!key) {
				const rows = this.ctx.storage.sql
					.exec(
						`SELECT key, value, updated_at FROM state WHERE namespace = ?`,
						namespace,
					)
					.toArray();
				return Response.json({ namespace, entries: rows });
			}
			const rows = this.ctx.storage.sql
				.exec(
					`SELECT value, updated_at FROM state WHERE namespace = ? AND key = ?`,
					namespace,
					key,
				)
				.toArray();
			if (rows.length === 0) {
				return Response.json({ error: "not_found" }, { status: 404 });
			}
			return Response.json({ namespace, key, ...rows[0] });
		}

		if (request.method === "POST" || request.method === "PUT") {
			const body = (await request.json()) as { value: unknown };
			const val =
				typeof body.value === "string"
					? body.value
					: JSON.stringify(body.value);
			this.ctx.storage.sql.exec(
				`INSERT OR REPLACE INTO state (namespace, key, value, updated_at) VALUES (?, ?, ?, datetime('now'))`,
				namespace,
				key,
				val,
			);
			return Response.json({ namespace, key, status: "written" });
		}

		if (request.method === "DELETE") {
			this.ctx.storage.sql.exec(
				`DELETE FROM state WHERE namespace = ? AND key = ?`,
				namespace,
				key,
			);
			return Response.json({ namespace, key, status: "deleted" });
		}

		return Response.json({ error: "method_not_allowed" }, { status: 405 });
	}

	private handleEvents(url: URL): Response {
		this.ensureTables();
		const limit = parseInt(url.searchParams.get("limit") || "50");
		const rows = this.ctx.storage.sql
			.exec(
				`SELECT id, event, detail, timestamp FROM lifecycle_events ORDER BY id DESC LIMIT ?`,
				limit,
			)
			.toArray();
		return Response.json({ events: rows });
	}

	private handleHealth(): Response {
		return Response.json({
			status: "ok",
			timestamp: new Date().toISOString(),
			container_id: this.ctx.id.toString(),
		});
	}
}

const app = new Hono<{ Bindings: Env }>();

// Home route listing all endpoints
app.get("/", (c) => {
	return c.json({
		name: "containers-template",
		version: "0.1.0",
		endpoints: {
			containers: {
				"GET /container/:id": "Route to specific container instance",
				"GET /singleton": "Single persistent container instance",
				"GET /lb": "Load balance across 3 containers",
				"GET /error": "Error handling demo (forces panic)",
			},
			state: {
				"GET /api/state/:ns": "List all keys in namespace",
				"GET /api/state/:ns/:key": "Read a key",
				"POST /api/state/:ns/:key": "Write a key (body: {value: ...})",
				"DELETE /api/state/:ns/:key": "Delete a key",
			},
			lifecycle: {
				"GET /api/events": "Container lifecycle events (?limit=N)",
			},
			health: {
				"GET /api/health": "Durable Object health check",
				"GET /api/container-health": "Go container health check",
			},
		},
	});
});

// --- State API (proxied through singleton DO) ---

app.get("/api/state/:namespace", async (c) => {
	const ns = c.req.param("namespace");
	const container = getContainer(c.env.MY_CONTAINER, "state-store");
	const res = await container.fetch(
		new Request(`http://internal/state/${ns}`),
	);
	return new Response(res.body, res);
});

app.get("/api/state/:namespace/:key", async (c) => {
	const ns = c.req.param("namespace");
	const key = c.req.param("key");
	const container = getContainer(c.env.MY_CONTAINER, "state-store");
	const res = await container.fetch(
		new Request(`http://internal/state/${ns}/${key}`),
	);
	return new Response(res.body, res);
});

app.post("/api/state/:namespace/:key", async (c) => {
	const ns = c.req.param("namespace");
	const key = c.req.param("key");
	const container = getContainer(c.env.MY_CONTAINER, "state-store");
	const res = await container.fetch(
		new Request(`http://internal/state/${ns}/${key}`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: await c.req.text(),
		}),
	);
	return new Response(res.body, res);
});

app.delete("/api/state/:namespace/:key", async (c) => {
	const ns = c.req.param("namespace");
	const key = c.req.param("key");
	const container = getContainer(c.env.MY_CONTAINER, "state-store");
	const res = await container.fetch(
		new Request(`http://internal/state/${ns}/${key}`, { method: "DELETE" }),
	);
	return new Response(res.body, res);
});

// --- Lifecycle Events ---

app.get("/api/events", async (c) => {
	const limit = c.req.query("limit") || "50";
	const container = getContainer(c.env.MY_CONTAINER, "state-store");
	const res = await container.fetch(
		new Request(`http://internal/events?limit=${limit}`),
	);
	return new Response(res.body, res);
});

// --- Health Checks ---

app.get("/api/health", async (c) => {
	const container = getContainer(c.env.MY_CONTAINER, "state-store");
	const res = await container.fetch(
		new Request("http://internal/do-health"),
	);
	return new Response(res.body, res);
});

app.get("/api/container-health", async (c) => {
	try {
		const container = getContainer(c.env.MY_CONTAINER, "health-check");
		const res = await container.fetch(
			new Request("http://internal/health"),
		);
		return new Response(res.body, res);
	} catch (err) {
		return c.json(
			{
				status: "error",
				message: err instanceof Error ? err.message : "container unreachable",
			},
			503,
		);
	}
});

// --- Original container routing (preserved) ---

app.get("/container/:id", async (c) => {
	const id = c.req.param("id");
	const containerId = c.env.MY_CONTAINER.idFromName(`/container/${id}`);
	const container = c.env.MY_CONTAINER.get(containerId);
	return await container.fetch(c.req.raw);
});

app.get("/error", async (c) => {
	const container = getContainer(c.env.MY_CONTAINER, "error-test");
	return await container.fetch(c.req.raw);
});

app.get("/lb", async (c) => {
	const container = await getRandom(c.env.MY_CONTAINER, 3);
	return await container.fetch(c.req.raw);
});

app.get("/singleton", async (c) => {
	const container = getContainer(c.env.MY_CONTAINER);
	return await container.fetch(c.req.raw);
});

export default app;
