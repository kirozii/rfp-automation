export interface fileStatus {
    name: string,
    generated: boolean
    pptGenerated: boolean
}

export type FileProcessingState = 'idle' | 'generating_spreadsheet' | 'generating_ppt';
