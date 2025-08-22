export interface fileStatus {
    rfp_id: number,
    filename: string,
    uploaded_at: string,
    status: string
}

export type FileProcessingState = 'idle' | 'generating_spreadsheet' | 'revising_file' | 'generating_ppt';
