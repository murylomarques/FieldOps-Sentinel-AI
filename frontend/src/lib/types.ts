export type Role = "manager" | "dispatcher" | "analyst";

export interface KpiData {
  percent_orders_at_risk: number;
  avg_sla_risk_score: number;
  approval_rate: number;
  override_rate: number;
  avg_response_latency_ms: number;
  projected_avoided_delays: number;
  projected_backlog_reduction: number;
  estimated_operational_impact: number;
}

export interface Order {
  id: number;
  order_id: string;
  customer_id: string;
  city: string;
  region: string;
  service_type: string;
  priority: string;
  created_at: string;
  scheduled_start: string;
  scheduled_end: string;
  technician_id: string;
  technician_skill: string;
  technician_load: number;
  distance_km: number;
  previous_reschedules: number;
  customer_history_no_show: number;
  rain_level: number;
  traffic_level: number;
  backlog_region: number;
  sla_hours_remaining: number;
  estimated_duration_minutes: number;
  status: string;
  notes: string;
}

export interface RecommendationQueue {
  decision_id: string;
  order_id: string;
  confidence: number;
  impact_score: number;
  status: string;
  action_type: string;
  recommended_priority: string;
  created_at: string;
}
