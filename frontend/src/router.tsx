import { createBrowserRouter, Navigate } from 'react-router-dom';

import MainLayout from '@/components/MainLayout';
import ProtectedRoute from '@/components/ProtectedRoute';
import LoginPage from '@/pages/LoginPage';
import ProjectCreatePage from '@/pages/ProjectCreatePage';
import ProjectDetailPage from '@/pages/ProjectDetailPage';
import ProjectEditPage from '@/pages/ProjectEditPage';
import ProjectsListPage from '@/pages/ProjectsListPage';
import RegisterPage from '@/pages/RegisterPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      // Public routes
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> },

      // Protected routes
      {
        element: <ProtectedRoute />,
        children: [
          { index: true, element: <Navigate to="/projects" replace /> },

          { path: 'projects', element: <ProjectsListPage /> },
          { path: 'projects/new', element: <ProjectCreatePage /> },
          { path: 'projects/:id', element: <ProjectDetailPage /> },
          { path: 'projects/:id/edit', element: <ProjectEditPage /> },
        ],
      },
    ],
  },
]);