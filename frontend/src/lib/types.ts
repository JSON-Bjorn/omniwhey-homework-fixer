// User related types
export interface User {
    id: number;
    email: string;
    full_name: string;
    is_admin: boolean;
    created_at: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
}

// Template related types
export interface Template {
    id: number;
    title: string;
    description: string | null;
    structure: string; // JSON string
    is_public: boolean;
    owner_id: number;
    created_at: string;
    updated_at: string | null;
}

export interface TemplateCreate {
    title: string;
    description?: string;
    structure: string;
    is_public: boolean;
}

// PRD related types
export interface PRD {
    id: number;
    title: string;
    content: string;
    template_id: number | null;
    owner_id: number;
    created_at: string;
    updated_at: string | null;
}

export interface PRDCreate {
    title: string;
    content: string;
    template_id?: number;
}

// Collaboration related types
export interface Collaboration {
    id: number;
    prd_id: number;
    user_id: number;
    permission: 'read' | 'write' | 'admin';
    created_at: string;
    user?: User;
    prd?: PRD;
}

export interface CollaborationCreate {
    prd_id: number;
    user_id: number;
    permission: 'read' | 'write' | 'admin';
}

// Submission related types
export interface Submission {
    id: number;
    title: string;
    description: string | null;
    file_path: string;
    status: 'pending' | 'reviewed' | 'graded';
    user_id: number;
    created_at: string;
    updated_at: string | null;
    user?: User;
    feedback?: Feedback[];
}

export interface SubmissionCreate {
    title: string;
    description?: string;
    file: File;
}

// Feedback related types
export interface Feedback {
    id: number;
    content: string;
    grade: string | null;
    submission_id: number;
    created_at: string;
    updated_at: string | null;
    submission?: Submission;
}

export interface FeedbackCreate {
    content: string;
    grade?: string;
    submission_id: number;
}

// Pagination related types
export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    per_page: number;
    pages: number;
} 