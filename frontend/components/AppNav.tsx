"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/profile", label: "Profile" },
  { href: "/documents", label: "Documents" },
  { href: "/discovery", label: "Discovery" },
  { href: "/results", label: "Results" },
];

export function AppNav() {
  const pathname = usePathname();
  return (
    <header className="nav">
      <Link className="nav-brand" href="/">
        FinSarthi
      </Link>
      <nav className="nav-links">
        {LINKS.filter((item) => item.href !== "/").map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={pathname === item.href ? "nav-link active" : "nav-link"}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
