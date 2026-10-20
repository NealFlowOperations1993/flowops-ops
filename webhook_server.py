"""
FastAPI webhook receiver for Smartlead EMAIL_REPLY events.

Run:
  pip install fastapi uvicorn
  uvicorn webhook_server:app --host 0.0.0.0 --port 8787

Expose publicly (one option):
  ngrok http 8787
  -> copy the https URL into Smartlead settings -> Webhooks -> EMAIL_REPLY

Smartlead EMAIL_REPLY payload (approx schema):
  {
    "event_type": "EMAIL_REPLY",
    "campaign_id": 3263732,
    "lead_id": 3725290207,
    "to_email": "ralph@firstchoicedebtsolutions.org",
    "to_name": "Ralph",
    "reply_message": "Sure",
    "reply_subject": "Re: ...",
    "sl_lead_email": "ralph@firstchoicedebtsolutions.org",
    "sl_company": "First Choice Debt Solutions",
    ...
  }
"""
import json
import os
import threading
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from core.reply_orchestrator import handle_inbound_reply

app = FastAPI(title="Council Reply Webhook", version="1.1")

# Optional: log every event to a local JSONL for debugging / replay
LOG_PATH = os.path.expanduser("~/.council/reply_events.jsonl")
BOOKINGS_PATH = os.path.expanduser("~/.council/bookings.jsonl")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
_log_lock = threading.Lock()
_bookings_lock = threading.Lock()


