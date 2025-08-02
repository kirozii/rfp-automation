export interface fileStatus {
    name: string,
    generated: boolean
    pptGenerated: boolean
    revised: boolean
}

export type FileProcessingState = 'idle' | 'generating_spreadsheet' | 'revising_file' | 'generating_ppt';
