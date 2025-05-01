
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet";

const Navbar = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  
  // This would be replaced with actual auth logic
  const handleLogout = () => {
    setIsLoggedIn(false);
  };
  
  return (
    <nav className="w-full py-4 border-b border-gray-100 bg-white/80 backdrop-blur-md sticky top-0 z-50">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-md bg-gradient-to-br from-brand-purple-dark to-brand-purple-light flex items-center justify-center text-white font-bold text-lg">O</div>
          <span className="text-xl font-bold">Omniwhey</span>
        </Link>
        
        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-8">
          <Link to="/" className="text-gray-700 hover:text-brand-purple transition-colors">Home</Link>
          <Link to="/features" className="text-gray-700 hover:text-brand-purple transition-colors">Features</Link>
          {isLoggedIn ? (
            <>
              <Link to="/dashboard" className="text-gray-700 hover:text-brand-purple transition-colors">Dashboard</Link>
              <Button variant="outline" onClick={handleLogout}>Logout</Button>
            </>
          ) : (
            <>
              <Link to="/login">
                <Button variant="outline">Log in</Button>
              </Link>
              <Link to="/login?signup=true">
                <Button>Sign up</Button>
              </Link>
            </>
          )}
        </div>
        
        {/* Mobile Navigation */}
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="outline" size="icon" className="md:hidden">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="3" y1="12" x2="21" y2="12"></line>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <line x1="3" y1="18" x2="21" y2="18"></line>
              </svg>
            </Button>
          </SheetTrigger>
          <SheetContent>
            <div className="flex flex-col gap-6 pt-10">
              <Link to="/" className="text-lg font-medium">Home</Link>
              <Link to="/features" className="text-lg font-medium">Features</Link>
              {isLoggedIn ? (
                <>
                  <Link to="/dashboard" className="text-lg font-medium">Dashboard</Link>
                  <Button onClick={handleLogout}>Logout</Button>
                </>
              ) : (
                <>
                  <Link to="/login">
                    <Button variant="outline" className="w-full">Log in</Button>
                  </Link>
                  <Link to="/login?signup=true">
                    <Button className="w-full">Sign up</Button>
                  </Link>
                </>
              )}
            </div>
          </SheetContent>
        </Sheet>
      </div>
    </nav>
  );
};

export default Navbar;
