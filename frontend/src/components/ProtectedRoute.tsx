import { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";

interface ProtectedRouteProps {
    element: ReactNode;
    requireAdmin?: boolean;
}

export const ProtectedRoute = ({ element, requireAdmin = false }: ProtectedRouteProps) => {
    const { isAuthenticated, isLoading, user } = useAuth();

    // Show loading or redirect if still checking auth
    if (isLoading) {
        // You could return a loading spinner here
        return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
    }

    // Redirect to login if not authenticated
    if (!isAuthenticated) {
        return <Navigate to="/login" />;
    }

    // Check admin status if required
    if (requireAdmin && !user?.is_admin) {
        return <Navigate to="/dashboard" />;
    }

    // User is authenticated (and is admin if required)
    return <>{element}</>;
};

export default ProtectedRoute; 