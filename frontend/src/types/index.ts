export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: number;
  role: "user" | "assistant" | "system";
  content: string;
  sources?: SourceItem[];
  created_at: string;
}

export interface SourceItem {
  content: string;
  source: string;
  score: number;
}

export interface Document {
  id: number;
  filename: string;
  file_type: string;
  chunk_count: number;
  status: string;
  created_at: string;
}

export interface MonitoringStats {
  users: number;
  conversations: number;
  messages: number;
  documents: number;
  services: Record<string, string>;
  app: Record<string, string>;
}
