
import { useEffect } from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import DashboardComponent from '@/components/Dashboard';

const DashboardPage = () => {
  useEffect(() => {
    // Set page title
    document.title = 'Dashboard | Omniwhey';
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      
      <main className="flex-grow bg-gray-50 py-8">
        <div className="container px-4 mx-auto">
          <DashboardComponent />
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default DashboardPage;
