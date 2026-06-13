export interface DocumentItem {
  id: string;
  userId: string;
  filename: string;
  size: number;
  mimeType: string;
  uploadedAt?: string;
  previewText?: string;
  metadata: Record<string, unknown>;
  createdAt: string;
  updatedAt?: string;
}

export interface DocumentDetail {
  document: DocumentItem;
  previewUrl: string;
}
