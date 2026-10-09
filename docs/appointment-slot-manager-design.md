# Appointment Slot Manager – Education Cloud Portal (LWC Design)

Component for students/applicants to **book**, **transfer (reschedule)** and **cancel** appointment slots
(advising, admissions interviews, financial aid, etc.) in an Experience Cloud portal.

> Note: the reference folder (`.../2000_scheduler/main/default/lwc`) was not available when this was written.
> Reuse names below map to "existing scheduler LWCs if present"; replace with your actual components.

---

## 1. Component tree

```
c-appointment-slot-manager            (container, owns state + Apex wiring)
├── c-appointment-list                (upcoming / past appointments, row actions)
│   └── c-appointment-card            (one appointment; Transfer / Cancel buttons)
├── c-slot-picker                     (shared by Book and Transfer)
│   ├── c-slot-filter-bar             (service type, advisor, campus/virtual, date range)
│   ├── c-slot-calendar               (month strip / day selector, availability dots)
│   └── c-slot-time-grid              (time buttons for selected day)
├── c-appointment-confirm-modal       (summary step: book / transfer)
├── c-appointment-cancel-modal        (reason + policy warning)
└── c-appointment-toast-region        (success/error, uses lightning/platformShowToastEvent)
```

Container is the only component that calls Apex; children are presentational and emit events
(`slotselect`, `transferrequest`, `cancelrequest`, `confirm`, `close`).

---

## 2. Screens & flows

### 2.1 Home – "My Appointments"
```
+--------------------------------------------------------------+
| My Appointments                         [ + Book appointment ]|
| [Upcoming (2)] [Past] [Cancelled]                             |
|--------------------------------------------------------------|
| Academic Advising                         ● Confirmed         |
| Tue 14 Oct 2026 · 10:30–11:00 · Zoom      Advisor: A. Rahman  |
|                         [ Transfer ]  [ Cancel ]  [ Add to cal]|
|--------------------------------------------------------------|
| Financial Aid Review                      ● Pending           |
| Fri 17 Oct 2026 · 14:00–14:30 · Room B12                      |
|                         [ Transfer ]  [ Cancel ]              |
+--------------------------------------------------------------+
```
- Empty state: illustration + "No upcoming appointments" + primary Book button.
- Transfer/Cancel disabled with tooltip when inside policy cut-off (e.g. < 24h).

### 2.2 Book (3 steps, `lightning-progress-indicator`)
1. **Service** – appointment type, reason (optional), preferred advisor / any, mode (in person / virtual).
2. **Slot** – `c-slot-picker`: pick date, then time. Shows time zone of the user.
3. **Confirm** – summary, attendee contact info, notes, consent checkbox → **Confirm booking**.

### 2.3 Transfer
- Launched from card. Shows **current slot** (struck-through chip) vs **new slot** side by side.
- Reuses `c-slot-picker`, locked to same service type (advisor optional).
- Confirm modal: "Move from *Tue 14 Oct 10:30* to *Wed 15 Oct 09:00*". Reason optional.
- Atomic on server: book new slot then release old; roll back on failure.

### 2.4 Cancel
- Modal: appointment summary, reason picklist (required), free text, policy message
  (late-cancel / no-show warning), buttons **Keep appointment** / **Cancel appointment** (destructive).
- After success: toast + offer **Rebook** shortcut.

---

## 3. State model (container)

| Property | Type | Purpose |
|---|---|---|
| `view` | `'list' \| 'book' \| 'transfer'` | current screen |
| `appointments` | `Appointment[]` | wired list |
| `selectedAppointment` | `Appointment` | transfer/cancel target |
| `filters` | `{serviceType, advisorId, mode, from, to}` | slot search |
| `slots` | `Slot[]` | available slots (grouped by day in a getter) |
| `selectedSlot` | `Slot` | pending choice |
| `step` | `1..3` | book wizard step |
| `isLoading`, `error` | | UX states |

