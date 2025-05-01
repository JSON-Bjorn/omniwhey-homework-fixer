
import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import FileUpload from '@/components/FileUpload';
import { Button } from '@/components/ui/button';

const Upload = () => {
  useEffect(() => {
    // Set page title
    document.title = 'Upload Homework | Omniwhey';
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      
      <main className="flex-grow bg-gray-50 py-12">
        <div className="container px-4 mx-auto">
          <div className="mb-8">
            <Link to="/dashboard" className="text-brand-purple hover:underline flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-2">
                <path d="m15 18-6-6 6-6"></path>
              </svg>
              Back to Dashboard
            </Link>
          </div>
          
          <div className="text-center mb-12">
            <h1 className="text-3xl font-bold mb-3 gradient-heading">Upload Your Homework</h1>
            <p className="text-gray-600 max-w-xl mx-auto">
              Upload your assignment to get AI-powered feedback and suggestions for improvement.
            </p>
          </div>
          
          <FileUpload />
          
          <div className="mt-16 bg-white rounded-lg p-6 border border-gray-100 shadow-sm">
            <h2 className="text-xl font-semibold mb-4">Supported Files</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 p-4 rounded-md flex items-center">
                <div className="mr-3 text-red-500">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium">PDF</h3>
                  <p className="text-xs text-gray-500">Adobe PDF Documents</p>
                </div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-md flex items-center">
                <div className="mr-3 text-blue-500">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium">DOCX</h3>
                  <p className="text-xs text-gray-500">Microsoft Word Documents</p>
                </div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-md flex items-center">
                <div className="mr-3 text-gray-500">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <line x1="10" y1="9" x2="8" y2="9"></line>
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium">TXT</h3>
                  <p className="text-xs text-gray-500">Plain Text Files</p>
                </div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-md flex items-center">
                <div className="mr-3 text-orange-500">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <path d="M12 18v-6"></path>
                    <path d="M8 18v-1"></path>
                    <path d="M16 18v-3"></path>
                  </svg>
                </div>
                <div>
                  <h3 className="font-medium">IPYNB</h3>
                  <p className="text-xs text-gray-500">Jupyter Notebooks</p>
                </div>
              </div>
            </div>
            
            <div className="mt-6 text-sm text-gray-500">
              <p>Max file size: 10MB. For optimal results, ensure your files are properly formatted.</p>
              <p className="mt-2">Need help? <a href="/help" className="text-brand-purple hover:underline">Contact our support team</a>.</p>
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default Upload;
