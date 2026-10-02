// ============================================================
// Dashboard Seed Data — Placeholder shapes for UI dev
// Replaced by real API data when backend connects.
// ============================================================

import type {
  DashboardKPI,
  AISummary,
  ClientHealthBreakdown,
  ChurnTrendPoint,
  RiskDistributionSlice,
  ActivityItem,
  WorkflowStep,
  HighRiskClientRow,
  DashboardRecommendation,
  QuickAction,
} from './dashboard.types';

// ── KPIs ─────────────────────────────────────────────────────

// ── KPIs ─────────────────────────────────────────────────────

export const PLACEHOLDER_KPIS: DashboardKPI[] = [
  {
    id: 'total_clients',
    label: 'Total Clients',
    value: 1,
    trend: { direction: 'neutral', percent: 0, period: 'current' },
    sparkline: [1, 1, 1, 1, 1, 1, 1],
    iconColor: 'primary',
  },
  {
    id: 'healthy',
    label: 'Healthy Clients',
    value: 0,
    trend: { direction: 'neutral', percent: 0, period: 'current' },
    sparkline: [0, 0, 0, 0, 0, 0, 0],
    iconColor: 'success',
  },
  {
    id: 'medium_risk',
    label: 'Medium Risk',
    value: 0,
    trend: { direction: 'neutral', percent: 0, period: 'current' },
    sparkline: [0, 0, 0, 0, 0, 0, 0],
    iconColor: 'warning',
  },
  {
    id: 'high_risk',
    label: 'High Risk',
    value: 1,
    trend: { direction: 'neutral', percent: 0, period: 'current' },
    sparkline: [1, 1, 1, 1, 1, 1, 1],
    iconColor: 'danger',
  },
  {
    id: 'ai_predictions',
    label: 'AI Predictions Today',
    value: 12,
    trend: { direction: 'up', percent: 100, period: 'vs yesterday' },
    sparkline: [1, 2, 4, 6, 8, 10, 12],
    iconColor: 'info',
  },
  {
    id: 'reports',
    label: 'Reports Generated',
    value: 4,
    trend: { direction: 'neutral', percent: 0, period: 'this week' },
    sparkline: [1, 2, 2, 3, 3, 4, 4],
    iconColor: 'primary',
  },
];

// ── AI Summary ────────────────────────────────────────────────

export const PLACEHOLDER_AI_SUMMARY: AISummary = {
  headline: 'Yardworx Land Management client intelligence & churn analysis.',
  body: 'Comprehensive account analysis for Yardworx Land Management indicates elevated appointment and lead acquisition costs. Automated AI workflows have processed telemetry data with high confidence, generating dedicated intervention and retention recommendations.',
  confidence: 0.95,
  generatedAt: 'Today at 09:14 AM',
  flags: ['Yardworx Land Management requires optimization', 'Targeted retention playbook active'],
};

// ── Client Health ─────────────────────────────────────────────

export const PLACEHOLDER_HEALTH: ClientHealthBreakdown = {
  healthy: 0,
  medium: 0,
  high: 0,
  critical: 1,
  total: 1,
};

// ── Churn Trend ───────────────────────────────────────────────

export const PLACEHOLDER_CHURN_TREND: ChurnTrendPoint[] = [
  { month: 'Jan', churnRate: 6.2, predicted: 6.0 },
  { month: 'Feb', churnRate: 5.8, predicted: 5.9 },
  { month: 'Mar', churnRate: 6.5, predicted: 6.1 },
  { month: 'Apr', churnRate: 5.2, predicted: 5.5 },
  { month: 'May', churnRate: 4.8, predicted: 5.0 },
  { month: 'Jun', churnRate: 5.4, predicted: 5.2 },
  { month: 'Jul', churnRate: 6.1, predicted: 5.8 },
  { month: 'Aug', churnRate: 5.9, predicted: 5.6 },
  { month: 'Sep', churnRate: 4.6, predicted: 5.0 },
  { month: 'Oct', churnRate: 4.2, predicted: 4.8 },
  { month: 'Nov', churnRate: 3.8, predicted: 4.2 },
  { month: 'Dec', churnRate: 3.5, predicted: 3.9 },
];

// ── Risk Distribution ─────────────────────────────────────────

export const PLACEHOLDER_RISK_DISTRIBUTION: RiskDistributionSlice[] = [
  { name: 'Healthy',  value: 0, color: '#22C55E' },
  { name: 'Medium',   value: 0, color: '#F59E0B' },
  { name: 'High',     value: 0, color: '#EF4444' },
  { name: 'Critical', value: 1, color: '#991B1B' },
];

