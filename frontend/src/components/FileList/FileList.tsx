import styles from "./FileList.module.css"

interface FileStore {
    name: string,
    generated: boolean,
    pptGenerated: boolean
}

interface FileListProps {
    uploadedFiles: FileStore[];
    handleFileDownload: (fileName: string) => void;
    generateAnswers: (fileName: string) => void;
    handleDownloadPPT: (filename: string) => void;
    handleGeneratePPT: (filename: string) => void;
}

const FileList: React.FC<FileListProps> = ({ uploadedFiles, handleFileDownload, generateAnswers, handleDownloadPPT, handleGeneratePPT }) => {
    return (
        uploadedFiles.length > 0 && (
            <div className={styles.listContainer}>
                <h3>Uploaded Files:</h3>
                <ul className={styles.ul}>
                    {uploadedFiles.map((file: FileStore) => (
                        <li key={file.name} className={styles.li}>
                            {file.name}
                            <div>
                                {file.generated && (
                                    <>
                                        {!file.pptGenerated ? (
                                            <button
                                                onClick={() => handleGeneratePPT(file.name)}
                                                className={styles.downloadButton}
                                            >Generate PPT</button>
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
                                        className={styles.downloadButton}
                                    >Generate Spreadsheet</button>
                                )}
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
        )
    )
}


export default FileList;
