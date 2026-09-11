import { ActivitySquare, Orbit } from "lucide-react";

import { Badge } from "@/components/ui/badge";

export function TopNavbar() {
  return (
    <header className="sticky top-0 z-20 border-b border-white/60 bg-white/70 backdrop-blur-xl">
      <div className="mx-auto flex max-w-[1800px] items-center justify-between px-5 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-950 text-white shadow-soft">
            <Orbit className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.26em] text-slate-500">
              Multi-Agent Research Assistant
            </p>
            <h1 className="text-lg font-extrabold text-slate-950 sm:text-xl">
              Analyst Workstation
            </h1>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="primary" className="px-3 py-1.5">
            <ActivitySquare className="h-3.5 w-3.5" />
            Orchestrator Mode
          </Badge>
        </div>
      </div>
    </header>
  );
}
