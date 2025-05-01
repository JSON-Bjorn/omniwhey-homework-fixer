
import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import AuthForm from '@/components/AuthForm';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

const Login = () => {
  useEffect(() => {
    // Set page title
    document.title = 'Login | Omniwhey';
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      
      <main className="flex-grow flex items-center justify-center bg-gray-50 py-12">
        <div className="container px-4 mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16">
            <div className="w-full max-w-md">
              <div className="text-center mb-6">
                <h1 className="text-2xl md:text-3xl font-bold mb-2 gradient-heading">Welcome to Omniwhey</h1>
                <p className="text-gray-600">
                  Sign in to your account or create a new one to get started.
                </p>
              </div>
              
              <AuthForm />
              
              <div className="text-center mt-8">
                <p className="text-sm text-gray-500">
                  By continuing, you agree to Omniwhey's{" "}
                  <Link to="/terms" className="text-brand-purple hover:underline">
                    Terms of Service
                  </Link>{" "}
                  and{" "}
                  <Link to="/privacy" className="text-brand-purple hover:underline">
                    Privacy Policy
                  </Link>
                  .
                </p>
              </div>
            </div>
            
            <div className="hidden md:block w-full max-w-md">
              <div className="bg-white p-8 rounded-2xl border border-gray-100 shadow-md">
                <h3 className="text-xl font-semibold mb-4">Why students love Omniwhey</h3>
                
                <ul className="space-y-4">
                  <li className="flex gap-3">
                    <div className="bg-brand-purple-light/20 rounded-full p-1">
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-brand-purple">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                      </svg>
                    </div>
                    <div>
                      <h4 className="font-medium">Detailed Feedback</h4>
                      <p className="text-sm text-gray-500">Receive comprehensive feedback on your homework</p>
                    </div>
                  </li>
                  
                  <li className="flex gap-3">
                    <div className="bg-brand-purple-light/20 rounded-full p-1">
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-brand-purple">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                      </svg>
                    </div>
                    <div>
                      <h4 className="font-medium">Instant Results</h4>
                      <p className="text-sm text-gray-500">No more waiting days for teacher feedback</p>
                    </div>
                  </li>
                  
                  <li className="flex gap-3">
                    <div className="bg-brand-purple-light/20 rounded-full p-1">
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-brand-purple">
                        <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path>
                        <path d="m9 12 2 2 4-4"></path>
                      </svg>
                    </div>
                    <div>
                      <h4 className="font-medium">Learn From Mistakes</h4>
                      <p className="text-sm text-gray-500">Understand where you went wrong and how to improve</p>
                    </div>
                  </li>
                  
                  <li className="flex gap-3">
                    <div className="bg-brand-purple-light/20 rounded-full p-1">
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-brand-purple">
                        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                      </svg>
                    </div>
                    <div>
                      <h4 className="font-medium">Track Progress</h4>
                      <p className="text-sm text-gray-500">Monitor your improvement over time</p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default Login;
