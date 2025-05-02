import { useAuth } from "@/hooks/useAuth";

// This hook provides simplified access to user information and role-checking
export const useUserInfo = () => {
    const { user, isAuthenticated } = useAuth();

    // Check if user has admin role
    const isAdmin = () => {
        return user?.is_admin === true;
    };

    // Check if user has a specific role
    // Currently supports 'admin' and 'user'
    const hasRole = (role: string): boolean => {
        if (!user) return false;

        switch (role.toLowerCase()) {
            case 'admin':
                return user.is_admin === true;
            case 'user':
                return true; // All authenticated users have 'user' role
            default:
                return false;
        }
    };

    // Check if user has necessary permission
    // Useful for component-level access control
    const hasPermission = (permission: string): boolean => {
        if (!isAuthenticated || !user) return false;

        // This can be expanded to check against user permissions
        // when a more granular permission system is implemented
        switch (permission) {
            case 'view_admin_panel':
                return user.is_admin === true;
            case 'submit_homework':
            case 'view_submissions':
                return true; // All authenticated users can submit homework
            default:
                return false;
        }
    };

    return {
        user,
        isAuthenticated,
        isAdmin,
        hasRole,
        hasPermission,
        // Return user properties directly for convenience
        userId: user?.id,
        email: user?.email,
        fullName: user?.full_name,
    };
};

export default useUserInfo; 