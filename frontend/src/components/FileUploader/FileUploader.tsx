import styles from "./FileUploader.module.css"
import { useDropzone } from "react-dropzone";
import { FiUpload } from "react-icons/fi";

interface FileUploaderProps {
    status: 'uploading' | 'error' | 'success' | 'idle'
    onDrop: (acceptedFile: File[]) => void;
}

const FileUploader: React.FC<FileUploaderProps> = ({ status, onDrop }) => {
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        multiple: false,
        accept: {
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
        }
    });

    return (
        <div
            {...getRootProps()}
            className={`${styles.dropzone} ${isDragActive ? styles.dropzoneActive : ""}`}
        >
            <input {...getInputProps()} />
            <div className={styles.icon}>
                <FiUpload />
            </div>
            <p className={styles.message}>
                Drag and drop file or <span className={styles.browse}>Browse</span>
            </p>
            <p className={styles.supportedFormats}>
                Supported formats: .xlsx
            </p>
            {status === "uploading" && <p className={styles.message}>Uploading...</p>}
            {status === "error" && <p className={styles.error}>Error</p>}
            {status === "success" && <p className={styles.success}>File uploaded successfully!</p>}
        </div>
    );
}

export default FileUploader;
