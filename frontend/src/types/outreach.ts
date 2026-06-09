export enum DraftStatus {
  PENDING = 'pending',
  EDITED = 'edited',
  READY = 'ready',
  SENT = 'sent',
  FAILED = 'failed',
  ARCHIVED = 'archived',
}

export interface Draft {
  id: string;
  professorName: string;
  professorEmail: string;
  university: string;
  subject: string;
  body: string;
  status: DraftStatus;
  createdAt: string;
  updatedAt: string;
}

export interface OutreachHistory {
  id: string;
  professorEmail: string;
  sentAt: string;
  status: string;
  provider: string;
  messageId: string;
  subject: string;
}
