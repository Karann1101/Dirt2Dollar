import * as React from 'react';
import { motion } from 'framer-motion';
import { ContentWrapper } from '@/components/common/PageHeader';
import { ErrorState } from '@/components/common/EmptyState';

// ── Dashboard feature components ──────────────────────────────
import { DashboardHeader }         from './components/DashboardHeader';
import { QuickActionBar }          from './components/QuickActionBar';
import { KPISection }              from './components/KPISection';
import { AISummaryCard }           from './components/AISummaryCard';
import { ClientHealthOverview }    from './components/ClientHealthOverview';
import { RiskDistributionChart, ChurnTrendChart } from './components/DashboardCharts';
import { HighRiskClientsTable }    from './components/HighRiskClientsTable';
import { RecentActivityTimeline }  from './components/RecentActivityTimeline';
import { WorkflowStatusCard }      from './components/WorkflowStatusCard';
import { RecentRecommendations }   from './components/RecentRecommendations';
import { AIAssistantPreview }      from './components/AIAssistantPreview';

// ============================================================
// Dashboard Page — Executive View
import { useDashboard } from '@/hooks/useDashboard';

export function DashboardPage() {
  const [refreshKey, setRefreshKey] = React.useState(0);
  const { metrics, churnRiskChart, revenueChart, healthDistribution, isLoading, isError, errorMessage, refetch } = useDashboard();

  // If the core metrics call fails, the whole page has nothing meaningful
  // to show (every section below depends on `metrics` in some way), so we
  // show a single full-page error state with a retry button instead of
  // rendering ten sections of broken/empty widgets.
  if (isError && !isLoading) {
    return (
      <ContentWrapper className="flex min-h-[60vh] items-center justify-center">
        <ErrorState
          title="Couldn't load your dashboard"
          description={errorMessage ?? 'Something went wrong while fetching your metrics.'}
          onRetry={refetch}
        />
      </ContentWrapper>
    );
  }

  // Create KPI array mapped from metrics
  const kpiData = metrics
  ? [
      {
        id: 'total_clients',
        label: 'Total Clients',
        value: metrics.totalClients,
        trend: {
          direction: 'neutral' as const,
          percent: 0,
          period: 'current',
        },
        iconColor: 'primary' as const,
      },
      {
        id: 'active_clients',
        label: 'Active Clients',
        value: metrics.activeClients,
        trend: {
          direction: metrics.activeGrowth >= 0 ? 'up' as const : 'down' as const,
          percent: Math.abs(metrics.activeGrowth),
          period: 'vs previous period',
        },
        iconColor: 'success' as const,
      },
      {
        id: 'at_risk_clients',
        label: 'At Risk Clients',
        value: metrics.atRiskClients,
        trend: {
          direction: metrics.riskGrowth >= 0 ? 'up' as const : 'down' as const,
          percent: Math.abs(metrics.riskGrowth),
          period: 'vs previous period',
        },
        iconColor: 'warning' as const,
      },
      {
        id: 'churn_probability',
        label: 'Avg Churn Probability',
        value: `${metrics.avgChurnProbability}%`,
        trend: {
          direction: 'neutral' as const,
          percent: 0,
          period: 'current',
        },
        iconColor: 'danger' as const,
      },
      {
        id: 'health_score',
        label: 'Avg Health Score',
        value: metrics.avgHealthScore,
        trend: {
          direction: metrics.healthGrowth >= 0 ? 'up' as const : 'down' as const,
          percent: Math.abs(metrics.healthGrowth),
          period: 'vs previous period',
        },
        iconColor: 'info' as const,
      },
      {
        id: 'total_mrr',
        label: 'Total MRR',
        value: `₹${metrics.totalMRR.toLocaleString('en-IN')}`,
        trend: {
          direction: metrics.mrrGrowth >= 0 ? 'up' as const : 'down' as const,
          percent: Math.abs(metrics.mrrGrowth),
          period: 'vs previous period',
        },
        iconColor: 'primary' as const,
      },
    ]
  : undefined;

  const healthBreakdown = healthDistribution
  ? {
      healthy:
        (healthDistribution.find((p) => (p.label ?? (p as any).name) === '90-100')?.value ?? 0) +
        (healthDistribution.find((p) => (p.label ?? (p as any).name) === '70-89')?.value ?? 0),
      medium:
        healthDistribution.find((p) => (p.label ?? (p as any).name) === '50-69')?.value ?? 0,
      high:
        healthDistribution.find((p) => (p.label ?? (p as any).name) === '30-49')?.value ?? 0,
      critical:
        healthDistribution.find((p) => (p.label ?? (p as any).name) === '0-29')?.value ?? 0,
      total: healthDistribution.reduce((sum, p) => sum + p.value, 0),
    }
  : undefined;

const riskDistribution = healthDistribution?.map((point) => {
  const label = point.label ?? (point as any).name;

  return {
    name: label,
    value: point.value,
    color: '#64748B',
  };
});

  const churnTrend = churnRiskChart?.map((point) => ({
    month: point.label ?? '',
    churnRate: point.value,
    predicted: point.secondaryValue,
}));

  return (
    <ContentWrapper className="space-y-5">

      {/* ── 1. Welcome Banner ── */}
      <DashboardHeader
        userName="Alex Johnson"
        userRole="Admin"
        company="Customer Churn Predictor"
        systemStatus="operational"
      />

      {/* ── 2. Quick Actions ── */}
      <QuickActionBar
        onRefresh={() => {
          setRefreshKey((k) => k + 1);
          refetch();
        }}
      />

      {/* ── 3. KPI Cards ── */}
      <section aria-label="Key Performance Indicators">
        <KPISection kpis={kpiData} />
      </section>

      {/* ── 4. AI Executive Summary ── */}
      <section aria-label="AI Executive Summary">
        <AISummaryCard />
      </section>

      {/* ── 6. Health + Distribution (2-col) ── */}

      <section
        aria-label="Client Health and Risk Distribution"
        className="grid grid-cols-1 lg:grid-cols-3 gap-4"
      >
        <ClientHealthOverview health={healthBreakdown} className="lg:col-span-2" />
        <RiskDistributionChart data={riskDistribution} />
      </section>

      {/* ── 6. Churn Trend Chart ── */}
      <section aria-label="Monthly Churn Trend">
        <ChurnTrendChart data={churnTrend} />
      </section>

      {/* ── 7. High Risk Table ── */}
      <section aria-label="High Risk Clients">
        <HighRiskClientsTable />
      </section>

      {/* ── 8. Activity + Workflow (2-col) ── */}
      <section
        aria-label="Activity and Workflow"
        className="grid grid-cols-1 lg:grid-cols-3 gap-4"
      >
        <RecentActivityTimeline className="lg:col-span-2" />
        <WorkflowStatusCard />
      </section>

      {/* ── 9. Recent Recommendations ── */}
      <section aria-label="Recent Recommendations">
        <RecentRecommendations />
      </section>

      {/* ── 10. AI Assistant Preview ── */}
      <section aria-label="AI Assistant Preview">
        <AIAssistantPreview />
      </section>

      {/* ── 11. Footer ── */}
      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="flex items-center justify-between py-4 border-t border-border"
      >
        <p className="text-[11.5px] text-muted-foreground">
          © 2025 Customer Churn Predictor · All rights reserved
        </p>
        <div className="flex items-center gap-4">
          <a href="#" className="text-[11.5px] text-muted-foreground hover:text-foreground transition-colors">Privacy</a>
          <a href="#" className="text-[11.5px] text-muted-foreground hover:text-foreground transition-colors">Terms</a>
          <a href="#" className="text-[11.5px] text-muted-foreground hover:text-foreground transition-colors">Support</a>
        </div>
      </motion.footer>

    </ContentWrapper>
  );
}

export default DashboardPage;