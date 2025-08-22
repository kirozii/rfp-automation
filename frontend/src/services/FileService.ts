import axios from 'axios';
import { API_BASE_URL } from '../config/constants'
import type { fileStatus } from '@/types/types';

interface UploadResponse {
    message: string
}

export const uploadFile = async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_BASE_URL}/files/uploadfile/`, formData, {
        headers: {
            'Content-type': 'multipart/form-data',
        }
    });
    return response.data;
};

export const getUploadedFiles = async (): Promise<fileStatus[]> => {
    const response = await axios.get(`${API_BASE_URL}/files`);
    console.log(response.data)
    return response.data;
};

export const downloadFile = (rfpId: number, filename: string): void => {
    console.log("DOWNLOAD: we are downloading the file: ", rfpId);
    const downloadURL = `${API_BASE_URL}/files/download/${rfpId}`;
    const link = document.createElement('a');
    link.href = downloadURL;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

export const reviseFile = async (rfpId: number, file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file)

    const response = await axios.post(`${API_BASE_URL}/files/revise/${rfpId}`, formData, {
        headers: {
            'Content-type': 'multipart/form-data',
        }
    });
    return response.data;
}

export const downloadPPT = (rfpId: number, filename: string): void => {
    console.log("DOWNLOAD: we are downloading the file: ", filename);
    const downloadURL = `${API_BASE_URL}/files/downloadppt/${rfpId}`;
    const link = document.createElement('a');
    link.href = downloadURL;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

export const generatePPT = async (rfpId: number) => {
    console.log("PPTGEN: Generating ppt for file: ", rfpId)
    const generateURL = `${API_BASE_URL}/files/generateppt/${rfpId}`;

    const response = await axios.post(generateURL, null, {
        headers: {
            'Content-type': 'application/json',
        },
    });
    console.log("PPTGEN: Successfully generated ppt for: ", rfpId);
    return response;
}

export const generateAnswers = async (rfpId: number) => {
    console.log("GENERATE: Generating answers for file: ", rfpId)
    const generateURL = `${API_BASE_URL}/files/generate/${rfpId}`;

    const response = await axios.post(generateURL, null, {
        headers: {
            'Content-type': 'application/json',
        },
    });
    console.log("GENERATE: Successfully generated file: ", rfpId);

    return response;
}
