import UploadComponent from './components/UploadComponent.js'
import logo from './mphasis_logo.png';

function App() {
    return (
        <div className="App" style={{ textAlign: 'center', marginTop: '50px' }}>
            <img src={logo} style={{
                position: 'absolute',
                top: '20px',
                left: '20px',
                width: '200px'
            }} />
            <h1>RFP Response Generator</h1>
            <UploadComponent />
        </div>
    );
}

export default App;
