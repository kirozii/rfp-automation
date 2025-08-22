import { useCallback, useState, useEffect } from "react";
import { uploadFile, downloadFile, getUploadedFiles, generateAnswers, generatePPT, downloadPPT, reviseFile } from "@/services/FileService";
import type { fileStatus, FileProcessingState } from "../types/types.ts"

type uploadStatus = 'uploading' | 'error' | 'success' | 'idle';

interface UseFileUploadReturn {
    status: uploadStatus;
    uploadedFiles: fileStatus[],
    fileProcessingStatus: Record<string, FileProcessingState>;
    handleFileUpload: (acceptedFile: File[]) => Promise<void>;
    handleFileDownload: (rfpId: number, filename: string) => void;
    handleReviseFile: (rfpId: number, file: File) => Promise<void>;
    handleGenerateAnswers: (rfpId: number) => Promise<void>;
    handleGeneratePPT: (rfpId: number) => Promise<void>;
    handleDownloadPPT: (rfpId: number, filename: string) => void;
}

const useFileManagement = (): UseFileUploadReturn => {
    const [status, setStatus] = useState<uploadStatus>('idle');
    const [uploadedFiles, setUploadedFiles] = useState<fileStatus[]>([]);
    const [fileProcessingStatus, setFileProcessingStatus] = useState<Record<number, FileProcessingState>>({});

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

    const refreshFiles = useCallback(async () => {
        try {
            const fetchedFiles = await getUploadedFiles();
            setUploadedFiles(fetchedFiles);
            console.log("FETCH: Files fetched:", fetchedFiles)

            setFileProcessingStatus(prevStatus => {
                const updatedStatus: Record<string, FileProcessingState> = {};
                fetchedFiles.forEach(file => {
                    updatedStatus[file.rfp_id] = prevStatus[file.rfp_id] || 'idle';
                });
                return updatedStatus;
            });
        } catch (err) {
            console.error("FETCH: Error while fetching file: ", err);
            setUploadedFiles([]);
        }
    }, []);

    const handleFileDownload = useCallback((rfpId: number, filename: string) => {
        downloadFile(rfpId, filename);
    }, []);

    const handleReviseFile = useCallback(async (rfpId: number, file: File) => {
        setFileProcessingStatus(prev => ({ ...prev, [rfpId]: 'revising_file' }));
        try {
            await reviseFile(rfpId, file);
            alert("Uploaded revised file successfully");
            await refreshFiles();
        } catch (err) {
            console.error("REVISE: Error while revising file:", err);
            alert("Error while revising. Check console.");
        } finally {
            setFileProcessingStatus(prev => ({ ...prev, [rfpId]: 'idle' }));
        }
    }, [refreshFiles]);

    const handleDownloadPPT = useCallback((rfpId: number, filename: string) => {
        downloadPPT(rfpId, filename);
    }, []);

    const handleGenerateAnswers = async (rfpId: number) => {
        setFileProcessingStatus(prev => ({ ...prev, [rfpId]: 'generating_spreadsheet' }));
        try {
            await generateAnswers(rfpId);
            alert("Answers generated for " + rfpId);
            await refreshFiles();
        } catch (err) {
            console.log("ERROR: ", err);
        } finally {
            setFileProcessingStatus(prev => ({ ...prev, [rfpId]: 'idle' }));
        }
    }

    const handleGeneratePPT = async (rfpId: number) => {
        setFileProcessingStatus(prev => ({ ...prev, [rfpId]: 'generating_ppt' }));
        try {
            await generatePPT(rfpId);
            alert("PPT generated for id: " + rfpId);
            await refreshFiles();
        } catch (err) {
            console.log("ERROR: ", err);
        } finally {
            setFileProcessingStatus(prev => ({ ...prev, [rfpId]: 'idle' }));
        }
    }

    useEffect(() => { refreshFiles(); }, [refreshFiles]);

    return {
        status,
        uploadedFiles,
        fileProcessingStatus,
        handleFileUpload,
        handleFileDownload,
        handleReviseFile,
        handleGenerateAnswers,
        handleGeneratePPT,
        handleDownloadPPT
    };
}

export default useFileManagement;
