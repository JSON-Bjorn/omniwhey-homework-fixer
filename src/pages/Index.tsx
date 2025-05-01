
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      
      <main className="flex-grow">
        {/* Hero Section */}
        <section className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800 py-16 md:py-24">
          <div className="container px-4 mx-auto">
            <div className="flex flex-col md:flex-row items-center">
              <div className="md:w-1/2 md:pr-10 mb-10 md:mb-0">
                <h1 className="text-5xl font-bold mb-6 gradient-heading md:text-3xl">
                  AI-Powered Homework Feedback
                </h1>
                <p className="text-xl text-gray-600 dark:text-gray-300 mb-8">
                  Upload your homework, get instant feedback from our AI system, and improve your academic performance.
                </p>
                <div className="flex flex-col sm:flex-row gap-4">
                  <Link to="/login">
                    <Button size="lg" className="btn-primary">
                      Get Started
                    </Button>
                  </Link>
                  <Link to="/features">
                    <Button variant="outline" size="lg" className="btn-secondary">
                      Learn More
                    </Button>
                  </Link>
                </div>
              </div>
              <div className="md:w-1/2 animate-fade-in">
                <img src="/placeholder.svg" alt="Student getting homework feedback" className="rounded-lg shadow-xl dark:opacity-80" />
              </div>
            </div>
          </div>
        </section>
        
        {/* Features Section */}
        <section className="py-16 md:py-24 bg-white dark:bg-gray-900">
          <div className="container px-4 mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4 gradient-heading">How It Works</h2>
              <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                Our AI-powered platform makes getting quality feedback on your homework assignments simple and fast.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="card dark:bg-gray-800 dark:border-gray-700">
                <div className="mb-6 bg-brand-blue-light dark:bg-brand-blue-light/30 w-14 h-14 flex items-center justify-center rounded-full">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-brand-blue dark:text-brand-blue-light">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="17 8 12 3 7 8"></polyline>
                    <line x1="12" y1="3" x2="12" y2="15"></line>
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2 dark:text-white">Upload Your Work</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Simply upload your homework in PDF, DOCX, TXT, or .ipynb format. Our system accepts all common file types.
                </p>
              </div>
              
              <div className="card dark:bg-gray-800 dark:border-gray-700">
                <div className="mb-6 bg-brand-blue-light dark:bg-brand-blue-light/30 w-14 h-14 flex items-center justify-center rounded-full">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-brand-blue dark:text-brand-blue-light">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2 dark:text-white">AI Analysis</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Our advanced AI analyzes your work, checking for accuracy, completeness, and providing constructive feedback.
                </p>
              </div>
              
              <div className="card dark:bg-gray-800 dark:border-gray-700">
                <div className="mb-6 bg-brand-blue-light dark:bg-brand-blue-light/30 w-14 h-14 flex items-center justify-center rounded-full">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-brand-blue dark:text-brand-blue-light">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                  </svg>
                </div>
                <h3 className="text-xl font-semibold mb-2 dark:text-white">Get Detailed Results</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Receive detailed feedback with suggestions for improvement, explanations of mistakes, and areas of strength.
                </p>
              </div>
            </div>
          </div>
        </section>
        
        {/* Testimonials */}
        <section className="py-16 md:py-24 bg-gray-50 dark:bg-gray-800">
          <div className="container px-4 mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4 gradient-heading">What Students Say</h2>
              <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
                Thousands of students are improving their grades with Omniwhey's AI-powered feedback.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="card dark:bg-gray-700 dark:border-gray-600">
                <div className="flex gap-2 text-amber-400 mb-4">
                  {[...Array(5)].map((_, i) => <svg key={i} xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="none">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                    </svg>)}
                </div>
                <p className="text-gray-600 dark:text-gray-200 mb-4">
                  "Omniwhey helped me understand where I was going wrong in my calculus homework. The detailed explanations were like having a tutor available 24/7."
                </p>
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-gray-300 dark:bg-gray-500 mr-3"></div>
                  <div>
                    <h4 className="font-medium dark:text-white">Jamie R.</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-300">Computer Science Student</p>
                  </div>
                </div>
              </div>
              
              <div className="card dark:bg-gray-700 dark:border-gray-600">
                <div className="flex gap-2 text-amber-400 mb-4">
                  {[...Array(5)].map((_, i) => <svg key={i} xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" stroke="none">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                    </svg>)}
                </div>
                <p className="text-gray-600 dark:text-gray-200 mb-4">
                  "I've seen a significant improvement in my essay writing skills thanks to the personalized feedback. My professor even commented on my progress!"
                </p>
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-gray-300 dark:bg-gray-500 mr-3"></div>
                  <div>
                    <h4 className="font-medium dark:text-white">Alex W.</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-300">English Literature Major</p>
                  </div>
                </div>
              </div>
              
              <div className="card dark:bg-gray-700 dark:border-gray-600">
                <div className="flex gap-2 text-amber-400 mb-4">
                  {[...Array(5)].map((_, i) => <svg key={i} xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill={i < 4 ? "currentColor" : "none"} stroke={i < 4 ? "none" : "currentColor"} strokeWidth="2">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                    </svg>)}
                </div>
                <p className="text-gray-600 dark:text-gray-200 mb-4">
                  "As a teacher, I recommend Omniwhey to all my students. It gives them instant feedback when I'm not available, and the AI catches things I might miss."
                </p>
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-gray-300 dark:bg-gray-500 mr-3"></div>
                  <div>
                    <h4 className="font-medium dark:text-white">Dr. Martinez</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-300">High School Physics Teacher</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        {/* CTA Section */}
        <section className="py-16 md:py-24 bg-gradient-to-br from-brand-purple to-brand-purple-dark text-white">
          <div className="container px-4 mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to Improve Your Grades?</h2>
            <p className="text-xl mb-8 max-w-2xl mx-auto opacity-90">
              Join thousands of students who are using Omniwhey to get better feedback and improve their academic performance.
            </p>
            <Link to="/login">
              <Button size="lg" className="bg-white text-brand-purple-dark hover:bg-gray-100 dark:bg-gray-800 dark:text-white dark:hover:bg-gray-700 hover-glow">
                Get Started for Free
              </Button>
            </Link>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
};

export default Index;
