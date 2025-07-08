import { useState, useEffect } from 'react';
import { uploadFile, getUploadedFiles, downloadFile } from '../services/fileService';
import { isValidExtension } from '../utils/validation';

const useFileUpload = (fileInputRef) => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isUploading, setIsUploading] = useState(false);

    const clearFileInput = () => {
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    const fetchFiles = async () => {
        try {
            const files = await getUploadedFiles();
            setUploadedFiles(files);
            console.log("FETCH: Files fetched: ", files);
        } catch (error) {
            console.error("FETCH: Error while fetching file: ", error);
            setUploadedFiles([]);
        }
    }

    const handleFileChange = (event) => {
        const file = event.target.files[0];

        if (!file) {
            setSelectedFile(null);
            clearFileInput();
            return;
        }

        if (!isValidExtension(file.name)) {
            alert('Invalid file type. Please use .xlsx files.');
            setSelectedFile(null);
            clearFileInput();
            return;
        }

        setSelectedFile(file);
    };

    const handleUploadClick = async () => {
        if (!selectedFile) {
            alert('Please select a file.');
            return;
        }

        setIsUploading(true);
        setUploadProgress(0);

        try {
            const response = await uploadFile(selectedFile, (progressEvent) => {
                setUploadProgress(Math.round((progressEvent.loaded * 100) / progressEvent.total));
            });
            alert('Uploaded successfully');
            setSelectedFile(null);
            clearFileInput();
            fetchFiles();
        } catch (error) {
            const errorMessage = error.response && error.response.data && error.response.data.detail ? error.response.data.detail : 'Unknown error during upload. Please try again.';
            alert(`Upload failed! ${errorMessage}`);
            console.error('Upload error:', error);
        } finally {
            setIsUploading(false);
            setUploadProgress(0);
        }
    };

    const handleSearchClick = () => {
        alert('To be implemented :(');
    };

    const handleFileDownload = (filename) => {
        downloadFile(filename);
    };

    useEffect(() => { fetchFiles(); }, []);

    return {
        selectedFile,
        uploadedFiles,
        uploadProgress,
        isUploading,
        handleFileChange,
        handleUploadClick,
        handleSearchClick,
        handleFileDownload
    };
};

export default useFileUpload;
