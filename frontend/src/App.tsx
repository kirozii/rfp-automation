import FileList from './components/FileList/FileList';
import FileUploader from './components/FileUploader/FileUploader';
import useFileManagement from './hooks/useFileManagement';
import logo from './assets/mphasis_logo.png'
import './index.css'

function App() {
    const { status, uploadedFiles, handleFileUpload, handleFileDownload, handleGenerateAnswers, handleGeneratePPT, handleDownloadPPT } = useFileManagement();
    return (
        <div className="flex flex-col items-center justify-start min-h-screen bg-gray-100">
            <img src={logo} className="absolute top-5 left-5 w-50" />
            <header className="text-center mt-10">
                <h1 className="text-2xl font-semibold text-gray-800">RFP Generator</h1>
                <p className="text-sm text-gray-500">GenAI to help with RFPs</p>
            </header>
            <div className="mt-10 flex justify-center items-center w-full">
                <FileUploader status={status} onDrop={handleFileUpload} />
            </div>
            <div className="flex justify-center items-center w-3/4 ">
                <FileList uploadedFiles={uploadedFiles} handleFileDownload={handleFileDownload} generateAnswers={handleGenerateAnswers} handleGeneratePPT={handleGeneratePPT} handleDownloadPPT={handleDownloadPPT} />
            </div>
        </div>
    );
}

export default App;
