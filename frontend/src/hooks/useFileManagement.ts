import { useCallback, useState, useEffect } from "react";
import { uploadFile, downloadFile, getUploadedFiles, generateAnswers, generatePPT, downloadPPT } from "@/services/FileService";

type FileProcessingState = 'idle' | 'generating_spreadsheet' | 'generating_ppt';
type uploadStatus = 'uploading' | 'error' | 'success' | 'idle';

interface fileStore {
    name: string,
    generated: boolean
    pptGenerated: boolean
}

interface UseFileUploadReturn {
    status: uploadStatus;
    uploadedFiles: fileStore[],
    fileProcessingStatus: Record<string, FileProcessingState>;
    handleFileUpload: (acceptedFile: File[]) => Promise<void>;
    handleFileDownload: (filename: string) => void;
    handleGenerateAnswers: (filename: string) => Promise<void>;
    handleGeneratePPT: (filename: string) => Promise<void>;
    handleDownloadPPT: (filename: string) => void;
}

const useFileManagement = (): UseFileUploadReturn => {
    const [status, setStatus] = useState<uploadStatus>('idle');
    const [uploadedFiles, setUploadedFiles] = useState<fileStore[]>([]);
    const [fileProcessingStatus, setFileProcessingStatus] = useState<Record<string, FileProcessingState>>({});

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
            const fetchedFiles = await getUploadedFiles();
            setUploadedFiles(fetchedFiles);
            console.log("FETCH: Files fetched:", fetchedFiles)
            const newProcessingStatus: Record<string, FileProcessingState> = {};
            fetchedFiles.forEach(file => {
                newProcessingStatus[file.name] = fileProcessingStatus[file.name] || 'idle';
            });

            setFileProcessingStatus(prevStatus => {
                const updatedStatus: Record<string, FileProcessingState> = {};
                fetchedFiles.forEach(file => {
                    updatedStatus[file.name] = prevStatus[file.name] || 'idle';
                });
                for (const key in prevStatus) {
                    if (!fetchedFiles.some(f => f.name === key)) {
                        delete updatedStatus[key];
                    }
                }
                return updatedStatus;
            });
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
        setFileProcessingStatus(prev => ({ ...prev, [filename]: 'generating_spreadsheet' }));
        try {
            await generateAnswers(filename);
            alert("Answers generated for " + filename);
            await refreshFiles();
            setUploadedFiles((prevFiles) =>
                prevFiles.map((file) =>
                    file.name === filename ? { ...file, generated: true } : file
                )
            );
        } catch (err) {
            console.log("ERROR: ", err);
        } finally {
            setFileProcessingStatus(prev => ({ ...prev, [filename]: 'idle' }));
        }
    }

    const handleGeneratePPT = async (filename: string) => {
        setFileProcessingStatus(prev => ({ ...prev, [filename]: 'generating_ppt' }));
        try {
            await generatePPT(filename);
            alert("PPT generated for " + filename);
            await refreshFiles();
            setUploadedFiles((prevFiles) =>
                prevFiles.map((file) =>
                    file.name === filename ? { ...file, pptGenerated: true } : file
                )
            );
        } catch (err) {
            console.log("ERROR: ", err);
        } finally {
            setFileProcessingStatus(prev => ({ ...prev, [filename]: 'idle' }));
        }
    }

    useEffect(() => { refreshFiles(); }, []);

    return {
        status,
        uploadedFiles,
        fileProcessingStatus,
        handleFileUpload,
        handleFileDownload,
        handleGenerateAnswers,
        handleGeneratePPT,
        handleDownloadPPT
    };
}

export default useFileManagement;
