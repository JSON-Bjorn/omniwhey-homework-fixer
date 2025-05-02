import { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { useUserInfo } from "@/hooks/useUserInfo";
import Navbar from "@/components/Navbar";

interface DashboardLayoutProps {
    children: ReactNode;
}

export const DashboardLayout = ({ children }: DashboardLayoutProps) => {
    const { isAdmin, user, isAuthenticated } = useUserInfo();
    const location = useLocation();

    if (!isAuthenticated) {
        return (
            <div className="flex min-h-screen flex-col">
                <Navbar />
                <div className="flex flex-1 flex-col items-center justify-center p-4">
                    <h1 className="text-2xl font-bold">You need to be logged in</h1>
                    <p className="mt-2 text-muted-foreground">Please log in to access this page.</p>
                    <Link
                        to="/login"
                        className="mt-4 rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90"
                    >
                        Log In
                    </Link>
                </div>
            </div>
        );
    }

    const navItems = [
        { href: "/dashboard", label: "Dashboard" },
        { href: "/submissions", label: "My Submissions" },
        { href: "/upload", label: "Upload Homework" },
        { href: "/templates", label: "Templates" },
    ];

    // Add admin-only nav items
    if (isAdmin()) {
        navItems.push({ href: "/admin", label: "Admin Panel" });
    }

    return (
        <div className="flex min-h-screen flex-col">
            <Navbar />

            <div className="container mx-auto flex flex-1 gap-8 px-4 py-6">
                {/* Sidebar */}
                <aside className="hidden w-64 shrink-0 lg:block">
                    <div className="sticky top-20 rounded-lg border bg-card p-4 shadow-sm">
                        <div className="mb-6 flex flex-col items-center">
                            <div className="h-20 w-20 overflow-hidden rounded-full bg-muted">
                                {/* Profile picture or initials */}
                                <div className="flex h-full w-full items-center justify-center bg-primary text-xl font-semibold text-primary-foreground">
                                    {user?.full_name
                                        ? user.full_name.split(" ").map(n => n[0]).join("").toUpperCase().substring(0, 2)
                                        : user?.email?.substring(0, 2).toUpperCase() || "U"}
                                </div>
                            </div>
                            <h3 className="mt-2 text-lg font-semibold">{user?.full_name || 'User'}</h3>
                            <p className="text-sm text-muted-foreground">{user?.email}</p>
                        </div>

                        <nav className="space-y-1">
                            {navItems.map((item) => (
                                <Link
                                    key={item.href}
                                    to={item.href}
                                    className={`block rounded-md px-3 py-2 text-sm font-medium ${location.pathname === item.href
                                            ? "bg-primary/10 text-primary"
                                            : "text-primary-foreground hover:bg-muted"
                                        }`}
                                >
                                    {item.label}
                                </Link>
                            ))}
                        </nav>
                    </div>
                </aside>

                {/* Main content */}
                <main className="flex-1">{children}</main>
            </div>
        </div>
    );
};

export default DashboardLayout; 