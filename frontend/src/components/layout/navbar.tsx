import { useState } from "react"
import { NavLink } from "react-router-dom"
import { Bell, Command, Menu, Moon, Search, Sun, X } from "lucide-react"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { Logo } from "@/components/layout/logo"
import { NAV_ITEMS } from "@/constants"
import { useApp } from "@/contexts/app-context"
import { useTheme } from "@/contexts/theme-context"
import { cn } from "@/lib/utils"

/**
 * Top navigation bar. Left: brand. Center: global command/search (Phase 2:
 * repository search, run lookup). Right: environment badge, notifications,
 * theme toggle, user avatar.
 */
export function Navbar() {
  const { environment } = useApp()
  const { theme, toggleTheme } = useTheme()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  return (
    <header className="sticky top-0 z-40 flex h-14 items-center gap-4 border-b border-border bg-background/85 px-4 backdrop-blur-md lg:px-6">
      <Button
        variant="ghost"
        size="icon"
        className="md:hidden"
        onClick={() => setMobileNavOpen((open) => !open)}
        aria-label={mobileNavOpen ? "Close navigation" : "Open navigation"}
        aria-expanded={mobileNavOpen}
      >
        {mobileNavOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
      </Button>

      {/* Mobile navigation drawer */}
      {mobileNavOpen && (
        <nav
          className="absolute inset-x-0 top-14 z-50 border-b border-border bg-card p-3 shadow-lg md:hidden"
          aria-label="Mobile navigation"
        >
          <ul className="flex flex-col gap-0.5">
            {NAV_ITEMS.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  end={item.path === "/"}
                  onClick={() => setMobileNavOpen(false)}
                  className={({ isActive }) =>
                    cn(
                      "block rounded-md px-3 py-2 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-accent text-accent-foreground"
                        : "text-muted-foreground hover:bg-muted/60 hover:text-foreground",
                    )
                  }
                >
                  {item.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      )}

      <Logo />

      {/* Global search placeholder — wired to real search in Phase 2 */}
      <div className="hidden max-w-md flex-1 md:block">
        <button
          type="button"
          className="flex w-full items-center gap-2 rounded-md border border-border bg-muted/50 px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:border-ring/60 hover:text-foreground"
          aria-label="Search (placeholder)"
        >
          <Search className="h-3.5 w-3.5" />
          <span className="flex-1 text-left">Search repositories, runs, findings…</span>
          <kbd className="hidden items-center gap-0.5 rounded border border-border bg-card px-1.5 font-mono text-[10px] lg:flex">
            <Command className="h-2.5 w-2.5" />K
          </kbd>
        </button>
      </div>

      <div className="ml-auto flex items-center gap-1.5">
        <span className="mr-1 hidden rounded-full border border-border bg-muted/60 px-2.5 py-1 font-mono text-[10px] uppercase tracking-widest text-muted-foreground sm:inline-flex">
          {environment}
        </span>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="ghost" size="icon" aria-label="Notifications (placeholder)">
              <Bell className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent>Notifications — coming online with live events</TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
            >
              {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
          </TooltipTrigger>
          <TooltipContent>{theme === "dark" ? "Light theme" : "Dark theme"}</TooltipContent>
        </Tooltip>

        <Avatar className="ml-1 h-8 w-8">
          <AvatarFallback className="text-[10px] font-semibold">OP</AvatarFallback>
        </Avatar>
      </div>
    </header>
  )
}