Types
```
Appointment { id, serviceType, status, start, end, timeZone, advisorName, location|joinUrl, canTransfer, canCancel }
Slot        { id, start, end, advisorId, advisorName, mode, capacity, remaining }
```

---

## 4. Apex / data contract (controller `AppointmentSlotController`)

| Method | Cacheable | Description |
|---|---|---|
| `getMyAppointments(status)` | yes | appointments for current contact |
| `getAvailableSlots(filters)` | yes | open slots, honours capacity & blackout dates |
| `bookAppointment(slotId, serviceType, notes)` | no | creates appointment; re-checks capacity |
| `transferAppointment(apptId, newSlotId, reason)` | no | transactional move |
| `cancelAppointment(apptId, reason, comments)` | no | validates policy window, frees slot |
| `getPolicy(serviceType)` | yes | cut-off hours, messages |

Concurrency: server re-validates slot availability; on `SLOT_TAKEN` the UI keeps the user on step 2,
refreshes slots, and shows an inline message (no data loss).
Use `refreshApex` after each mutation. Enforce sharing / contact ownership server-side
(`with sharing`, filter on current user's Contact/Person Account).

Suggested objects (adapt to existing scheduler): `ServiceAppointment`/custom `Appointment__c`,
`Slot__c` (or `ServiceResource` availability), `Appointment_Policy__mdt`.

---

## 5. UX details

- **SLDS** only; theme via Experience Cloud branding tokens / styling hooks (`--slds-c-*`), no hard-coded colors.
- Status badges: Confirmed (success), Pending (warning), Cancelled (offline), Completed (default).
- Slot buttons: `lightning-button` stateful toggle; selected state with check icon (not colour alone).
- Time zone: always display + label; store UTC.
- Loading: `lightning-spinner` for first load, skeleton rows for slot grid.
- Errors: inline `slds-form-element__help` for field errors, toast for server errors.
- Mobile-first: calendar collapses to horizontal day strip; modals become full-screen sheets < 480px.
- Confirmations: email + ICS download ("Add to calendar").

## 6. Accessibility (WCAG 2.1 AA)

- Wizard: `aria-current="step"`; focus moves to step heading on change.
- Calendar/time grid: roles `grid`/`gridcell` or radio group; arrow-key navigation; visible focus.
- Modals: focus trap, `Esc` closes, focus returns to triggering button, `aria-labelledby/-describedby`.
- Toasts announced via `aria-live="polite"`; destructive button labelled with appointment context
  ("Cancel Academic Advising on 14 Oct").
- Contrast ≥ 4.5:1; don't rely on colour for availability.

## 7. Design attributes (Experience Builder)

`@api` exposed: `serviceTypes` (CSV), `allowTransfer`, `allowCancel`, `cancelCutoffHours` (fallback),
`showPastAppointments`, `defaultMode`, `cardTitle`.
Meta targets: `lightningCommunity__Page`, `lightningCommunity__Default`.

## 8. Edge cases

- No slots in range → suggest widening dates / different advisor.
- Slot taken mid-flow, appointment changed by staff, duplicate booking of same service type (block or warn).
- Transfer limit (e.g. max 2 per appointment) → disable with explanation.
- Guest / unauthenticated users: redirect to login.
- Cancelling during a transfer in progress: disable actions while `isSaving`.

## 9. Testing

- Jest: each presentational component (events, a11y roles, disabled states); container with mocked Apex.
- Apex: capacity race, policy cut-off, sharing, transfer rollback.
- Manual: keyboard-only pass, screen reader (NVDA/VoiceOver), mobile viewport, multiple time zones.

## 10. Suggested build order

1. `c-appointment-list` + card (read-only) with wired Apex
2. `c-slot-picker` (filters, calendar, grid)
3. Book flow + confirm modal
4. Cancel modal + policy
5. Transfer flow
6. Polish: a11y, toasts, ICS, Experience Builder attributes