// ── Activity ──────────────────────────────────────────────────

export const PLACEHOLDER_ACTIVITY: ActivityItem[] = [
  { id: '1', type: 'ai_analysis',        title: 'AI Analysis Complete',     description: 'Analysis completed for Yardworx Land Management', client: 'Yardworx Land Management', timestamp: '9 min ago', isNew: true },
  { id: '2', type: 'alert_triggered',    title: 'High Risk Alert',          description: 'Yardworx Land Management churn probability assessed', client: 'Yardworx Land Management', timestamp: '24 min ago', isNew: true },
  { id: '3', type: 'workflow_executed',  title: 'Workflow Completed',       description: 'Client intelligence workflow ran successfully', client: 'Yardworx Land Management', timestamp: '1h ago' },
  { id: '4', type: 'report_generated',  title: 'Report Generated',         description: 'Yardworx Land Management Executive Summary exported', client: 'Yardworx Land Management', timestamp: '2h ago' },
  { id: '5', type: 'recommendation_sent', title: 'Recommendation Generated', description: 'Next-best-action ready for Account Manager', client: 'Yardworx Land Management', timestamp: '3h ago' },
  { id: '6', type: 'client_updated',    title: 'Client Data Refreshed',    description: 'Yardworx Land Management telemetry synced', client: 'Yardworx Land Management', timestamp: '5h ago' },
];

// ── Workflow Steps ─────────────────────────────────────────────

export const PLACEHOLDER_WORKFLOW: WorkflowStep[] = [
  { id: 'slack',       name: 'Slack Trigger',      status: 'completed', duration: '0.1s' },
  { id: 'retrieval',   name: 'Client Retrieval',   status: 'completed', duration: '0.4s' },
  { id: 'summary',     name: 'Data Summary',        status: 'completed', duration: '1.2s' },
  { id: 'embedding',   name: 'Embedding',           status: 'completed', duration: '2.1s' },
  { id: 'similarity',  name: 'Similarity Search',   status: 'completed', duration: '0.8s' },
  { id: 'groq',        name: 'Groq Analysis',       status: 'running',   duration: '—' },
  { id: 'recommend',   name: 'Recommendation',      status: 'pending' },
  { id: 'complete',    name: 'Completed',            status: 'pending' },
];

// ── High Risk Clients ─────────────────────────────────────────

export const PLACEHOLDER_HIGH_RISK: HighRiskClientRow[] = [
  { id: 'yardworx', name: 'Yardworx Land Management', industry: 'Landscaping', healthScore: 20, churnProbability: 80, trend: 'down', riskLevel: 'critical', mrr: 12000 },
];

// ── Recommendations ────────────────────────────────────────────

export const PLACEHOLDER_RECOMMENDATIONS: DashboardRecommendation[] = [
  { id: '1', title: 'Schedule Executive Review', description: 'Review operational metrics and address appointment conversion costs.', client: 'Yardworx Land Management', priority: 'critical', confidence: 0.95, category: 'Engagement' },
  { id: '2', title: 'Optimize Lead Channel Allocation', description: 'Rebalance acquisition ad placement to improve cost per scheduled appointment.', client: 'Yardworx Land Management', priority: 'high', confidence: 0.89, category: 'Retention' },
  { id: '3', title: 'Streamline Telemetry Sync', description: 'Ensure continuous sync of field operations and CRM updates.', client: 'Yardworx Land Management', priority: 'medium', confidence: 0.84, category: 'Operations' },
];

// ── Quick Actions ─────────────────────────────────────────────

export const QUICK_ACTIONS: QuickAction[] = [
  { id: 'analyze',   label: 'Analyze Client',    description: 'Run AI analysis on Yardworx',      icon: 'brain',         color: 'primary', href: '/clients' },
  { id: 'report',    label: 'Generate Report',   description: 'Export executive summary',           icon: 'file-text',     color: 'success', href: '/reports' },
  { id: 'ai',        label: 'AI Assistant',      description: 'Ask Customer Churn Predictor AI anything', icon: 'sparkles', color: 'info'    },
  { id: 'workflow',  label: 'Workflow Monitor',  description: 'View automation pipeline status',    icon: 'git-branch',    color: 'warning', href: '/workflow' },
  { id: 'export',    label: 'Export Dashboard',  description: 'Download dashboard as PDF',          icon: 'download',      color: 'default' },
  { id: 'refresh',   label: 'Refresh Data',      description: 'Pull latest data from backend',      icon: 'refresh-cw',    color: 'default' },
];
