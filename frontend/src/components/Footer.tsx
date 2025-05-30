
import { Link } from 'react-router-dom';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-gray-50 dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800 py-12 mt-20">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-md bg-gradient-to-br from-brand-purple-dark to-brand-purple-light flex items-center justify-center text-white font-bold text-lg">O</div>
              <span className="text-xl font-bold">Omniwhey</span>
            </div>
            <p className="text-gray-500 dark:text-gray-400 text-sm max-w-xs">
              AI-powered homework feedback and grading platform for students and educators.
            </p>
          </div>
          
          <div className="col-span-1">
            <h4 className="font-semibold mb-4 dark:text-gray-200">Product</h4>
            <ul className="space-y-2">
              <li><Link to="/features" className="text-gray-500 hover:text-brand-purple dark:text-gray-400 dark:hover:text-brand-purple-light text-sm">Features</Link></li>
              <li><Link to="/pricing" className="text-gray-500 hover:text-brand-purple dark:text-gray-400 dark:hover:text-brand-purple-light text-sm">Pricing</Link></li>
              <li><Link to="/for-teachers" className="text-gray-500 hover:text-brand-purple dark:text-gray-400 dark:hover:text-brand-purple-light text-sm">For Teachers</Link></li>
              <li><Link to="/for-students" className="text-gray-500 hover:text-brand-purple dark:text-gray-400 dark:hover:text-brand-purple-light text-sm">For Students</Link></li>
            </ul>
          </div>
          
          <div className="col-span-1">
            <h4 className="font-semibold mb-4 dark:text-gray-200">Resources</h4>
            <ul className="space-y-2">
              <li><Link to="/help" className="text-gray-500 hover:text-brand-purple dark:text-gray-400 dark:hover:text-brand-purple-light text-sm">Help Center</Link></li>
              <li><Link to="/blog" className="text-gray-500 hover:text-brand-purple dark:text-gray-400 dark:hover:text-brand-purple-light text-sm">Blog</Link></li>
              <li><Link to="/ai-ethics" className="text-gray-500 hover:text-brand-purple dark:text-gray-400 dark:hover:text-brand-purple-light text-sm">AI Ethics</Link></li>
              <li><Link to="/support" className="text-gray-500 hover:text-brand-purple dark:text-gray-400 dark:hover:text-brand-purple-light text-sm">Support</Link></li>
            </ul>
          </div>
          
          <div className="col-span-1">
            <h4 className="font-semibold mb-4 dark:text-gray-200">Company</h4>
            <ul className="space-y-2">
              <li><Link to="/about" className="text-gray-500 hover:text-brand-purple dark:text-gray-400 dark:hover:text-brand-purple-light text-sm">About Us</Link></li>
              <li><Link to="/careers" className="text-gray-500 hover:text-brand-purple dark:text-gray-400 dark:hover:text-brand-purple-light text-sm">Careers</Link></li>
              <li><Link to="/privacy" className="text-gray-500 hover:text-brand-purple dark:text-gray-400 dark:hover:text-brand-purple-light text-sm">Privacy Policy</Link></li>
              <li><Link to="/terms" className="text-gray-500 hover:text-brand-purple dark:text-gray-400 dark:hover:text-brand-purple-light text-sm">Terms of Service</Link></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-200 dark:border-gray-800 mt-12 pt-6 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-500 dark:text-gray-400 text-sm">© {currentYear} Omniwhey, Inc. All rights reserved.</p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-brand-purple dark:hover:text-brand-purple-light">
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84"></path>
              </svg>
            </a>
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-brand-purple dark:hover:text-brand-purple-light">
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd"></path>
              </svg>
            </a>
            <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-brand-purple dark:hover:text-brand-purple-light">
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"></path>
              </svg>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
