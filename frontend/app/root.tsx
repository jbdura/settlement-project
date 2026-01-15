import {
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
} from "react-router";

import type { Route } from "./+types/root";
import { Navbar } from "./components/navbar";
import "./app.css";
import { Toaster } from "sonner";

export function meta({ }: Route.MetaArgs) {
  return [
    { title: "Payment Settlement RDBMS - Pesapal Challenge 2026" },
    { name: "description", content: "A custom RDBMS built from scratch with payment settlement features" },
  ];
}

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function Root() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main>
        <Outlet />
      </main>
      <Toaster />
    </div>
  );
}