def _append_log(entry: dict) -> None:
    try:
        with _log_lock, open(LOG_PATH, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception as e:
        print(f"[log-error] {e}")


def _append_booking(entry: dict) -> None:
    try:
        with _bookings_lock, open(BOOKINGS_PATH, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception as e:
        print(f"[booking-log-error] {e}")


@app.get("/")
def health():
    return {"ok": True, "service": "council-reply-webhook"}


@app.post("/webhook/smartlead-reply")
async def smartlead_reply(request: Request, background: BackgroundTasks):
    """
    Smartlead webhook receiver. Acks immediately, processes async.
    """
    try:
        payload = await request.json()
    except Exception as e:
        return JSONResponse({"ok": False, "error": f"bad json: {e}"}, status_code=400)

    # Validate the bits we need; Smartlead's payload shape can vary by event flavor.
    campaign_id = payload.get("campaign_id") or payload.get("sl_campaign_id")
    lead_id     = payload.get("lead_id")     or payload.get("sl_lead_id")
    email       = payload.get("to_email")    or payload.get("sl_lead_email")
    reply_text  = payload.get("reply_message") or payload.get("sl_message_text") or ""

    if not all([campaign_id, lead_id, email, reply_text]):
        _append_log({"event": "rejected", "reason": "missing fields", "payload": payload})
        return JSONResponse(
            {"ok": False, "error": "missing required fields",
             "got": {k: bool(v) for k, v in
                     {"campaign_id": campaign_id, "lead_id": lead_id, "email": email,
                      "reply_text": reply_text}.items()}},
            status_code=400,
        )

    first_name = payload.get("to_name") or payload.get("first_name") or ""
    company    = payload.get("sl_company") or payload.get("company_name") or ""

    # Process in background — return 200 immediately so Smartlead doesn't retry
    def _process():
        try:
            result = handle_inbound_reply(
                campaign_id=int(campaign_id),
                lead_id=int(lead_id),
                lead_email=email,
                inbound_text=reply_text,
                lead_first_name=first_name,
                lead_company=company,
                dry_run=False,
            )
            _append_log({"event": "processed", "result": result})
            print(f"[{result.get('decision')}] {email} ({result.get('niche')}) "
                  f"-> {result.get('classification', {}).get('label')} "
                  f"({result.get('elapsed_sec')}s, ${result.get('cost_usd')})")
        except Exception as e:
            _append_log({"event": "error", "error": str(e), "payload": payload})
            print(f"[orchestrator-error] {e}")

    background.add_task(_process)
    return {"ok": True, "queued": True}


@app.post("/test/dry-run")
async def test_dry_run(request: Request):
    """
    Test endpoint: same shape as Smartlead webhook but runs dry (no send).
    Useful for shaping the integration before pointing Smartlead at it.
    """
    payload = await request.json()
    result = handle_inbound_reply(
        campaign_id=int(payload.get("campaign_id", 0)),
        lead_id=int(payload.get("lead_id", 0)),
        lead_email=payload.get("to_email", ""),
        inbound_text=payload.get("reply_message", ""),
        lead_first_name=payload.get("to_name", ""),
        lead_company=payload.get("sl_company", ""),
        dry_run=True,
    )
    return result


@app.post("/webhook/ghl/booked")
async def ghl_booked(request: Request):
    """
    GHL booking webhook. Fires when a lead books a call via the
    flowqualificationcall calendar widget.

    Typical GHL payload (varies slightly by trigger):
      {
        "type": "AppointmentCreate" | "AppointmentUpdate" | "AppointmentDelete",
        "appointment": {
          "id": "...",
          "calendarId": "...",
          "contactId": "...",
          "startTime": "2026-05-30T15:00:00Z",
          "endTime":   "2026-05-30T15:15:00Z",
          "title": "...",
          "appointmentStatus": "confirmed" | "cancelled" | "showed" | "noshow"
        },
        "contact": {
          "id": "...",
          "firstName": "...",
          "lastName": "...",
          "email": "...",
          "phone": "...",
          "companyName": "..."
        },
        "locationId": "...",
        "timestamp": "..."
      }

    Returns 200 immediately so GHL doesn't retry.
    """
    try:
        payload = await request.json()
    except Exception as e:
        return JSONResponse({"ok": False, "error": f"bad json: {e}"}, status_code=400)

    appt = payload.get("appointment") or payload.get("calendar") or {}
    contact = payload.get("contact") or {}
    evt_type = payload.get("type") or payload.get("event") or "AppointmentCreate"

    # ATTRIBUTION: look up the lead in Smartlead by email → which campaign + variant?
    attribution = {"niche":None,"campaign_id":None,"variant_label":None,"last_send":None}
    email_addr = (contact.get("email") or "").lower().strip()
    if email_addr:
        try:
            import urllib.request as _u
            SL_KEY = os.environ["SMARTLEAD_API_KEY"]
            SL = "https://server.smartlead.ai/api/v1"
            # Use Smartlead's lead-search endpoint
            url = f"{SL}/leads/?api_key={SL_KEY}&email={email_addr}"
            r = _u.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            d = json.loads(_u.urlopen(r, timeout=10).read())
            lead = d if isinstance(d, dict) and d.get("id") else (d.get("data",[None])[0] if isinstance(d, dict) else None)
            if lead:
                # find the campaign this lead belongs to via campaign_lead_maps endpoint
                lead_id = lead.get("id")
                CIDS = {3263730:"WEALTH",3191292:"FINANCIAL",3191290:"MORTGAGE",
                        3191291:"INSURANCE",3191285:"MEDSPA",3327115:"PI_LAW",
                        3263732:"MCA",3263731:"COMMLOAN"}
                for cid in CIDS.keys():
                    # Pull full stats list per campaign (up to 2000 rows)
                    found_in_camp = False
                    offset = 0
                    while offset < 2000:
                        try:
                            url2 = f"{SL}/campaigns/{cid}/statistics?limit=500&offset={offset}&api_key={SL_KEY}"
                            d2 = json.loads(_u.urlopen(_u.Request(url2, headers={"User-Agent":"Mozilla/5.0"}), timeout=10).read())
                            rows = d2.get("data",[])
                            if not rows: break
                            for row in rows:
                                if (row.get("lead_email") or "").lower() == email_addr:
                                    attribution["niche"]         = CIDS[cid]
                                    attribution["campaign_id"]   = cid
                                    attribution["variant_label"] = row.get("variant_label") or row.get("seq_variant_id")
                                    attribution["last_send"]     = row.get("sent_time")
                                    attribution["sequence_step"] = row.get("sequence_number")
                                    found_in_camp = True
                                    break
                            if found_in_camp or len(rows) < 500: break
                            offset += 500
                        except Exception:
                            break
                    if found_in_camp: break
        except Exception:
            pass

    entry = {
        "received_at":   __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "event_type":    evt_type,
        "appointment_id": appt.get("id"),
        "calendar_id":    appt.get("calendarId"),
        "start_time":     appt.get("startTime"),
        "end_time":       appt.get("endTime"),
        "status":         appt.get("appointmentStatus") or appt.get("status"),
        "title":          appt.get("title"),
        "contact_id":     contact.get("id"),
        "first_name":     contact.get("firstName"),
        "last_name":      contact.get("lastName"),
        "email":          contact.get("email"),
        "phone":          contact.get("phone"),
        "company":        contact.get("companyName"),
        "attribution":    attribution,
        "raw":            payload,  # keep raw for debugging
    }
    _append_booking(entry)
    print(f"[GHL-BOOKING] {evt_type} {contact.get('email','?')} <{contact.get('firstName','')} "
          f"{contact.get('lastName','')}> @ {appt.get('startTime','?')}")
    return {"ok": True, "booking_logged": True}


@app.get("/bookings")
def bookings(limit: int = 50):
    """Recent booking events tail (for metrics_api to consume)."""
    if not os.path.exists(BOOKINGS_PATH):
        return {"count": 0, "bookings": []}
    with open(BOOKINGS_PATH) as f:
        lines = f.readlines()
    out = []
    for ln in lines[-limit:]:
        try:
            entry = json.loads(ln)
            # Strip raw payload for cleaner response
            entry.pop("raw", None)
            out.append(entry)
        except Exception:
            continue
    # Aggregate counts
    confirmed = sum(1 for e in out if e.get("event_type") == "AppointmentCreate"
                    and (e.get("status") or "").lower() not in ("cancelled", "canceled", "noshow"))
    cancelled = sum(1 for e in out if (e.get("status") or "").lower() in ("cancelled", "canceled"))
    return {
        "count":     len(out),
        "confirmed": confirmed,
        "cancelled": cancelled,
        "bookings":  list(reversed(out)),  # newest first
    }


@app.get("/recent")
def recent(limit: int = 20):
    """Tail of the reply event log."""
    if not os.path.exists(LOG_PATH):
        return {"events": []}
    with open(LOG_PATH) as f:
        lines = f.readlines()
    events = []
    for ln in lines[-limit:]:
        try:
            events.append(json.loads(ln))
        except Exception:
            continue
    return {"count": len(events), "events": events}
