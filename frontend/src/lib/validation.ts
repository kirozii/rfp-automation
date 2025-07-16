import { ALLOWED_EXTENSIONS } from '../config/constants';

export const isValidExtension = (filename: string): boolean => {
    const extension = filename.substring(filename.lastIndexOf('.')).toLowerCase();
    console.log('VALIDATION: validated file!');
    return ALLOWED_EXTENSIONS.includes(extension);
}
