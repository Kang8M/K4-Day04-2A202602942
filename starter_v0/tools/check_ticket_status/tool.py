from __future__ import annotations

import json
import re
from typing import Any

from tools._shared import ROOT, err

MOCK_FILE = ROOT / "helpdesk_data" / "tickets_mock.json"
LOCAL_TICKETS_DIR = ROOT / "tickets"
TICKET_ID_PATTERN = re.compile(r"^LAB-[A-F0-9]{8}$", re.IGNORECASE)


def check_ticket_status(ticket_id: str = "") -> dict[str, Any]:
    """Check the status and progress of an IT support ticket."""
    if not isinstance(ticket_id, str):
        return {"tool": "check_ticket_status", "error": "invalid_input_type"}

    norm_id = (ticket_id or "").strip().upper()
    if not norm_id:
        return {"tool": "check_ticket_status", "error": "missing_ticket_id"}

    if not TICKET_ID_PATTERN.fullmatch(norm_id):
        return {
            "tool": "check_ticket_status",
            "ticket_id": norm_id,
            "error": "invalid_ticket_id_format",
            "message": "Ticket ID must match the format LAB-XXXXXXXX (8 hex characters).",
        }

    try:
        # 1. Check runtime session tickets in tickets/ folder
        local_file = LOCAL_TICKETS_DIR / f"{norm_id}.json"
        if local_file.exists():
            ticket = json.loads(local_file.read_text(encoding="utf-8"))
            return {
                "tool": "check_ticket_status",
                "ticket_id": norm_id,
                "status": ticket.get("status", "open"),
                "summary": ticket.get("summary"),
                "priority": ticket.get("priority"),
                "asset_id": ticket.get("asset_id"),
                "created_at": ticket.get("created_at"),
                "assigned_to": "IT-Support-L1",
                "source": "local_runtime",
            }

        # 2. Check historical mock database
        if MOCK_FILE.exists():
            data = json.loads(MOCK_FILE.read_text(encoding="utf-8"))
            for item in data.get("tickets", []):
                if item.get("ticket_id") == norm_id:
                    return {
                        "tool": "check_ticket_status",
                        **item,
                        "source": "mock_database",
                    }

        return {
            "tool": "check_ticket_status",
            "ticket_id": norm_id,
            "error": "ticket_not_found",
            "message": f"No ticket found with ID {norm_id}.",
        }
    except Exception as exc:
        return err("check_ticket_status", exc)
