import { useCallback, useState, useEffect } from "react";
import { uploadFile, downloadFile, getUploadedFiles, generateAnswers, generatePPT, downloadPPT } from "@/services/FileService";

type uploadStatus = 'uploading' | 'error' | 'success' | 'idle';

interface fileStore {
    name: string,
    generated: boolean
    pptGenerated: boolean
}

interface UseFileUploadReturn {
    status: uploadStatus;
    uploadedFiles: fileStore[],
    handleFileUpload: (acceptedFile: File[]) => Promise<void>;
    handleFileDownload: (filename: string) => void;
    handleGenerateAnswers: (filename: string) => void;
    handleGeneratePPT: (filename: string) => void;
    handleDownloadPPT: (filename: string) => void;
}

const useFileManagement = (): UseFileUploadReturn => {
    const [status, setStatus] = useState<uploadStatus>('idle');
    const [uploadedFiles, setUploadedFiles] = useState<fileStore[]>([]);

    const handleFileUpload = useCallback(async (acceptedFile: File[]) => {
        if (acceptedFile.length === 0) return;
        setStatus('uploading');
        const file = acceptedFile[0]

        try {
            await uploadFile(file);
            setStatus("success");
            alert("File uploaded successfully!");
            refreshFiles();
        } catch (err) {
            setStatus('error');
            alert("There was an error uploading the file.");
        } finally {
            setStatus('idle');
        }

    }, []);

    const refreshFiles = async () => {
        try {
            const files = await getUploadedFiles();
            setUploadedFiles(files);
            console.log("FETCH: Files fetched:", files)
        } catch (err) {
            console.error("FETCH: Error while fetching file: ", err);
            setUploadedFiles([]);
        }
    }

    const handleFileDownload = (filename: string) => {
        downloadFile(filename);
    }

    const handleDownloadPPT = (filename: string) => {
        downloadPPT(filename);
    }

    const handleGenerateAnswers = async (filename: string) => {
        try {
            await generateAnswers(filename);
            alert("Answers generated for " + filename);
            refreshFiles();
            setUploadedFiles((prevFiles) =>
                prevFiles.map((file) =>
                    file.name === filename ? { ...file, generated: true } : file
                )
            );
        } catch (err) {
            console.log("ERROR: ", err);
        }
    }

    const handleGeneratePPT = async (filename: string) => {
        try {
            await generatePPT(filename);
            alert("PPT generated for " + filename);
            refreshFiles();
            setUploadedFiles((prevFiles) =>
                prevFiles.map((file) =>
                    file.name === filename ? { ...file, pptGenerated: true } : file
                )
            );
        } catch (err) {
            console.log("ERROR: ", err);
        }
    }

    useEffect(() => { refreshFiles(); }, []);

    return {
        status,
        uploadedFiles,
        handleFileUpload,
        handleFileDownload,
        handleGenerateAnswers,
        handleGeneratePPT,
        handleDownloadPPT
    };
}

export default useFileManagement;
