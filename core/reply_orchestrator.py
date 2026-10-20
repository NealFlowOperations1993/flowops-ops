"""
End-to-end orchestrator for inbound replies.

Flow:
  1. Smartlead webhook fires EMAIL_REPLY → handle_inbound_reply(payload)
  2. Classify reply (Haiku, 200ms)
  3. If POSITIVE & confidence >= 0.75 → draft auto-reply (Haiku, 800ms)
  4. Post draft to Smartlead reply API
  5. Mark lead status (INTERESTED → after they book it flips to MEETING_BOOKED via GHL webhook)
  6. Slack alert to Neal (FYI, not action-required)

For everything else (NEUTRAL/NEGATIVE/OOO/UNSUB):
  - Log + Slack alert to Neal so he can choose to engage manually
  - UNSUBSCRIBE → auto-flag lead status, no reply

Total auto-reply latency target: <30 sec from inbound webhook to outbound send.
"""
import json
import time
from . import reply_classifier, auto_reply, smartlead_io, slack_alert


# Niche detection from subject line patterns (campaign-specific subject lines we use)
NICHE_FROM_SUBJECT = [
    ("mca",          "MCA"),
    ("mortgage",     "MORTGAGE"),
    ("financial advisor", "FINANCIAL"),
    ("wealth",       "WEALTH"),
    ("sba",          "COMMERCIAL_LOAN"),
    ("commercial",   "COMMERCIAL_LOAN"),
    ("funding",      "FUNDING"),
    ("agency",       "AGENCY"),
    ("med spa",      "MEDSPA"),
    ("medspa",       "MEDSPA"),
    ("injury",       "PI_LAW"),
    ("pi attorney",  "PI_LAW"),
    ("business attorney", "BIZ_LAW"),
    ("tax",          "TAX_RES"),
    ("msp",          "IT_MSP"),
]


def detect_niche(subject: str, campaign_id: int | None = None) -> str:
    """Niche from subject keywords; fallback to campaign-id lookup."""
    if subject:
        s = subject.lower()
        for kw, niche in NICHE_FROM_SUBJECT:
            if kw in s:
                return niche
    CIDS = {
        3191292: "FINANCIAL",
        3191290: "MORTGAGE",
        3263732: "MCA",
        3266528: "WEALTH",
        3266532: "COMMERCIAL_LOAN",
        3191291: "FUNDING",
        3191285: "MEDSPA",
    }
    return CIDS.get(campaign_id or 0, "UNKNOWN")


def handle_inbound_reply(
    campaign_id: int,
    lead_id: int,
    lead_email: str,
    inbound_text: str,
    lead_first_name: str = "",
    lead_company: str = "",
    dry_run: bool = False,
) -> dict:
    """
    Main entry. Returns full event log:
      {
        "decision": "AUTO_REPLIED" | "FLAGGED_TO_NEAL" | "UNSUB" | "SKIPPED" | "ERROR",
        "classification": {...},
        "draft": {...} | None,
        "send_result": {...} | None,
        "elapsed_sec": float,
        "cost_usd": float
      }
    """
    t0 = time.time()
    cost = 0.0

    # Step 1: Pull the last outbound for thread context
    last = smartlead_io.get_last_outbound(campaign_id, lead_id)
    if not last:
        return {
            "decision": "ERROR",
            "error": "no outbound message found in thread",
            "elapsed_sec": time.time() - t0,
        }

    subject = last.get("subject") or ""
    niche = detect_niche(subject, campaign_id)

    # Step 2: Classify
    cls = reply_classifier.classify(inbound_text, subject, lead_email)
    cost += cls.get("_cost", 0.0)

    log = {
        "lead_email": lead_email,
        "lead_first_name": lead_first_name,
        "campaign_id": campaign_id,
        "lead_id": lead_id,
        "niche": niche,
        "classification": cls,
        "subject": subject,
        "inbound_text": inbound_text[:500],
    }

    # Unsubscribe → just mark and stop
    if cls.get("label") == "UNSUBSCRIBE":
        if not dry_run:
            smartlead_io.mark_lead_status(campaign_id, lead_id, "DO_NOT_CONTACT")
        log["decision"] = "UNSUB"
        log["elapsed_sec"] = time.time() - t0
        log["cost_usd"] = round(cost, 5)
        return log

    # Not auto-reply-safe → flag to Neal
    if not cls.get("auto_reply_safe", False):
        log["decision"] = "FLAGGED_TO_NEAL"
        log["reason"] = f"label={cls.get('label')} confidence={cls.get('confidence')}"
        log["elapsed_sec"] = time.time() - t0
        log["cost_usd"] = round(cost, 5)
        return log

    # Step 3: Draft auto-reply
    draft = auto_reply.draft_reply(
        inbound_text=inbound_text,
        original_subject=subject,
        lead_first_name=lead_first_name,
        lead_company=lead_company,
        niche=niche,
        niche_offer_summary=auto_reply.NICHE_OFFERS.get(niche, ""),
    )
    cost += draft.get("_cost", 0.0)

    if draft.get("_error"):
        log["decision"] = "ERROR"
        log["draft"] = draft
        log["elapsed_sec"] = time.time() - t0
        log["cost_usd"] = round(cost, 5)
        return log

    log["draft"] = draft

    # Step 4: Send (skip on dry_run)
    if dry_run:
        log["decision"] = "DRY_RUN_OK"
        log["elapsed_sec"] = time.time() - t0
        log["cost_usd"] = round(cost, 5)
        return log

    ok, msg = smartlead_io.send_reply(
        campaign_id=campaign_id,
        stats_id=last["stats_id"],
        reply_message_id=last["message_id"],
        to_email=lead_email,
        body_plain=draft["body_plain"],
        to_first_name=lead_first_name,
        reply_email_body=inbound_text,
    )
    log["send_result"] = {"ok": ok, "message": msg}

    if ok:
        smartlead_io.mark_lead_status(campaign_id, lead_id, "INTERESTED")
        log["decision"] = "AUTO_REPLIED"
    else:
        log["decision"] = "ERROR"
        log["error"] = f"send failed: {msg}"

    log["elapsed_sec"] = round(time.time() - t0, 2)
    log["cost_usd"] = round(cost, 5)

    # Fire Slack alert (no-ops if no token)
    if not dry_run:
        try:
            slack_alert.reply_alert(log)
        except Exception as e:
            log["slack_error"] = str(e)

    return log


if __name__ == "__main__":
    # Dry-run smoke test against Ralph (won't actually send)
    print("=" * 70)
    print("Orchestrator dry-run on Ralph's 'Sure'")
    print("=" * 70)
    result = handle_inbound_reply(
        campaign_id=3263732,
        lead_id=3725290207,
        lead_email="ralph@firstchoicedebtsolutions.org",
        inbound_text="Sure",
        lead_first_name="Ralph",
        lead_company="First Choice Debt Solutions",
        dry_run=True,
    )
    print(json.dumps({k: v for k, v in result.items() if k != "draft"}, indent=2, default=str))
    if result.get("draft"):
        print("\n--- DRAFT BODY ---")
        print(result["draft"]["body_plain"])
        print(f"\nelapsed: {result['elapsed_sec']}s | cost: ${result['cost_usd']}")
