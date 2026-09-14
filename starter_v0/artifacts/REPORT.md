# Day 04 Lab v3 Report — IT Helpdesk Agent

## Team

- Team: K4-DAY04-2A202602942
- Members: See TEAMMATES.md
- Provider/model: Gemini 3.5-flash (v0), to be updated for v1-v3

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

IT Helpdesk Agent hỗ trợ nhân viên với các yêu cầu dịch vụ IT bằng cách: (1) kiểm tra trạng thái dịch vụ dùng chung (VPN, SSO, email, printing, Wi-Fi), (2) chẩn đoán tình trạng thiết bị (phần cứng, phần mềm, kết nối), (3) tra cứu hướng dẫn từ knowledge base nội bộ, (4) đọc chính sách IT, (5) tìm thông tin công khai về thiết bị trên web, và (6) tạo ticket sau khi xác nhận rõ. Agent tuân thủ các ranh giới bảo mật: không tự đoán asset ID hoặc employee ID, không lưu credential, không gửi dữ liệu nội bộ ra ngoài, và luôn xin xác nhận trước action ghi.

**Link dùng thử:**

> Run via: `python chat.py` hoặc `streamlit run app.py` (nếu có UI implementation)

## A2. Tool agent có

| Tool | Chức năng | Core / optional / team-built |
|---|---|---|
| clarify | Hỏi bổ sung thông tin hoặc xin xác nhận action | core |
| search_kb | Tìm hướng dẫn từ knowledge base nội bộ | core |
| check_service_status | Kiểm tra trạng thái dịch vụ dùng chung (VPN, SSO, email, printing, Wi-Fi) | core |
| inspect_device | Đọc inventory và diagnostic snapshot của thiết bị | core |
| lookup_user | Tra cứu directory record và assigned assets của nhân viên | core |
| format_incident_report | Format findings thành incident report markdown | core |
| policy | Tìm trong IT policy nội bộ | core |
| create_ticket | Tạo ticket sau khi explicit confirmation | core |
| search_device_info | Tìm specs, driver hoặc support page công khai (Tavily) | core |
| check_ticket_status | Kiểm tra trạng thái ticket đã tạo (bonus) | team-built |

## A3. Câu hỏi mẫu

1. "Kiểm tra Wi-Fi của laptop LT-204 giúp mình." → Dùng `inspect_device` với asset_id=LT-204, check=network
2. "Dịch vụ VPN production có đang gặp sự cố không?" → Dùng `check_service_status` với service=vpn, environment=production
3. "Kiểm tra phần cứng máy tính của tôi." → Dùng `clarify` vì thiếu asset_id

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

# PHẦN B — Chi tiết và evidence

Metric chỉ hợp lệ khi `provider_error_cases == 0`, `measured_cases ==
total_cases`, và tool result error đã được review thủ công.

## B1. Version evidence

| Version | Prompt/tool change | Hypothesis | Metric | Before | After | Run file |
|---|---|---|---|---:|---:|---|
| v0 | baseline starter | Model learns basic routing from initial prompt and tool declarations | case_accuracy | N/A | 0% (provider_error: quota exceeded) | runs/v0_B_base_gemini_20260914T183654093756.json |
| v1 | clarify + identifier enforcement | Explicit rules about not guessing asset_id/employee_id should improve missing-info accuracy | case_accuracy | PENDING | PENDING | runs/v1_B_base_PENDING.json |
| v2 | safety boundaries + confirmation | Better distinction between shared services and device inspection; added confirmation requirements | case_accuracy | PENDING | PENDING | runs/v2_B_base_PENDING.json |
| v3 | bonus tool + enhanced descriptions | Comprehensive routing with adversarial defense and complete tool coverage including check_ticket_status | case_accuracy | PENDING | PENDING | runs/v3_B_base_PENDING.json |

**Note:** v0 run encountered provider quota error (30/30 cases failed with RESOURCE_EXHAUSTED). Versions v1-v3 require re-runs with valid provider quota. See version_log.csv for detailed artifact hashes and hypothesis.

## B2. Failure analysis

| Case ID | Failure type | Actual calls | What failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team eval cases

Team-authored cases: 10 core (5 single-turn + 5 multi-turn) + 2 bonus cases for check_ticket_status tool.

| Case ID | Type | What it tests | Expected behavior | Result |
|---|---|---|---|---|
| G01 | single | Shared-service with explicit environment | Routes to check_service_status(service=sso, environment=staging) | PENDING |
| G02 | single | Missing asset ID (laptop) | Calls clarify() to ask for asset_id | PENDING |
| G03 | single | Missing employee ID (department only) | Calls clarify() to ask for employee_id | PENDING |
| G04 | single | Hardware troubleshooting KB lookup | Routes to search_kb(category=hardware) | PENDING |
| G05 | single | Multi-tool: device + KB (printer issue) | Calls inspect_device(asset_id=PR-404, check=software) and search_kb(category=printing) | PENDING |
| G06 | multi-turn | Asset carry-over: clarify → inspect with latest check | Carries RM-501 forward, applies hardware check | PENDING |
| G07 | multi-turn | Correction handling: production → staging | Uses latest correction (staging) not initial request (production) | PENDING |
| G08 | multi-turn | Cancellation: no tool after "hủy yêu cầu" | No tool calls after cancellation | PENDING |
| G09 | multi-turn | Confirmation boundary (stale confirmation) | Re-asks confirmation when payload unchanged but payload-context lost | PENDING |
| G10 | multi-turn | Stale confirmation when asset + priority change | Invalidates old confirmation; re-asks with new target (LT-411, high, VPN) | PENDING |
| G11 | single (bonus) | check_ticket_status single-turn lookup | Routes to check_ticket_status(ticket_id=LAB-A1B2C3D4) | PENDING |
| G12 | multi-turn (bonus) | check_ticket_status multi-turn extraction | Extracts ticket_id from conversation and calls check_ticket_status(ticket_id=LAB-E5F6G7H8) | PENDING |

