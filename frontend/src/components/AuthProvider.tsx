import { ReactNode } from "react";
import { AuthProvider as ContextAuthProvider } from "@/hooks/useAuth";

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
    return <ContextAuthProvider>{children}</ContextAuthProvider>;
};

export default AuthProvider; 