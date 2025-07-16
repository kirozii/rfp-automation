import axios from 'axios';
import { API_BASE_URL } from '../config/constants'

interface UploadResponse {
    message: string
}

interface fileStore {
    name: string,
    generated: boolean,
    pptGenerated: boolean
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

export const getUploadedFiles = async (): Promise<fileStore[]> => {
    const response = await axios.get(`${API_BASE_URL}/files`);
    console.log(response.data)
    return response.data;
};

export const downloadFile = (filename: string): void => {
    console.log("DOWNLOAD: we are downloading the file: ", filename);
    const downloadURL = `${API_BASE_URL}/files/download/${filename}`;
    const link = document.createElement('a');
    link.href = downloadURL;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

export const downloadPPT = (filename: string): void => {
    console.log("DOWNLOAD: we are downloading the file: ", filename);
    const downloadURL = `${API_BASE_URL}/files/downloadppt/${filename}`;
    const link = document.createElement('a');
    link.href = downloadURL;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

export const generatePPT = async (filename: string) => {
    console.log("PPTGEN: Generating ppt for file: ", filename)
    const generateURL = `${API_BASE_URL}/files/generateppt/${filename}`;

    const response = await axios.post(generateURL, null, {
        headers: {
            'Content-type': 'application/json',
        },
    });
    console.log("PPTGEN: Successfully generated ppt for: ", filename);
    return response;
}

export const generateAnswers = async (filename: string) => {
    console.log("GENERATE: Generating answers for file: ", filename)
    const generateURL = `${API_BASE_URL}/files/generate/${filename}`;

    const response = await axios.post(generateURL, null, {
        headers: {
            'Content-type': 'application/json',
        },
    });
    console.log("GENERATE: Successfully generated file: ", filename);

    return response;
}
