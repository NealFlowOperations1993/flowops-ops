"""
Smartlead API helpers for inbound + outbound reply handling.

Exposed:
  - get_lead_thread(campaign_id, lead_id) → list of messages (for context)
  - get_lead_by_email(email) → {campaign_id, lead_id, lead_data}
  - get_last_outbound(campaign_id, lead_id) → the SENT message we want to reply to
  - send_reply(campaign_id, stats_id, reply_message_id, to_email, to_first_name, body) → bool, status
  - mark_lead_status(campaign_id, lead_id, status) → bool
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any
import os

API_KEY = os.environ["SMARTLEAD_API_KEY"]
BASE = "https://server.smartlead.ai/api/v1"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"


def _get(path: str, params: dict | None = None) -> Any:
    qs = {"api_key": API_KEY}
    if params:
        qs.update(params)
    url = f"{BASE}{path}?{urllib.parse.urlencode(qs)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def _post(path: str, body: dict, params: dict | None = None) -> Any:
    qs = {"api_key": API_KEY}
    if params:
        qs.update(params)
    url = f"{BASE}{path}?{urllib.parse.urlencode(qs)}"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "User-Agent": UA,
            "Accept": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read().decode()
        # Smartlead's reply-email-thread returns plain text "Email added to queue..."
        # not JSON. Tolerate both.
        try:
            return r.status, json.loads(raw)
        except json.JSONDecodeError:
            return r.status, {"message": raw}


def get_lead_thread(campaign_id: int, lead_id: int) -> list[dict]:
    """Pull full message history for one lead in a campaign."""
    data = _get(f"/campaigns/{campaign_id}/leads/{lead_id}/message-history")
    if isinstance(data, dict) and "history" in data:
        return data["history"]
    return data if isinstance(data, list) else []


def get_lead_by_email(email: str, campaign_id: int | None = None) -> dict | None:
    """
    Find a lead by email. The Smartlead /leads/ endpoint returns a flat dict
    with the lead at top level. Returns {"campaign_id", "lead_id", "lead_data"} or None.
    """
    try:
        data = _get("/leads/", {"email": email})
    except Exception as e:
        print(f"  [smartlead] lead lookup error: {e}")
        return None

    # The endpoint returns the lead record at top level (id, email, custom_fields, etc.)
    if isinstance(data, dict) and data.get("id"):
        return {
            "campaign_id": campaign_id,
            "lead_id":     data.get("id"),
            "lead_data":   data,
        }
    # List form (rare but possible)
    if isinstance(data, list) and data:
        ld = data[0]
        return {
            "campaign_id": campaign_id,
            "lead_id":     ld.get("id"),
            "lead_data":   ld,
        }
    return None


def get_last_outbound(campaign_id: int, lead_id: int) -> dict | None:
    """
    Returns metadata of the last SENT email in the thread:
      {"stats_id", "message_id", "subject", "sent_time", "from_email"}
    """
    msgs = get_lead_thread(campaign_id, lead_id)
    sent = [m for m in msgs if (m.get("type") or m.get("email_type") or "").upper() == "SENT"]
    if not sent:
        return None
    # newest first
    sent.sort(key=lambda m: m.get("time") or m.get("created_at") or "", reverse=True)
    m = sent[0]
    return {
        "stats_id":    m.get("stats_id") or m.get("email_stats_id"),
        "message_id":  m.get("message_id"),
        "subject":     m.get("subject"),
        "sent_time":   m.get("time") or m.get("created_at"),
        "from_email":  m.get("from") or m.get("from_email"),
    }


def send_reply(
    campaign_id: int,
    stats_id: str,
    reply_message_id: str,
    to_email: str,
    body_plain: str,
    to_first_name: str = "",
    reply_email_time: str = "",
    reply_email_body: str = "",
) -> tuple[bool, str]:
    """
    Post a reply onto an existing Smartlead thread.
    Returns (ok, status_message).
    """
    payload = {
        "email_stats_id":    stats_id,
        "email_body":        body_plain.replace("\n", "<br/>"),
        "reply_message_id":  reply_message_id,
        "reply_email_time":  reply_email_time or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "reply_email_body":  reply_email_body or "(inbound reply)",
        "to_email":          to_email,
        "to_first_name":     to_first_name,
    }
    try:
        status, resp = _post(f"/campaigns/{campaign_id}/reply-email-thread", payload)
        ok = status == 200
        return ok, json.dumps(resp)[:200] if isinstance(resp, dict) else str(resp)[:200]
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        return False, str(e)[:200]


def mark_lead_status(campaign_id: int, lead_id: int, status: str) -> bool:
    """
    Update lead status in Smartlead. Statuses: INTERESTED, MEETING_BOOKED, NOT_INTERESTED,
    INFORMATION_REQUEST, DO_NOT_CONTACT, WRONG_PERSON, OUT_OF_OFFICE.
    """
    try:
        st, _ = _post(
            f"/campaigns/{campaign_id}/leads/{lead_id}/category",
            {"category": status},
        )
        return st == 200
    except Exception as e:
        print(f"  [smartlead] mark_lead_status error: {e}")
        return False


if __name__ == "__main__":
    # Smoke test: pull Ralph's thread
    print("Pulling Ralph's thread (MCA campaign 3263732, lead 3725290207)...")
    msgs = get_lead_thread(3263732, 3725290207)
    print(f"  {len(msgs)} messages in thread")
    for m in msgs:
        t = m.get("type") or m.get("email_type") or "?"
        s = (m.get("subject") or "")[:60]
        when = m.get("time") or m.get("created_at") or ""
        print(f"    [{t:<8}] {when[:19]}  {s}")
    print()
    last = get_last_outbound(3263732, 3725290207)
    print(f"Last outbound: {last}")
