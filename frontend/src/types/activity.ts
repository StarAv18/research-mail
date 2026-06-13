export interface ActivityLogItem {
  id: string;
  userId: string;
  eventType: string;
  entityType: string;
  entityId?: string;
  details: Record<string, unknown>;
  createdAt: string;
  updatedAt?: string;
}

export interface AnalyticsSeriesItem {
  date: string;
  value: number;
}

export interface DashboardAnalytics {
  dailyOutreach: AnalyticsSeriesItem[];
  weeklyOutreach: AnalyticsSeriesItem[];
  monthlyOutreach: AnalyticsSeriesItem[];
  professorsDiscovered: number;
  draftsGenerated: number;
  emailsSent: number;
  responsesReceived: number;
}
