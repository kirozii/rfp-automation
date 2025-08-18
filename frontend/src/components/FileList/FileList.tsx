import styles from "./FileList.module.css"
import type { fileStatus, FileProcessingState } from "@/types/types";
import ButtonArray from "../ButtonArray/ButtonArray.tsx"

interface FileListProps {
    uploadedFiles: fileStatus[];
    fileProcessingStatus: Record<string, FileProcessingState>;
    handleFileDownload: (rfpId: number, fileName: string) => void;
    generateAnswers: (rfpId: number) => Promise<void>;
    handleReviseFile: (rfpId: number, file: File) => Promise<void>;
    handleDownloadPPT: (rfpId: number, filename: string) => void;
    handleGeneratePPT: (rfpId: number) => Promise<void>;
}


const FileList: React.FC<FileListProps> = ({ uploadedFiles, fileProcessingStatus, handleFileDownload, handleReviseFile, generateAnswers, handleDownloadPPT, handleGeneratePPT }) => {
    return (
        uploadedFiles.length > 0 && (
            <div className={styles.listContainer}>
                <h3>Uploaded Files:</h3>
                <ul className={styles.ul}>
                    {uploadedFiles.map((file: fileStatus) => {
                        return (
                            <li key={file.rfp_id} className={styles.li}>
                                <div className={styles.container}>
                                    <span className={styles.id}>ID: {file.rfp_id}</span>
                                    <span className={styles.filename}>{file.filename}</span>
                                </div>
                                <ButtonArray file={file} fileProcessingStatus={fileProcessingStatus} handleFileDownload={handleFileDownload} handleReviseFile={handleReviseFile} generateAnswers={generateAnswers} handleDownloadPPT={handleDownloadPPT} handleGeneratePPT={handleGeneratePPT} />
                            </li>
                        )
                    })}
                </ul>
            </div>
        )
    )
}


export default FileList;
