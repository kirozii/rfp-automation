import type { fileStatus, FileProcessingState } from "../../types/types"
import { useState, useCallback, useRef } from "react";
import styles from "./ButtonArray.module.css"

interface ButtonArrayProps {
    file: fileStatus
    fileProcessingStatus: Record<number, FileProcessingState>;
    handleFileDownload: (rfpId: number, fileName: string) => void;
    generateAnswers: (rfpId: number) => Promise<void>;
    handleReviseFile: (rfpId: number, file: File) => Promise<void>;
    handleDownloadPPT: (rfpId: number, filename: string) => void;
    handleGeneratePPT: (rfpId: number) => Promise<void>;
}

const ButtonArray: React.FC<ButtonArrayProps> = ({ file, fileProcessingStatus, handleFileDownload, generateAnswers, handleDownloadPPT, handleGeneratePPT, handleReviseFile }) => {
    const hiddenFileInput = useRef<HTMLInputElement>(null);

    const onRevisionFileChange = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files.length > 0) {
            const fileToUpload = event.target.files[0];
            await handleReviseFile(file.rfp_id, fileToUpload);
        }
    }, [file.rfp_id, handleReviseFile]);

    const handleReviseButtonClick = useCallback(() => {
        if (hiddenFileInput.current) {
            hiddenFileInput.current.click();
        }
    }, []);

    const isProcessing = fileProcessingStatus[file.rfp_id] !== 'idle';

    return (
        <div>
            {file.status === "pending_review" ? (
                <>
                    <input
                        type="file"
                        ref={hiddenFileInput}
                        onChange={onRevisionFileChange}
                        accept=".xlsx"
                        style={{ display: 'none' }}
                    />
                    <button
                        onClick={() => handleFileDownload(file.rfp_id, file.filename)}
                        className={styles.downloadButton}
                        disabled={isProcessing}
                    >
                        Download Spreadsheet
                    </button>
                    <button
                        onClick={handleReviseButtonClick}
                        disabled={isProcessing || fileProcessingStatus[file.rfp_id] === 'revising_file'}
                        className={styles.downloadButton}
                    >
                        {fileProcessingStatus[file.rfp_id] === 'revising_file' ? "Uploading Revision..." : "Upload Revised File"}
                    </button>
                </>
            ) : file.status === "reviewed" ? (
                <>
                    <button
                        onClick={() => handleFileDownload(file.rfp_id, file.filename)}
                        className={styles.downloadButton}
                        disabled={isProcessing}
                    >
                        Download Spreadsheet
                    </button>
                    <button
                        onClick={() => handleGeneratePPT(file.rfp_id)}
                        disabled={isProcessing || fileProcessingStatus[file.rfp_id] === 'generating_ppt'}
                        className={styles.downloadButton}
                    >
                        {fileProcessingStatus[file.rfp_id] === 'generating_ppt' ? "Generating PPT..." : "Generate PPT"}
                    </button>
                </>
            ) : file.status === "completed" ? (
                <>
                    <button
                        onClick={() => handleFileDownload(file.rfp_id, file.filename)}
                        className={styles.downloadButton}
                        disabled={isProcessing}
                    >
                        Download Spreadsheet
                    </button>
                    <button
                        onClick={() => handleDownloadPPT(file.rfp_id, file.filename)}
                        className={styles.downloadButton}
                        disabled={isProcessing}
                    >
                        Download PPT
                    </button>
                </>
            ) : file.status === "uploaded" ? (
                <button
                    onClick={() => generateAnswers(file.rfp_id)}
                    disabled={isProcessing || fileProcessingStatus[file.rfp_id] === 'generating_spreadsheet'}
                    className={styles.downloadButton}
                >
                    {fileProcessingStatus[file.rfp_id] === 'generating_spreadsheet' ? "Generating answers..." : "Generate Spreadsheet"}
                </button>
            ) : (
                null
            )}
        </div>
    );
}

export default ButtonArray;
