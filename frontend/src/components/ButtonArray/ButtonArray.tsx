import type { fileStatus, FileProcessingState } from "../../types/types"
import { useState, useCallback, useRef } from "react";
import styles from "./ButtonArray.module.css"

interface ButtonArrayProps {
    file: fileStatus
    fileProcessingStatus: Record<string, FileProcessingState>;
    handleFileDownload: (fileName: string) => void;
    generateAnswers: (fileName: string) => Promise<void>;
    handleDownloadPPT: (filename: string) => void;
    handleGeneratePPT: (filename: string) => Promise<void>;
    handleReviseFile: (filename: string, file: File) => Promise<void>;
}

const ButtonArray: React.FC<ButtonArrayProps> = ({ file, fileProcessingStatus, handleFileDownload, generateAnswers, handleDownloadPPT, handleGeneratePPT, handleReviseFile }) => {
    const hiddenFileInput = useRef<HTMLInputElement>(null);

    const onRevisionFileChange = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files.length > 0) {
            const fileToUpload = event.target.files[0];
            await handleReviseFile(file.name, fileToUpload);
        }
    }, [file.name, handleReviseFile]);

    const handleReviseButtonClick = useCallback(() => {
        if (hiddenFileInput.current) {
            hiddenFileInput.current.click();
        }
    }, []);

    const isProcessing = fileProcessingStatus[file.name] !== 'idle';

    return (
        <div>
            {file.generated && !file.revised ? (
                <>
                    <input
                        type="file"
                        ref={hiddenFileInput}
                        onChange={onRevisionFileChange}
                        accept=".xlsx"
                        style={{ display: 'none' }}
                    />
                    <button
                        onClick={handleReviseButtonClick}
                        disabled={isProcessing || fileProcessingStatus[file.name] === 'revising_file'}
                        className={styles.downloadButton}
                    >
                        {fileProcessingStatus[file.name] === 'revising_file' ? "Uploading Revision..." : "Upload Revised File"}
                    </button>
                </>
            ) : file.generated && file.revised ? (
                <>
                    {!file.pptGenerated ? (
                        <button
                            onClick={() => handleGeneratePPT(file.name)}
                            disabled={isProcessing || fileProcessingStatus[file.name] === 'generating_ppt'}
                            className={styles.downloadButton}
                        >
                            {fileProcessingStatus[file.name] === 'generating_ppt' ? "Generating PPT..." : "Generate PPT"}
                        </button>
                    ) : (
                        <button
                            onClick={() => handleDownloadPPT(file.name)}
                            className={styles.downloadButton}
                            disabled={isProcessing}
                        >
                            Download PPT
                        </button>
                    )}
                </>
            ) : (
                null
            )}
            {file.generated ? (
                <button
                    onClick={() => handleFileDownload(file.name)}
                    className={styles.downloadButton}
                    disabled={isProcessing}
                >
                    Download Spreadsheet
                </button>
            ) : (
                <button
                    onClick={() => generateAnswers(file.name)}
                    disabled={isProcessing || fileProcessingStatus[file.name] === 'generating_spreadsheet'}
                    className={styles.downloadButton}
                >
                    {fileProcessingStatus[file.name] === 'generating_spreadsheet' ? "Generating answers..." : "Generate Spreadsheet"}
                </button>
            )}
        </div>
    );
}

export default ButtonArray;
