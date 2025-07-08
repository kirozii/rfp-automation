import { useRef } from 'react';
import useFileUpload from '../hooks/useFileUpload';
import styles from './UploadComponent.module.css';

const UploadComponent = () => {
    const fileInputRef = useRef(null);
    const {
        selectedFile,
        uploadedFiles,
        uploadProgress,
        isUploading,
        handleFileChange,
        handleUploadClick,
        handleSearchClick,
        handleFileDownload,
    } = useFileUpload(fileInputRef);

    return (
        <div className={styles.container}>
            <h3>Upload your file</h3>

            <div className={styles.buttonContainer}>
                <input
                    type='file'
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                />

                <button
                    onClick={() => fileInputRef.current?.click()}
                    className={`${styles.baseButton} $styles.selectButton}`}
                >Select File</button>

                <button
                    onClick={handleUploadClick}
                    disabled={!selectedFile || isUploading}
                    className={`${styles.baseButton} ${selectedFile && !isUploading ? styles.uploadButtonEnabled : styles.uploadButtonDisabled}`}
                >{isUploading ? `Uploading... ${uploadProgress}%` : `Upload ${selectedFile ? `(${selectedFile.name})` : ''}`}</button>

                <button
                    onClick={handleSearchClick}
                    className={`${styles.baseButton} ${styles.listButton}`}
                >Search</button>
            </div>
            {selectedFile && (
                <p className={styles.selectedFileText}>Selected: <strong>{selectedFile.name}</strong></p>
            )}

            {isUploading && uploadProgress > 0 && uploadProgress < 100 && (
                <div className={styles.progressBarContainer}>
                    <div className={styles.progressBar} style={{ width: `${uploadProgress}%` }}>
                        {uploadProgress}%
                    </div>
                </div>
            )}

            {uploadedFiles.length > 0 && (
                <div className={styles.listContainer}>
                    <h4>Uploaded Files:</h4>
                    <ul className={styles.ul}>
                        {uploadedFiles.map((fileName) => (
                            <li key={fileName} className={styles.li}>
                                {fileName}
                                <button
                                    onClick={() => handleFileDownload(fileName)}
                                    className={styles.downloadButton}
                                >Download</button>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default UploadComponent;
