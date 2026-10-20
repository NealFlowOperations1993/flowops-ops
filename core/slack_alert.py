"""
Slack alert helper. No-ops gracefully if BRUTUS_BOT_TOKEN env var is missing.

Used by reply_orchestrator to send Neal FYI pings about auto-replies and
flagged-to-Neal events.
"""
import json
import os
import urllib.request
import urllib.error

BRUTUS_TOKEN = os.environ.get("BRUTUS_BOT_TOKEN", "")
DEFAULT_CHANNEL = os.environ.get("SLACK_REPLY_CHANNEL", "#1-new-lead")


def post(text: str, channel: str = "", blocks: list | None = None) -> bool:
    """Post to Slack. Returns True on success, False otherwise (or no-token)."""
    if not BRUTUS_TOKEN:
        print(f"  [slack-noop] {text[:120]}")
        return False

    payload = {
        "channel":  channel or DEFAULT_CHANNEL,
        "text":     text,
        "unfurl_links": False,
    }
    if blocks:
        payload["blocks"] = blocks

    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {BRUTUS_TOKEN}",
            "Content-Type":  "application/json; charset=utf-8",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            resp = json.loads(r.read().decode())
            return bool(resp.get("ok"))
    except Exception as e:
        print(f"  [slack-error] {e}")
        return False


def reply_alert(event: dict) -> None:
    """
    Format and send a reply event log as a Slack message.
    event is the dict returned by reply_orchestrator.handle_inbound_reply.
    """
    decision = event.get("decision", "?")
    email    = event.get("lead_email", "?")
    name     = event.get("lead_first_name") or "?"
    company  = event.get("lead_company") or "?"
    niche    = event.get("niche", "?")
    label    = (event.get("classification") or {}).get("label", "?")
    inbound  = (event.get("inbound_text") or "")[:300]

    icon = {
        "AUTO_REPLIED":    ":white_check_mark:",
        "FLAGGED_TO_NEAL": ":eyes:",
        "UNSUB":           ":wave:",
        "ERROR":           ":warning:",
        "DRY_RUN_OK":      ":test_tube:",
    }.get(decision, ":bell:")

    header = f"{icon} *{decision}*  {name} ({email})  [{niche}]  -> {label}"
    body   = f"```\n{inbound}\n```"

    extras = []
    if decision == "AUTO_REPLIED":
        draft_body = (event.get("draft") or {}).get("body_plain", "")[:400]
        extras.append(f"*Sent reply:*\n```\n{draft_body}\n```")
    elif decision == "FLAGGED_TO_NEAL":
        extras.append(f"_Neal: open Smartlead and reply manually if this looks worth pursuing._")

    text = "\n".join([header, body] + extras)
    post(text)


if __name__ == "__main__":
    # Smoke
    post("Brutus alert test: reply system online.")
