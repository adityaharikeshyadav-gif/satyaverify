export interface Evidence {
  id: number;
  evidence_id: string;
  filename: string;
  media_type: string;
  mime_type: string;
  sha256: string;
  size: number;
  ipfs_cid?: string;
  ai_prediction?: string;
  ai_confidence?: number;
  model_scores?: Record<string, any>;
  suspicious_frames?: Array<{ frame_number: number; timestamp: number; prediction: string; confidence: number }>;
  gemini_assessment?: any;
  features?: any;
  media_metadata?: any;
  model_version: string;
  status: string;
  blockchain_tx_hash?: string;
  created_at: string;
  updated_at?: string;
}

export interface ProvenanceEvent {
  id: number;
  evidence_id: number;
  event_type: string;
  description?: string;
  actor: string;
  tx_hash?: string;
  timestamp: string;
}

export interface Report {
  evidence_id: string;
  filename: string;
  generated_at: string;
  disclaimer: string;
  file_integrity: any;
  ml_analysis: any;
  gemini_assessment?: any;
  media_metadata: any;
  blockchain: any;
  provenance: any[];
}
