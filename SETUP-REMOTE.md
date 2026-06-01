# Remote Routine Setup (claude.ai cloud)

This project runs as three scheduled **remote routines** on Anthropic's cloud infrastructure.
The code lives in this GitHub repo; secrets live in the cloud **environment** (never in the repo
or in a prompt).

## One-time web-UI configuration

At https://claude.ai/code/routines, open the environment used by these routines and configure:

### 1. Environment variables (secrets)
Add these three variables (paper keys only):
```
APCA_API_KEY_ID       = <your paper key id>
APCA_API_SECRET_KEY   = <your paper secret>
APCA_BASE_URL         = https://paper-api.alpaca.markets
```
The Python scripts read these via `os.getenv(...)`, so no code changes are needed.

### 2. Network access
The Default "Trusted" policy blocks Alpaca's hosts. Set Network access → **Custom** and add:
```
paper-api.alpaca.markets
data.alpaca.markets
```
Keep "include default list of common package managers" checked so `pip install` still works.

### 3. Setup script
```
pip install -r requirements.txt
```
(Result is cached between runs.)

### 4. Branch pushes (for the journal)
To let the routines commit daily journal entries straight to `main`, enable
**Allow unrestricted branch pushes** for this repository in the routine's Permissions tab.
Otherwise journal changes arrive as PRs on `claude/`-prefixed branches.

## Schedule (UTC cron) — DST WARNING

The strategy is anchored to New York market hours. Crons are fixed UTC:

| Routine            | ET time   | EDT cron (Mar–Nov) | EST cron (Nov–Mar) |
|--------------------|-----------|--------------------|--------------------|
| Morning Research   | 9:45 AM   | `45 13 * * 1-5`    | `45 14 * * 1-5`    |
| Trading Session    | 10:00 AM  | `0 14 * * 1-5`     | `0 15 * * 1-5`     |
| End-of-Day Journal | 4:15 PM   | `15 20 * * 1-5`    | `15 21 * * 1-5`    |

⚠️ Cron does not auto-adjust for US daylight saving. When the US switches between EDT and EST,
update each routine's cron (`/schedule update`) by ±1 hour using the table above. Currently set
for **EDT** (summer).

## Verifying a run
A green status only means the session started without infra error — open the run transcript to
confirm the task actually succeeded (e.g. that Alpaca calls returned 200, not 403 host_not_allowed).
