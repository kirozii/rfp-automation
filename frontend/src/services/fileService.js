import axios from 'axios';
import { API_BASE_URL } from '../config/constants'

export const uploadFile = async (file, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${API_BASE_URL}/files/uploadfile/`, formData, {
        headers: {
            'Content-type': 'multipart/form-data',
        },
        onUploadProgress,
    });
    return response.data;
};

export const getUploadedFiles = async () => {
    const response = await axios.get(`${API_BASE_URL}/files`);
    return response.data;
};

export const downloadFile = (filename) => {
    console.log("DOWNLOAD: we are downloading the file", filename);
    const downloadURL = `${API_BASE_URL}/files/download/${filename}`;
    const link = document.createElement('a');
    link.href = downloadURL;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
