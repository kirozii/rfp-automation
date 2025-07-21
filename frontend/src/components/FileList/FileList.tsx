import styles from "./FileList.module.css"
import type { fileStatus, FileProcessingState } from "@/types/types";
import ButtonArray from "../ButtonArray/ButtonArray.tsx"

interface FileListProps {
    uploadedFiles: fileStatus[];
    fileProcessingStatus: Record<string, FileProcessingState>;
    handleFileDownload: (fileName: string) => void;
    generateAnswers: (fileName: string) => Promise<void>;
    handleDownloadPPT: (filename: string) => void;
    handleGeneratePPT: (filename: string) => Promise<void>;
}


const FileList: React.FC<FileListProps> = ({ uploadedFiles, fileProcessingStatus, handleFileDownload, generateAnswers, handleDownloadPPT, handleGeneratePPT }) => {
    return (
        uploadedFiles.length > 0 && (
            <div className={styles.listContainer}>
                <h3>Uploaded Files:</h3>
                <ul className={styles.ul}>
                    {uploadedFiles.map((file: fileStatus) => {
                        return (
                            <li key={file.name} className={styles.li}>
                                {file.name}
                                <ButtonArray file={file} fileProcessingStatus={fileProcessingStatus} handleFileDownload={handleFileDownload} generateAnswers={generateAnswers} handleDownloadPPT={handleDownloadPPT} handleGeneratePPT={handleGeneratePPT} />
                            </li>
                        )
                    })}
                </ul>
            </div>
        )
    )
}


export default FileList;
