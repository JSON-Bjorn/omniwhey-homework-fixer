import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { adminAPI } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
    Tabs,
    TabsContent,
    TabsList,
    TabsTrigger
} from '@/components/ui/tabs';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    Pagination,
    PaginationContent,
    PaginationEllipsis,
    PaginationItem,
    PaginationLink,
    PaginationNext,
    PaginationPrevious,
} from "@/components/ui/pagination";
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
    Users,
    FileText,
    CheckCircle,
    XCircle,
    Search,
    ChevronDown,
    Sliders,
    BarChart
} from 'lucide-react';

const AdminPanel: React.FC = () => {
    const [activeTab, setActiveTab] = useState('users');
    const [userPage, setUserPage] = useState(1);
    const [userSearch, setUserSearch] = useState('');
    const [submissionPage, setSubmissionPage] = useState(1);
    const [submissionStatus, setSubmissionStatus] = useState<string | undefined>(undefined);
    const [submissionUserId, setSubmissionUserId] = useState<number | undefined>(undefined);

    const { toast } = useToast();

    // Fetch users with pagination
    const {
        data: userData,
        isLoading: userLoading,
        refetch: refetchUsers
    } = useQuery({
        queryKey: ['admin', 'users', userPage, userSearch],
        queryFn: () => adminAPI.getUsers(userPage, 10, userSearch),
        select: (response) => response.data,
    });

    // Fetch submissions with pagination
    const {
        data: submissionData,
        isLoading: submissionLoading,
        refetch: refetchSubmissions
    } = useQuery({
        queryKey: ['admin', 'submissions', submissionPage, submissionStatus, submissionUserId],
        queryFn: () => adminAPI.getSubmissions(submissionPage, 10, submissionStatus, submissionUserId),
        select: (response) => response.data,
    });

    // Handle user admin toggle
    const toggleUserAdmin = async (userId: number, isAdmin: boolean) => {
        try {
            // This would need to be implemented in the api.ts file
            // For now, we'll just show a toast
            toast({
                title: `Admin status ${isAdmin ? 'granted' : 'revoked'}`,
                description: `The user's admin privileges have been ${isAdmin ? 'granted' : 'revoked'}.`,
            });
            refetchUsers();
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.response?.data?.detail || 'Failed to update user admin status',
                variant: 'destructive',
            });
        }
    };

    // Handle user active toggle
    const toggleUserActive = async (userId: number, isActive: boolean) => {
        try {
            // This would need to be implemented in the api.ts file
            // For now, we'll just show a toast
            toast({
                title: `User ${isActive ? 'activated' : 'deactivated'}`,
                description: `The user has been ${isActive ? 'activated' : 'deactivated'}.`,
            });
            refetchUsers();
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.response?.data?.detail || 'Failed to update user status',
                variant: 'destructive',
            });
        }
    };

    // Generate pagination items
    const renderPagination = (currentPage: number, totalPages: number, onPageChange: (page: number) => void) => {
        const paginationItems = [];
        const maxVisiblePages = 5;

        // Previous button
        paginationItems.push(
            <PaginationItem key="prev">
                <PaginationPrevious
                    onClick={() => onPageChange(Math.max(1, currentPage - 1))}
                    className={currentPage === 1 ? 'pointer-events-none opacity-50' : ''}
                />
            </PaginationItem>
        );

        // Page numbers
        if (totalPages <= maxVisiblePages) {
            // Show all pages if there are few
            for (let i = 1; i <= totalPages; i++) {
                paginationItems.push(
                    <PaginationItem key={i}>
                        <PaginationLink
                            onClick={() => onPageChange(i)}
                            isActive={currentPage === i}
                        >
                            {i}
                        </PaginationLink>
                    </PaginationItem>
                );
            }
        } else {
            // Show limited pages with ellipsis for many pages
            let startPage = Math.max(1, currentPage - 2);
            let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

            if (endPage - startPage < maxVisiblePages - 1) {
                startPage = Math.max(1, endPage - maxVisiblePages + 1);
            }

            // First page
            if (startPage > 1) {
                paginationItems.push(
                    <PaginationItem key={1}>
                        <PaginationLink onClick={() => onPageChange(1)}>1</PaginationLink>
                    </PaginationItem>
                );

                if (startPage > 2) {
                    paginationItems.push(
                        <PaginationItem key="ellipsis1">
                            <PaginationEllipsis />
                        </PaginationItem>
                    );
                }
            }

            // Page numbers
            for (let i = startPage; i <= endPage; i++) {
                paginationItems.push(
                    <PaginationItem key={i}>
                        <PaginationLink
                            onClick={() => onPageChange(i)}
                            isActive={currentPage === i}
                        >
                            {i}
                        </PaginationLink>
                    </PaginationItem>
                );
            }

            // Last page
            if (endPage < totalPages) {
                if (endPage < totalPages - 1) {
                    paginationItems.push(
                        <PaginationItem key="ellipsis2">
                            <PaginationEllipsis />
                        </PaginationItem>
                    );
                }

                paginationItems.push(
                    <PaginationItem key={totalPages}>
                        <PaginationLink onClick={() => onPageChange(totalPages)}>
                            {totalPages}
                        </PaginationLink>
                    </PaginationItem>
                );
            }
        }

        // Next button
        paginationItems.push(
            <PaginationItem key="next">
                <PaginationNext
                    onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
                    className={currentPage === totalPages ? 'pointer-events-none opacity-50' : ''}
                />
            </PaginationItem>
        );

        return paginationItems;
    };

    return (
        <div className="container mx-auto p-6">
            <h1 className="text-3xl font-bold mb-6">Admin Panel</h1>

            <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
                <TabsList className="mb-4">
                    <TabsTrigger value="users" className="flex items-center">
                        <Users className="h-4 w-4 mr-2" />
                        User Management
                    </TabsTrigger>
                    <TabsTrigger value="submissions" className="flex items-center">
                        <FileText className="h-4 w-4 mr-2" />
                        Submissions
                    </TabsTrigger>
                    <TabsTrigger value="stats" className="flex items-center">
                        <BarChart className="h-4 w-4 mr-2" />
                        Statistics
                    </TabsTrigger>
                </TabsList>

                {/* Users Tab */}
                <TabsContent value="users">
                    <Card>
                        <CardHeader>
                            <CardTitle>Users</CardTitle>
                            <CardDescription>
                                Manage user accounts, admin privileges, and account status.
                            </CardDescription>
                            <div className="mt-2 w-full relative">
                                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                                <Input
                                    placeholder="Search users by email..."
                                    value={userSearch}
                                    onChange={(e) => setUserSearch(e.target.value)}
                                    className="pl-9"
                                />
                            </div>
                        </CardHeader>
                        <CardContent>
                            {userLoading ? (
                                <div className="py-4 text-center">Loading users...</div>
                            ) : (
                                <div className="border rounded-md">
                                    <Table>
                                        <TableHeader>
                                            <TableRow>
                                                <TableHead>Email</TableHead>
                                                <TableHead>Joined</TableHead>
                                                <TableHead>Admin</TableHead>
                                                <TableHead>Active</TableHead>
                                                <TableHead>Actions</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {userData?.users.map((user) => (
                                                <TableRow key={user.id}>
                                                    <TableCell className="font-medium">{user.email}</TableCell>
                                                    <TableCell>
                                                        {new Date(user.created_at).toLocaleDateString()}
                                                    </TableCell>
                                                    <TableCell>
                                                        <div className="flex items-center">
                                                            <Switch
                                                                checked={user.is_admin}
                                                                onCheckedChange={(checked) => toggleUserAdmin(user.id, checked)}
                                                            />
                                                        </div>
                                                    </TableCell>
                                                    <TableCell>
                                                        <div className="flex items-center">
                                                            <Switch
                                                                checked={user.is_active}
                                                                onCheckedChange={(checked) => toggleUserActive(user.id, checked)}
                                                            />
                                                        </div>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Button variant="ghost" size="sm">
                                                            View Details
                                                        </Button>
                                                    </TableCell>
                                                </TableRow>
                                            ))}

                                            {userData?.users.length === 0 && (
                                                <TableRow>
                                                    <TableCell colSpan={5} className="text-center py-4">
                                                        No users found matching your criteria.
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                        </TableBody>
                                    </Table>
                                </div>
                            )}

                            {userData && userData.total > 0 && (
                                <div className="mt-4">
                                    <Pagination>
                                        <PaginationContent>
                                            {renderPagination(userPage, userData.total_pages, setUserPage)}
                                        </PaginationContent>
                                    </Pagination>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Submissions Tab */}
                <TabsContent value="submissions">
                    <Card>
                        <CardHeader>
                            <CardTitle>Submissions</CardTitle>
                            <CardDescription>
                                View and manage all user submissions in the system.
                            </CardDescription>
                            <div className="mt-4 flex flex-col sm:flex-row gap-4">
                                <Select
                                    value={submissionStatus || ''}
                                    onValueChange={(value) => setSubmissionStatus(value || undefined)}
                                >
                                    <SelectTrigger className="w-full sm:w-[200px]">
                                        <SelectValue placeholder="Filter by status" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="">All statuses</SelectItem>
                                        <SelectItem value="pending">Pending</SelectItem>
                                        <SelectItem value="reviewed">Reviewed</SelectItem>
                                        <SelectItem value="graded">Graded</SelectItem>
                                    </SelectContent>
                                </Select>

                                <Input
                                    type="number"
                                    placeholder="Filter by user ID"
                                    className="w-full sm:w-[200px]"
                                    onChange={(e) => {
                                        const val = e.target.value;
                                        setSubmissionUserId(val ? parseInt(val) : undefined);
                                    }}
                                />
                            </div>
                        </CardHeader>
                        <CardContent>
                            {submissionLoading ? (
                                <div className="py-4 text-center">Loading submissions...</div>
                            ) : (
                                <div className="border rounded-md">
                                    <Table>
                                        <TableHeader>
                                            <TableRow>
                                                <TableHead>Title</TableHead>
                                                <TableHead>User</TableHead>
                                                <TableHead>Status</TableHead>
                                                <TableHead>Date</TableHead>
                                                <TableHead>Actions</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {submissionData?.submissions.map((submission) => (
                                                <TableRow key={submission.id}>
                                                    <TableCell className="font-medium">{submission.title}</TableCell>
                                                    <TableCell>User #{submission.user_id}</TableCell>
                                                    <TableCell>
                                                        <Badge
                                                            className={
                                                                submission.status === 'pending' ? 'bg-yellow-600' :
                                                                    submission.status === 'reviewed' ? 'bg-blue-600' :
                                                                        'bg-green-600'
                                                            }
                                                        >
                                                            {submission.status.charAt(0).toUpperCase() + submission.status.slice(1)}
                                                        </Badge>
                                                    </TableCell>
                                                    <TableCell>
                                                        {new Date(submission.created_at).toLocaleDateString()}
                                                    </TableCell>
                                                    <TableCell>
                                                        <div className="flex space-x-2">
                                                            <Button variant="outline" size="sm">
                                                                View
                                                            </Button>
                                                            <Button variant="outline" size="sm">
                                                                Feedback
                                                            </Button>
                                                        </div>
                                                    </TableCell>
                                                </TableRow>
                                            ))}

                                            {submissionData?.submissions.length === 0 && (
                                                <TableRow>
                                                    <TableCell colSpan={5} className="text-center py-4">
                                                        No submissions found matching your criteria.
                                                    </TableCell>
                                                </TableRow>
                                            )}
                                        </TableBody>
                                    </Table>
                                </div>
                            )}

                            {submissionData && submissionData.total > 0 && (
                                <div className="mt-4">
                                    <Pagination>
                                        <PaginationContent>
                                            {renderPagination(submissionPage, submissionData.total_pages, setSubmissionPage)}
                                        </PaginationContent>
                                    </Pagination>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Statistics Tab */}
                <TabsContent value="stats">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-lg">Total Users</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold">{userData?.total || 0}</div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-lg">Total Submissions</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold">{submissionData?.total || 0}</div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-lg">Pending Reviews</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-3xl font-bold">
                                    {/* This is a placeholder - would need real API data */}
                                    {submissionData?.submissions.filter(s => s.status === 'pending').length || 0}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    <Card>
                        <CardHeader>
                            <CardTitle>System Overview</CardTitle>
                            <CardDescription>
                                Key metrics and system statistics.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <p className="text-center py-8 text-gray-500">
                                Detailed statistics charts would be displayed here.
                            </p>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
};

export default AdminPanel; 