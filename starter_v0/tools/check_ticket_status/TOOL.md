---
name: check_ticket_status
track: bonus
kind: local_ticket_registry
provider: mock_ticket_registry
requires_env: []
inputs: [ticket_id]
outputs: [ticket_id, status, summary, priority, assigned_to]
side_effect: false
---
# check_ticket_status

Looks up the current lifecycle status, assignee, and progress of an existing IT support ticket by its ticket ID.
A valid ticket ID formatted as `LAB-XXXXXXXX` (8 hexadecimal characters) is required.
It checks both runtime tickets generated in the current environment and historical mock tickets in `helpdesk_data/tickets_mock.json`.
