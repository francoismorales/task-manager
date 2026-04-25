import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

export default function MainLayout() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/login', { replace: true });
  }

  return (
    <div className="min-h-full flex flex-col">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to="/" className="font-semibold text-brand-600 text-lg">
              Task Manager
            </Link>

            {isAuthenticated && (
              <nav className="flex items-center gap-4 text-sm">
                <NavLink
                  to="/projects"
                  className={({ isActive }) =>
                    'transition ' +
                    (isActive
                      ? 'text-slate-900 font-medium'
                      : 'text-slate-600 hover:text-slate-900')
                  }
                >
                  Proyectos
                </NavLink>
              </nav>
            )}
          </div>

          <nav className="flex items-center gap-4 text-sm">
            {isAuthenticated ? (
              <>
                <span className="text-slate-600 hidden sm:inline">
                  {user?.full_name}
                </span>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="rounded-md border border-slate-300 px-3 py-1.5 text-slate-700 hover:bg-slate-100 transition"
                >
                  Cerrar sesión
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-slate-700 hover:text-slate-900">
                  Iniciar sesión
                </Link>
                <Link
                  to="/register"
                  className="rounded-md bg-brand-600 text-white px-3 py-1.5 hover:bg-brand-700 transition"
                >
                  Crear cuenta
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-8">
        <Outlet />
      </main>

      <footer className="border-t border-slate-200 py-4 text-center text-xs text-slate-500">
        Task Manager · Prueba técnica
      </footer>
    </div>
  );
}