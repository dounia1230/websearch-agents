import { useState } from "react";
import {
  BrainCircuit,
  ChevronDown,
  Eye,
  Map,
  Network,
  Search,
  ShieldCheck,
  SquareTerminal,
} from "lucide-react";

import type { AgentCardModel, AgentStatus } from "@/lib/mock-data";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const ICON_MAP = {
  orchestrator: Network,
  planner: Map,
  research: Search,
  critic: ShieldCheck,
  summarizer: SquareTerminal,
  vision: Eye,
  synthesizer: BrainCircuit,
} as const;

const STATUS_STYLES: Record<AgentStatus, { label: string; variant: "default" | "primary" | "success" | "destructive" }> = {
  idle: { label: "Idle", variant: "default" },
  running: { label: "Running", variant: "primary" },
  done: { label: "Done", variant: "success" },
  failed: { label: "Failed", variant: "destructive" },
};

export function AgentStatusCard({
  agent,
  initiallyExpanded = false,
}: {
  agent: AgentCardModel;
  initiallyExpanded?: boolean;
}) {
  const [expanded, setExpanded] = useState(initiallyExpanded);
  const Icon = ICON_MAP[agent.iconKey];
  const statusStyle = STATUS_STYLES[agent.status];

  return (
    <Card
      className={cn(
        "transition-all duration-300",
        agent.status === "running" && "ring-2 ring-blue-100 shadow-soft",
      )}
    >
      <button
        type="button"
        onClick={() => setExpanded((value) => !value)}
        className="w-full text-left"
      >
        <CardHeader className="gap-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex min-w-0 items-start gap-3">
              <div
                className={cn(
                  "flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl",
                  agent.status === "done" && "bg-emerald-50 text-emerald-700",
                  agent.status === "running" && "bg-blue-50 text-blue-700",
                  agent.status === "idle" && "bg-slate-100 text-slate-700",
                  agent.status === "failed" && "bg-rose-50 text-rose-700",
                )}
              >
                <Icon className="h-5 w-5" />
              </div>
              <div className="min-w-0">
                <CardTitle className="text-base">{agent.name}</CardTitle>
                <p className="mt-1 text-sm leading-6 text-slate-500">{agent.description}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={statusStyle.variant}>{statusStyle.label}</Badge>
              <ChevronDown
                className={cn(
                  "h-4 w-4 shrink-0 text-slate-400 transition-transform",
                  expanded && "rotate-180",
                )}
              />
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline" className="bg-white/70">
              {agent.metric}
            </Badge>
            <p className="text-sm text-slate-600">{agent.preview}</p>
          </div>
        </CardHeader>
      </button>
      {expanded ? (
        <CardContent className="pt-0">
          <div className="rounded-2xl bg-slate-50/90 p-4">
            <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-500">
              Output Preview
            </p>
            <ul className="space-y-2">
              {agent.details.map((detail) => (
                <li key={detail} className="flex items-start gap-2 text-sm leading-6 text-slate-600">
                  <span className="mt-2 h-1.5 w-1.5 rounded-full bg-blue-500" />
                  <span>{detail}</span>
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      ) : null}
    </Card>
  );
}
