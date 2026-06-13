export interface Campaign {
  id: string;
  userId: string;
  name: string;
  status: string;
  totalDrafts: number;
  sentCount: number;
  failedCount: number;
  retryCount: number;
  lastError?: string;
  executedAt?: string;
  createdAt: string;
  updatedAt?: string;
}

export interface CampaignDetail {
  campaign: Campaign;
  draftIds: string[];
}

export interface CampaignExecutionResult {
  campaignId: string;
  sent: number;
  failed: number;
  retried: number;
}

export interface CampaignLog {
  id: string;
  recipientEmail: string;
  status: string;
  messageId?: string;
  errorMessage?: string;
  sentAt?: string;
  createdAt: string;
}
