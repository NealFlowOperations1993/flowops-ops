# Auto-Reply System — Deploy Guide

End-to-end pipeline that turns inbound POSITIVE replies into booked GHL calls without Neal in the loop.

## What it does

1. Smartlead fires `EMAIL_REPLY` webhook the second a lead replies
2. Webhook server classifies the reply with Haiku (~200ms, $0.0007 per reply)
3. If `POSITIVE` and confidence >= 0.75 → Haiku drafts a contextual reply with the GHL booking link inline (~800ms, $0.004)
4. Reply auto-sent via Smartlead reply API into the same thread (~500ms)
5. Lead status flipped to `INTERESTED` in Smartlead
6. Slack alert fired to Neal (FYI, not action-required)

**Total latency: ~3-5 seconds from reply → outbound auto-response.**
**Cost per inbound reply: ~$0.005.**

Anything that's not high-confidence POSITIVE (NEUTRAL / NEGATIVE / OOO / UNSUB) routes to Slack for Neal to handle.

## Files

```
council/
├── core/
│   ├── reply_classifier.py     # Haiku one-shot label classifier
│   ├── auto_reply.py           # Haiku contextual reply drafter (with voice rules)
│   ├── smartlead_io.py         # Smartlead API helpers (thread fetch, reply send, status update)
│   ├── slack_alert.py          # Slack helper (no-ops without token)
│   └── reply_orchestrator.py   # The pipeline; one function: handle_inbound_reply()
└── webhook_server.py           # FastAPI receiver
```

## Local smoke test (do this first)

```bash
cd ~/Desktop/council
.venv-server/bin/uvicorn webhook_server:app --host 127.0.0.1 --port 8787 --log-level warning &

# Health
curl http://127.0.0.1:8787/

# Dry run (no actual send) on Ralph's payload
curl -X POST http://127.0.0.1:8787/test/dry-run \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": 3263732,
    "lead_id": 3725290207,
    "to_email": "ralph@firstchoicedebtsolutions.org",
    "to_name": "Ralph",
    "reply_message": "Sure"
  }'
```

You'll get back the full classified+drafted event including the body of the reply that *would* have sent. Verify the draft looks good before going live.

## Production deploy

### Option A — ngrok (fastest, ephemeral)

```bash
# Terminal 1
cd ~/Desktop/council
.venv-server/bin/uvicorn webhook_server:app --host 0.0.0.0 --port 8787

# Terminal 2
ngrok http 8787
# Copy the https://xxxx.ngrok-free.app URL
```

Caveat: ngrok URL changes each restart. Free tier sessions expire.

### Option B — Cloudflare Tunnel (free, stable)

```bash
# Install
brew install cloudflared
cloudflared tunnel login

# Create persistent tunnel
cloudflared tunnel create council-replies
cloudflared tunnel route dns council-replies replies.flowoperations.org
cloudflared tunnel run --url http://127.0.0.1:8787 council-replies
```

You get `https://replies.flowoperations.org` permanently.

### Option C — Fly.io or Railway (cheapest, hands-off)

Fly is ~$2/mo, deploy with one Dockerfile:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn
ENV BRUTUS_BOT_TOKEN=""  # set in Fly dashboard
CMD ["uvicorn", "webhook_server:app", "--host", "0.0.0.0", "--port", "8787"]
```

```bash
fly launch
fly deploy
```

## Smartlead webhook config

Once the server is reachable:

1. Smartlead dashboard → **Settings → Webhooks → Add Webhook**
2. Event: `EMAIL_REPLY` (also enable `EMAIL_REPLY_RECEIVED` if available)
3. URL: `https://<your-public-host>/webhook/smartlead-reply`
4. Method: POST
5. Save + test with the "Send Test Webhook" button

## Environment variables (Neal to set)

```bash
# Required for Slack alerts (no-ops gracefully without)
export BRUTUS_BOT_TOKEN="xoxb-..."
export SLACK_REPLY_CHANNEL="#1-new-lead"   # or whatever channel
```

## Monitoring

- `GET /recent?limit=50` — last N reply events with classification + decision
- All events also write to `~/.council/reply_events.jsonl` for offline analysis

## Safety guardrails baked in

- Only `POSITIVE` with confidence >= 0.75 triggers auto-reply. Everything else routes to Neal.
- HUMAN_VOICE.md rules enforced post-generation (em-dashes stripped, banned phrases flagged).
- Booking URL hard-checked: if Haiku drops it from the body, system appends it before send.
- All sends go through Smartlead reply API (not raw SMTP) so deliverability stays clean.
- Dry-run mode for testing without sending.

## What's NOT in scope (yet)

- GHL booking webhook → pre-call brief generator (separate task)
- Multi-language reply support (currently English only)
- Negative reply auto-handling (intentionally Neal-only)
- Twilio SMS alert (waits on Twilio creds; Slack alone is fine for now)
