import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardDescription,
    CardFooter
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Badge } from '@/components/ui/badge';
import { submissionsAPI, feedbackAPI } from '@/lib/api';
import { Submission, Feedback } from '@/lib/types';
import { useToast } from '@/components/ui/use-toast';
import {
    FileText,
    ArrowLeft,
    Download,
    Clock,
    CheckCircle,
    MessageSquare,
    Award
} from 'lucide-react';

const SubmissionDetail: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const submissionId = parseInt(id || '0');
    const navigate = useNavigate();
    const { toast } = useToast();

    const { data: submission, isLoading: submissionLoading, isError: submissionError } = useQuery({
        queryKey: ['submission', submissionId],
        queryFn: () => submissionsAPI.getSubmission(submissionId),
        select: (response) => response.data as Submission,
        enabled: !!submissionId,
    });

    const { data: feedback, isLoading: feedbackLoading } = useQuery({
        queryKey: ['feedback', submissionId],
        queryFn: () => feedbackAPI.getSubmissionFeedback(submissionId),
        select: (response) => response.data as Feedback[],
        enabled: !!submissionId,
    });

    const handleDownload = async () => {
        if (!submission) return;

        try {
            const response = await submissionsAPI.downloadSubmission(submission.id);
            const blob = new Blob([response.data]);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `submission-${submission.title.replace(/\s+/g, '-')}.pdf`;
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

    if (submissionLoading) {
        return <div className="container mx-auto p-6 text-center">Loading submission details...</div>;
    }

    if (submissionError || !submission) {
        return (
            <div className="container mx-auto p-6">
                <div className="bg-red-100 dark:bg-red-900/20 border-l-4 border-red-500 text-red-700 dark:text-red-300 p-4 rounded mb-6">
                    <p>Failed to load submission details. The submission may have been deleted or you don't have permission to view it.</p>
                </div>
                <Button onClick={() => navigate('/submissions')}>
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back to Submissions
                </Button>
            </div>
        );
    }

    return (
        <div className="container mx-auto p-6">
            <Breadcrumb className="mb-6">
                <BreadcrumbList>
                    <BreadcrumbItem>
                        <BreadcrumbLink as={Link} to="/dashboard">Dashboard</BreadcrumbLink>
                    </BreadcrumbItem>
                    <BreadcrumbSeparator />
                    <BreadcrumbItem>
                        <BreadcrumbLink as={Link} to="/submissions">Submissions</BreadcrumbLink>
                    </BreadcrumbItem>
                    <BreadcrumbSeparator />
                    <BreadcrumbItem>
                        <BreadcrumbLink>{submission.title}</BreadcrumbLink>
                    </BreadcrumbItem>
                </BreadcrumbList>
            </Breadcrumb>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Submission details */}
                <div className="lg:col-span-2">
                    <Card>
                        <CardHeader className="flex flex-row items-start justify-between">
                            <div>
                                <CardTitle className="text-2xl">{submission.title}</CardTitle>
                                <CardDescription>
                                    Submitted on {format(new Date(submission.created_at), 'MMMM d, yyyy')} at {format(new Date(submission.created_at), 'h:mm a')}
                                </CardDescription>
                            </div>
                            <Badge
                                className={
                                    submission.status === 'pending' ? 'bg-yellow-600' :
                                        submission.status === 'reviewed' ? 'bg-blue-600' :
                                            'bg-green-600'
                                }
                            >
                                {submission.status.charAt(0).toUpperCase() + submission.status.slice(1)}
                            </Badge>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <h3 className="text-lg font-medium mb-2">Description</h3>
                                <p className="text-gray-500 dark:text-gray-400">
                                    {submission.description || 'No description provided.'}
                                </p>
                            </div>

                            <div className="border rounded-lg p-4 bg-gray-50 dark:bg-gray-900/50 flex items-center justify-between">
                                <div className="flex items-center">
                                    <FileText className="h-8 w-8 text-blue-500 mr-3" />
                                    <div>
                                        <p className="font-medium">Submission File</p>
                                        <p className="text-sm text-gray-500">
                                            {submission.file_path.split('/').pop()}
                                        </p>
                                    </div>
                                </div>
                                <Button onClick={handleDownload}>
                                    <Download className="h-4 w-4 mr-2" />
                                    Download
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Feedback section */}
                    <div className="mt-6">
                        <h2 className="text-xl font-bold mb-4 flex items-center">
                            <MessageSquare className="h-5 w-5 mr-2" />
                            Feedback & Evaluation
                        </h2>

                        {feedbackLoading ? (
                            <p>Loading feedback...</p>
                        ) : feedback && feedback.length > 0 ? (
                            <div className="space-y-4">
                                {feedback.map((item, index) => (
                                    <Card key={item.id}>
                                        <CardHeader>
                                            <CardTitle className="text-lg flex items-center">
                                                <span className="mr-2">Feedback #{index + 1}</span>
                                                {item.grade && (
                                                    <Badge className="ml-auto bg-blue-600">
                                                        <Award className="h-3 w-3 mr-1" />
                                                        Grade: {item.grade}
                                                    </Badge>
                                                )}
                                            </CardTitle>
                                            <CardDescription>
                                                Provided on {format(new Date(item.created_at), 'MMMM d, yyyy')}
                                            </CardDescription>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="prose dark:prose-invert max-w-none">
                                                {item.content}
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center border border-dashed rounded-lg p-8 bg-gray-50 dark:bg-gray-900/50">
                                <Clock className="h-12 w-12 mx-auto text-gray-400 mb-3" />
                                <h3 className="text-lg font-medium mb-2">Awaiting Feedback</h3>
                                <p className="text-gray-500 dark:text-gray-400">
                                    Your submission is currently under review. <br />
                                    Feedback will appear here once it's available.
                                </p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Status sidebar */}
                <div>
                    <Card>
                        <CardHeader>
                            <CardTitle>Submission Status</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-start space-x-3">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${submission.status !== 'pending' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'
                                    }`}>
                                    {submission.status !== 'pending' ? (
                                        <CheckCircle className="h-5 w-5" />
                                    ) : (
                                        <span>1</span>
                                    )}
                                </div>
                                <div>
                                    <p className="font-medium">Submitted</p>
                                    <p className="text-sm text-gray-500">
                                        {format(new Date(submission.created_at), 'MMM d, yyyy')}
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-start space-x-3">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${submission.status === 'reviewed' || submission.status === 'graded'
                                        ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                        : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'
                                    }`}>
                                    {submission.status === 'reviewed' || submission.status === 'graded' ? (
                                        <CheckCircle className="h-5 w-5" />
                                    ) : (
                                        <span>2</span>
                                    )}
                                </div>
                                <div>
                                    <p className="font-medium">Reviewed</p>
                                    <p className="text-sm text-gray-500">
                                        {submission.status === 'reviewed' || submission.status === 'graded'
                                            ? 'Your submission has been reviewed'
                                            : 'Your submission is pending review'}
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-start space-x-3">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${submission.status === 'graded'
                                        ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                        : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'
                                    }`}>
                                    {submission.status === 'graded' ? (
                                        <CheckCircle className="h-5 w-5" />
                                    ) : (
                                        <span>3</span>
                                    )}
                                </div>
                                <div>
                                    <p className="font-medium">Graded</p>
                                    <p className="text-sm text-gray-500">
                                        {submission.status === 'graded'
                                            ? 'Your submission has been graded'
                                            : 'Awaiting final grade'}
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                        <CardFooter>
                            <Button variant="outline" className="w-full" asChild>
                                <Link to="/submissions">
                                    <ArrowLeft className="h-4 w-4 mr-2" />
                                    Back to Submissions
                                </Link>
                            </Button>
                        </CardFooter>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default SubmissionDetail; 