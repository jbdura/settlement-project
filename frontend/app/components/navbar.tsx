import { useState } from 'react';
import { Link, useLocation } from 'react-router';
import { Button } from './ui/button';
import { api } from '../lib/api';
import { toast } from "sonner"


export function Navbar() {
  const location = useLocation();
  const [checking, setChecking] = useState(false);

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const checkHealth = async () => {
    setChecking(true);
    try {
      const result = await api.healthCheck();

      toast.success("✅ Health Check Passed", {
        description: result.message || "Backend API is healthy and running",
      });
    } catch (error) {
      toast.error("❌ Health Check Failed", {
        description: error instanceof Error ? error.message : "Could not connect to backend API",
      });
    } finally {
      setChecking(false);
    }
  };

  return (
    <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-6">
        <div className="flex h-16 items-center justify-between">
          {/* Logo and Brand */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="h-5 w-5"
                >
                  <path d="M20 7h-9" />
                  <path d="M14 17H5" />
                  <circle cx="17" cy="17" r="3" />
                  <circle cx="7" cy="7" r="3" />
                </svg>
              </div>
              <div>
                <h1 className="text-lg font-bold leading-none">Payment RDBMS</h1>
                <p className="text-xs text-muted-foreground">Pesapal Challenge 2026</p>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="flex items-center gap-6">
            <Link to="/">
              <Button
                variant={isActive('/') ? 'default' : 'ghost'}
                size="sm"
                className="font-medium"
              >
                Dashboard
              </Button>
            </Link>
            
            <Link to="/console">
              <Button
                variant={isActive('/console') ? 'default' : 'ghost'}
                size="sm"
                className="font-medium"
              >
                SQL Console
              </Button>
            </Link>

            {/* Health Check Button */}
            <Button
              variant="outline"
              size="sm"
              onClick={checkHealth}
              disabled={checking}
              className="gap-2"
            >
              {checking ? (
                <>
                  <span className="h-2 w-2 animate-pulse rounded-full bg-yellow-500" />
                  Checking...
                </>
              ) : (
                <>
                  <span className="h-2 w-2 rounded-full bg-green-500" />
                  Health Check
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
}
