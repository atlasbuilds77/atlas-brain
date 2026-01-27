// ============================================
// KRONOS TYPE DEFINITIONS
// ============================================

// User & Auth
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'staff' | 'client';
  avatar?: string;
  createdAt: string;
  lastActive: string;
}

// Leads
export type LeadStatus = 'new' | 'contacted' | 'qualified' | 'converted' | 'dead';
export type LeadSource = 'website' | 'referral' | 'social' | 'ads' | 'other';

export interface Lead {
  id: string;
  name: string;
  email: string;
  phone?: string;
  source: LeadSource;
  status: LeadStatus;
  score: number; // 0-100
  assignedTo?: string;
  notes?: string;
  tags: string[];
  createdAt: string;
  convertedAt?: string;
  lastContact?: string;
}

export interface LeadQualification {
  leadId: string;
  questions: QualificationQuestion[];
  completedAt?: string;
  score: number;
}

export interface QualificationQuestion {
  id: string;
  question: string;
  answer?: string;
  weight: number;
}

// Clients
export type ClientStatus = 'active' | 'inactive' | 'churned';

export interface Client {
  id: string;
  userId: string;
  name: string;
  email: string;
  phone?: string;
  company?: string;
  status: ClientStatus;
  clientSince: string;
  lifetimeValue: number;
  retentionRisk: number; // 0-100
  lastInteraction: string;
  nextFollowup?: string;
  tags: string[];
  notes?: string;
}

export interface ClientFile {
  id: string;
  clientId: string;
  filename: string;
  path: string;
  category: string;
  year?: number;
  encrypted: boolean;
  uploadedAt: string;
  size: number;
}

// Messages
export type MessageChannel = 'email' | 'sms' | 'web' | 'phone';
export type MessageCategory = 'prospective' | 'client' | 'office' | 'other';
export type MessageStatus = 'unread' | 'read' | 'archived' | 'flagged';

export interface Message {
  id: string;
  threadId: string;
  from: MessageParticipant;
  to: MessageParticipant[];
  channel: MessageChannel;
  category: MessageCategory;
  status: MessageStatus;
  subject?: string;
  body: string;
  preview: string;
  timestamp: string;
  attachments: Attachment[];
  isIncoming: boolean;
}

export interface MessageParticipant {
  id: string;
  name: string;
  email?: string;
  phone?: string;
}

export interface MessageThread {
  id: string;
  participants: MessageParticipant[];
  subject?: string;
  lastMessage: string;
  lastMessageAt: string;
  messageCount: number;
  unreadCount: number;
  category: MessageCategory;
}

export interface Attachment {
  id: string;
  filename: string;
  size: number;
  mimeType: string;
  url: string;
}

// Tax Organizers
export type OrganizerStatus = 'draft' | 'sent' | 'opened' | 'in_progress' | 'completed' | 'expired';

export interface TaxOrganizer {
  id: string;
  clientId: string;
  clientName: string;
  year: number;
  status: OrganizerStatus;
  templateId: string;
  sentAt?: string;
  openedAt?: string;
  completedAt?: string;
  dueDate?: string;
  progress: number; // 0-100
  sections: OrganizerSection[];
}

export interface OrganizerSection {
  id: string;
  title: string;
  completed: boolean;
  requiredFields: number;
  completedFields: number;
}

export interface OrganizerTemplate {
  id: string;
  name: string;
  year: number;
  sections: OrganizerSection[];
  isDefault: boolean;
}

// Tasks
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignedTo?: string;
  clientId?: string;
  dueDate?: string;
  completedAt?: string;
  createdAt: string;
}

// Analytics
export interface AnalyticsSummary {
  totalLeads: number;
  newLeadsThisMonth: number;
  conversionRate: number;
  totalClients: number;
  activeClients: number;
  churnRate: number;
  revenueThisMonth: number;
  revenueTrend: number; // percentage change
}

export interface LeadSourceData {
  source: LeadSource;
  count: number;
  converted: number;
  conversionRate: number;
}

export interface TimeSeriesData {
  date: string;
  value: number;
}

export interface RetentionData {
  cohort: string;
  months: number[];
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Filter Types
export interface LeadFilters {
  status?: LeadStatus[];
  source?: LeadSource[];
  assignedTo?: string;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
}

export interface ClientFilters {
  status?: ClientStatus[];
  search?: string;
  riskLevel?: 'low' | 'medium' | 'high';
}

export interface MessageFilters {
  category?: MessageCategory[];
  status?: MessageStatus[];
  channel?: MessageChannel[];
  search?: string;
  dateFrom?: string;
  dateTo?: string;
}
