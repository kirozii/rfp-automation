import type { fileStatus, FileProcessingState } from "../../types/types"
import styles from "./ButtonArray.module.css"

interface ButtonArrayProps {
    file: fileStatus
    fileProcessingStatus: Record<string, FileProcessingState>;
    handleFileDownload: (fileName: string) => void;
    generateAnswers: (fileName: string) => Promise<void>;
    handleDownloadPPT: (filename: string) => void;
    handleGeneratePPT: (filename: string) => Promise<void>;
}

const ButtonArray: React.FC<ButtonArrayProps> = ({ file, fileProcessingStatus, handleFileDownload, generateAnswers, handleDownloadPPT, handleGeneratePPT }) => {
    return (
        <div>
            {file.generated && (
                <>
                    {!file.pptGenerated ? (
                        <button
                            onClick={() => handleGeneratePPT(file.name)}
                            disabled={fileProcessingStatus[file.name] === 'generating_ppt'}
                            className={styles.downloadButton}
                        >
                            {fileProcessingStatus[file.name] === 'generating_ppt' ? "Generating PPT..." : "Generate PPT"}</button>
                    ) : (
                        <button
                            onClick={() => handleDownloadPPT(file.name)}
                            className={styles.downloadButton}
                        >Download PPT</button>
                    )}
                </>
            )}
            {file.generated ? (
                <button
                    onClick={() => handleFileDownload(file.name)}
                    className={styles.downloadButton}
                >Download Spreadsheet</button>
            ) : (
                <button
                    onClick={() => generateAnswers(file.name)}
                    disabled={fileProcessingStatus[file.name] === 'generating_spreadsheet'}
                    className={styles.downloadButton}
                >{fileProcessingStatus[file.name] === 'generating_spreadsheet' ? "Generating answers..." : "Generate Spreadsheet"}</button>
            )}
        </div>
    )
}

export default ButtonArray;
