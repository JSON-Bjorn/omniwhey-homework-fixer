import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
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
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue
} from '@/components/ui/select';
import { FileText, Eye, Trash2, Download } from 'lucide-react';
import { submissionsAPI } from '@/lib/api';
import { Submission } from '@/lib/types';
import { useToast } from '@/components/ui/use-toast';

const Submissions: React.FC = () => {
    const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
    const [searchQuery, setSearchQuery] = useState('');
    const { toast } = useToast();

    const { data, isLoading, isError, refetch } = useQuery({
        queryKey: ['submissions', statusFilter],
        queryFn: () => submissionsAPI.getSubmissions(statusFilter),
        select: (response) => response.data as Submission[],
    });

    const handleDelete = async (id: number) => {
        if (window.confirm('Are you sure you want to delete this submission?')) {
            try {
                await submissionsAPI.deleteSubmission(id);
                toast({
                    title: 'Submission deleted',
                    description: 'The submission has been deleted successfully',
                });
                refetch();
            } catch (error: any) {
                toast({
                    title: 'Error',
                    description: error.response?.data?.detail || 'Failed to delete submission',
                    variant: 'destructive',
                });
            }
        }
    };

    const handleDownload = async (id: number, title: string) => {
        try {
            const response = await submissionsAPI.downloadSubmission(id);
            const blob = new Blob([response.data]);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `submission-${title.replace(/\s+/g, '-')}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error: any) {
            toast({
                title: 'Error',
                description: error.response?.data?.detail || 'Failed to download submission',
                variant: 'destructive',
            });
        }
    };

    // Filter submissions based on search query
    const filteredSubmissions = data?.filter(submission =>
        submission.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        submission.description?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="container mx-auto p-6">
            <h1 className="text-3xl font-bold mb-6">My Submissions</h1>

            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                <div className="flex-1 w-full md:w-auto">
                    <Input
                        placeholder="Search submissions..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full"
                    />
                </div>

                <div className="flex gap-4 w-full md:w-auto">
                    <Select value={statusFilter || ''} onValueChange={(value) => setStatusFilter(value || undefined)}>
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Filter by status" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="">All statuses</SelectItem>
                            <SelectItem value="pending">Pending</SelectItem>
                            <SelectItem value="reviewed">Reviewed</SelectItem>
                            <SelectItem value="graded">Graded</SelectItem>
                        </SelectContent>
                    </Select>

                    <Button asChild>
                        <Link to="/upload">Upload New</Link>
                    </Button>
                </div>
            </div>

            {isLoading && <p className="text-center py-8">Loading submissions...</p>}

            {isError && (
                <div className="bg-red-100 dark:bg-red-900/20 border-l-4 border-red-500 text-red-700 dark:text-red-300 p-4 rounded mb-6">
                    <p>Failed to load submissions. Please try again later.</p>
                </div>
            )}

            {!isLoading && filteredSubmissions?.length === 0 && (
                <div className="text-center py-12">
                    <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                    <h3 className="text-xl font-medium mb-2">No submissions found</h3>
                    <p className="text-gray-500 dark:text-gray-400 mb-6">
                        {searchQuery
                            ? "No submissions match your search criteria."
                            : "You haven't uploaded any submissions yet."}
                    </p>
                    <Button asChild>
                        <Link to="/upload">Upload Your First Submission</Link>
                    </Button>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredSubmissions?.map((submission) => (
                    <Card key={submission.id} className="flex flex-col">
                        <CardHeader>
                            <div className="flex justify-between items-start">
                                <div>
                                    <CardTitle className="truncate">{submission.title}</CardTitle>
                                    <CardDescription>
                                        Submitted on {format(new Date(submission.created_at), 'MMM d, yyyy')}
                                    </CardDescription>
                                </div>
                                <div className={`
                  px-2 py-1 rounded-full text-xs font-medium 
                  ${submission.status === 'pending' && 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'}
                  ${submission.status === 'reviewed' && 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'}
                  ${submission.status === 'graded' && 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'}
                `}>
                                    {submission.status.charAt(0).toUpperCase() + submission.status.slice(1)}
                                </div>
                            </div>
                        </CardHeader>

                        <CardContent className="flex-grow">
                            <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-3">
                                {submission.description || 'No description provided.'}
                            </p>
                        </CardContent>

                        <CardFooter className="flex justify-between border-t pt-4">
                            <Button variant="outline" size="sm" asChild>
                                <Link to={`/submissions/${submission.id}`}>
                                    <Eye className="h-4 w-4 mr-2" />
                                    View
                                </Link>
                            </Button>

                            <div className="flex gap-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => handleDownload(submission.id, submission.title)}
                                >
                                    <Download className="h-4 w-4 mr-2" />
                                    Download
                                </Button>

                                <Button
                                    variant="outline"
                                    size="sm"
                                    className="text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/20"
                                    onClick={() => handleDelete(submission.id)}
                                >
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                            </div>
                        </CardFooter>
                    </Card>
                ))}
            </div>
        </div>
    );
};

export default Submissions; 