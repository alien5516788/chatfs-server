# ChatFS Server

This is the **server-side component** for ChatFS.

It acts as a lightweight relay between:

* a web-based AI (Grok, Qwen, etc.)
* your local machine running the ChatFS client

---

## Looking for the actual tool?

You probably want the **client repo**:

> [ChatFS - client](https://github.com/alien5516788/chatfs)

That’s the part you run locally to share your workspace.

This repo is just the server that sits in between.

---

## What this server does

* exposes simple URL-based endpoints for LLMs
* maintains WebSocket connections with clients
* forwards requests → client → response → back to LLM

It intentionally stays **very thin**.
All filesystem logic and safety checks happen in the client.

---

## Self-hosting (recommended)

You can run your own server instead of using a public one.

This is recommended if you care about:

* privacy
* control over sessions
* not sending requests through external infrastructure

---

## Requirements

* Python **3.12**
* `pip`

---

## Setup (using PDM)

### 1. Clone the repo

```bash
git clone <REPO_URL>
cd chatfs-server
```

---

### 2. Install dependencies

If you don’t have PDM:

```bash
pip install pdm
```

Then:

```bash
pdm install
```

---

### 3. Run the server

```bash
pdm run start
```

Server will start on:

```
http://0.0.0.0:8000
```

---

## Deployment note (Render, etc.)

If your platform doesn’t have PDM preinstalled, use the provided [`build.sh`](./build.sh):

```bash
bash build.sh
```

Then use this as your start command:

```bash
pdm run start
```

---

## How it connects

* Client connects via WebSocket → `/client/`
* LLM sends requests → `/{client_id}/...`
* Server forwards everything to the correct client session

---

## Gateway URL (Web Socket)

The client connects to the server using a **WebSocket gateway URL**.

This URL is created by:

1. taking your server URL
2. appending the client endpoint (`/client/`)
3. converting the protocol from HTTP → WebSocket

Examples,

If the server URL is `http://your-server.com/`,

```text
http://your-server.com/client/
```

becomes:

```text
ws://your-server.com/client/
```

For HTTPS servers,

```text
https://your-server.com/client/
```

becomes:

```text
wss://your-server.com/client/
```

For local development servers,

```text
http://localhost:8000
```

becomes:

```text
ws://localhost:8000/client/
```

---

## Notes

* This server does **not** enforce filesystem safety
* All validation happens in the client
* Treat this as a relay layer, not a secure boundary

---

## Privacy

If you use a public server, your requests pass through it.

For better privacy:

> run your own instance and point the client to it
