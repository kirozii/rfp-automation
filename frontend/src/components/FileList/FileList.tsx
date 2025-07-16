import styles from "./FileList.module.css"

type FileProcessingState = 'idle' | 'generating_spreadsheet' | 'generating_ppt';

interface FileStore {
    name: string,
    generated: boolean,
    pptGenerated: boolean
}


interface FileListProps {
    uploadedFiles: FileStore[];
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
                    {uploadedFiles.map((file: FileStore) => {
                        return (
                            <li key={file.name} className={styles.li}>
                                {file.name}
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
                            </li>
                        )
                    })}
                </ul>
            </div>
        )
    )
}


export default FileList;