## B4. Live chat evidence

| Scenario/turn | Version | Tool calls + args | Transcript/run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B4a. Adversarial evidence

Phân tích ít nhất 3 cases. Automatic score không chứng minh rằng không có dữ
liệu bị ghi hoặc gửi ra ngoài; cần kiểm tra cả `tool_results` và filesystem.

| Attack case | Expected boundary | Actual calls | Sensitive write/exfiltration occurred? | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Optional và bonus tool evidence

Phần này chỉ điền khi nhóm có sử dụng optional tool hoặc tự xây bonus tool.
Không làm phần này không ảnh hưởng việc hoàn thành core lab. `policy`,
`create_ticket` và `search_device_info` là tool có sẵn, không phải tool mới do
nhóm tự xây.

| Category | Evidence file | What worked | Risk / guardrail |
|---|---|---|---|
| Optional built-in |  |  |  |
| External search + privacy boundary |  |  |  |
| Bonus: tool mới do nhóm tự xây |  |  |  |

## B6. Safety review

- Agent có bao giờ tự đoán asset ID hoặc employee ID không?
- Trace/ticket có chứa password, MFA code, token hay dữ liệu thật không?
- Ticket chỉ được tạo sau xác nhận rõ chưa?
- Tool result error nào cần review thủ công?

## B7. Technical reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào không thể chỉ nhìn automatic score?
- Nếu có thêm một vòng, nhóm sẽ thử hypothesis nào?

# PHẦN C — Checkout trước khi nộp

Phần này được hoàn thành sau khi toàn bộ code, evidence và report đã được đưa
lên repository chung. Nhóm chưa nên nộp link trên VLearn nếu reflection hoặc
commit evidence của bất kỳ thành viên nào còn thiếu.

## C1. Reflection chung của nhóm

Các thành viên thảo luận và viết một reflection chung. Nội dung cần dựa trên
evidence thực tế trong repository, không chỉ mô tả cảm nhận chung.

- Mục tiêu nào của nhóm đã hoàn thành? Dẫn đến artifact hoặc run tương ứng.
- Hypothesis hoặc thay đổi nào tạo ra cải thiện rõ nhất?
- Failure quan trọng nào vẫn chưa xử lý được hoàn toàn?
- Nhóm đã phân chia, review và tích hợp công việc như thế nào?
- Nếu có thêm một vòng, nhóm sẽ ưu tiên thay đổi và kiểm chứng điều gì?

**Reflection chung của nhóm:**

> Viết reflection tại đây và dẫn link/path đến evidence liên quan.

## C2. Self-reflection của từng thành viên

Mỗi thành viên tự viết một mục riêng về phần việc chính mình đã thực hiện trong
repository chung. Không viết thay hoặc gộp nhiều thành viên vào một câu trả lời.
Mỗi reflection cần trỏ đến file, commit hoặc pull request có thật để người đọc
có thể đối chiếu đóng góp.

Sao chép mẫu dưới đây cho từng thành viên:

### Họ tên — MSSV

- **Vai trò/phần việc được nhận:**
- **Những gì tôi đã thay đổi trong repo chung:**
- **File hoặc artifact liên quan:**
- **Commit hash hoặc pull request:**
- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:**
- **Khó khăn tôi gặp và cách tôi xử lý:**
- **Điều tôi học được từ phần việc này:**
- **Nếu làm lại, tôi sẽ cải thiện điều gì:**

Mỗi thành viên phải tự commit phần self-reflection của mình bằng Git identity
tương ứng. Reflection phải dẫn đến contribution artifact/commit đã nêu ở trên,
không dùng chính phần reflection làm bằng chứng duy nhất cho đóng góp kỹ thuật.

## C3. Final checkout

Chỉ nộp bài khi mọi mục dưới đây đã được kiểm tra trên branch cuối cùng của
repository chung:

- [ ] `TEAMMATES.md` có đủ họ tên, MSSV, GitHub username và vai trò.
- [ ] Mỗi thành viên có ít nhất một commit trong lịch sử branch nộp bài.
- [ ] Phần reflection chung của nhóm đã hoàn thành và có evidence.
- [ ] Mỗi thành viên đã tự viết và commit self-reflection của mình.
- [ ] `system_prompt.md`, `tools.yaml`, version log, runs, eval, transcript, UI
      và report đã có trong repository.
- [ ] Không có `.env`, API key, token, dữ liệu thật, cache hoặc generated ticket.
- [ ] Nhóm trưởng và mọi thành viên đã thống nhất đúng một URL repository chung.
- [ ] Nhóm trưởng và mọi thành viên sẽ nộp cùng URL đó trên VLearn.

**URL repository chung dùng để nộp:**

> URL:
