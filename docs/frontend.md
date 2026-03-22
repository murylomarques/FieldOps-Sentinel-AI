# Frontend Notes

## Design Direction
The UI is built as a premium B2B operations console with:
- strong visual hierarchy
- large data cards
- subtle motion
- focused color palette

## Main Pages
- Login: role presets and secure token entry
- Dashboard: KPI summary, risk map, approval queue, agent runtime
- Orders: searchable operational list
- Order detail: risk snapshot, recommendation status, event timeline
- Recommendations: approve/reject workflow with justification
- Insights: executive summaries
- Monitoring: model telemetry and status distribution
- Replay: order decision timeline

## Data Access
A single typed fetch helper (`frontend/src/lib/api.ts`) handles API requests with JWT injection and error normalization.

## UX Behavior
- Protected routes via auth guard
- Empty/loading states on key screens
- Responsive dashboard layout
