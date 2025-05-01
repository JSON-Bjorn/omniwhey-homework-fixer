
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";

// Mock data for the dashboard
const recentSubmissions = [
  {
    id: 1,
    title: 'Math Homework 3',
    subject: 'Mathematics',
    date: '2025-04-30',
    score: 92,
    status: 'graded'
  },
  {
    id: 2,
    title: 'Physics Lab Report',
    subject: 'Physics',
    date: '2025-04-28',
    score: 88,
    status: 'graded'
  },
  {
    id: 3,
    title: 'Essay on Modern Literature',
    subject: 'English',
    date: '2025-04-26',
    score: 95,
    status: 'graded'
  },
  {
    id: 4,
    title: 'Computer Science Project',
    subject: 'CS',
    date: '2025-05-01',
    status: 'processing'
  }
];

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('recent');
  
  const getScoreClass = (score: number) => {
    if (score >= 90) return 'bg-green-100 text-green-800';
    if (score >= 75) return 'bg-blue-100 text-blue-800';
    return 'bg-amber-100 text-amber-800';
  };
  
  return (
    <div className="w-full">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-semibold">My Dashboard</h1>
          <p className="text-gray-500">View and manage your homework assignments</p>
        </div>
        <Link to="/upload">
          <Button>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="mr-2"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
            Submit New Homework
          </Button>
        </Link>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Total Submissions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold">12</span>
              <span className="text-green-600 text-sm">+2 this week</span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Average Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold">89%</span>
              <span className="text-green-600 text-sm">+3% from last month</span>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Pending Reviews</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold">1</span>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <Tabs defaultValue="recent" className="w-full" onValueChange={setActiveTab}>
        <TabsList className="mb-6">
          <TabsTrigger value="recent">Recent Submissions</TabsTrigger>
          <TabsTrigger value="all">All Submissions</TabsTrigger>
          <TabsTrigger value="bookmarks">Bookmarked</TabsTrigger>
        </TabsList>
        
        <TabsContent value="recent">
          <Card>
            <CardHeader>
              <CardTitle>Recent Submissions</CardTitle>
              <CardDescription>Your most recent homework submissions and their status.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-gray-500 uppercase bg-gray-50">
                    <tr>
                      <th className="px-6 py-3">Title</th>
                      <th className="px-6 py-3">Subject</th>
                      <th className="px-6 py-3">Date</th>
                      <th className="px-6 py-3">Score</th>
                      <th className="px-6 py-3">Status</th>
                      <th className="px-6 py-3">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentSubmissions.map((submission) => (
                      <tr key={submission.id} className="bg-white border-b hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium text-gray-900">
                          {submission.title}
                        </td>
                        <td className="px-6 py-4">{submission.subject}</td>
                        <td className="px-6 py-4">{submission.date}</td>
                        <td className="px-6 py-4">
                          {submission.status === 'graded' ? (
                            <span className={`text-sm font-medium px-2.5 py-1 rounded ${getScoreClass(submission.score!)}`}>
                              {submission.score}%
                            </span>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <span 
                            className={`text-xs font-medium px-2.5 py-1 rounded ${
                              submission.status === 'graded'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-amber-100 text-amber-800'
                            }`}
                          >
                            {submission.status === 'graded' ? 'Graded' : 'Processing'}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <Link 
                            to={`/results/${submission.id}`} 
                            className="text-brand-purple hover:underline"
                          >
                            View
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="all">
          <Card>
            <CardHeader>
              <CardTitle>All Submissions</CardTitle>
              <CardDescription>Complete history of your homework submissions.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <p>All your submitted homework will be displayed here.</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="bookmarks">
          <Card>
            <CardHeader>
              <CardTitle>Bookmarked Submissions</CardTitle>
              <CardDescription>Homework submissions you've bookmarked for quick access.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <p>You haven't bookmarked any submissions yet.</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Dashboard;
