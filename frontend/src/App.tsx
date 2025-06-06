import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@/components/ThemeProvider";
import { AuthProvider } from "@/components/AuthProvider";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import NotFound from "./pages/NotFound";
import Submissions from "./pages/Submissions";
import Templates from "./pages/Templates";
import SubmissionDetail from "./pages/SubmissionDetail";
import AdminPanel from "./pages/AdminPanel";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider defaultTheme="dark">
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <AuthProvider>
            <Routes>
              <Route path="/" element={<Index />} />
              <Route path="/login" element={<Login />} />
              <Route path="/dashboard" element={<ProtectedRoute element={<Dashboard />} />} />
              <Route path="/upload" element={<ProtectedRoute element={<Upload />} />} />
              <Route path="/submissions" element={<ProtectedRoute element={<Submissions />} />} />
              <Route path="/submissions/:id" element={<ProtectedRoute element={<SubmissionDetail />} />} />
              <Route path="/templates" element={<ProtectedRoute element={<Templates />} />} />
              <Route path="/admin" element={<ProtectedRoute element={<AdminPanel />} requireAdmin={true} />} />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </AuthProvider>
        </BrowserRouter>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
