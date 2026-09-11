import { Clock3, Cpu, Network, Route, Sparkles } from "lucide-react";

import { AgentStatusCard } from "@/components/agent-status-card";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { AgentCardModel, AgentStatus } from "@/lib/mock-data";

interface WorkflowPanelProps {
  agents: AgentCardModel[];
  query: string;
  sourceCount: number;
  includeVision: boolean;
  imageName: string | null;
  isRunning: boolean;
  hasRun: boolean;
}

export function WorkflowPanel({
  agents,
  query,
  sourceCount,
  includeVision,
  imageName,
  isRunning,
  hasRun,
}: WorkflowPanelProps) {
  const completedAgents = agents.filter((agent) => agent.status === "done").length;
  const runnableAgents = agents.filter((agent) => agent.enabled || agent.id !== "vision").length;
  const progress = runnableAgents === 0 ? 0 : Math.round((completedAgents / runnableAgents) * 100);
  const orchestratorStatus: AgentStatus = isRunning ? "running" : hasRun ? "done" : "idle";

  return (
    <div className="space-y-5">
      <Card>
        <CardHeader className="pb-5">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-950 text-white">
                <Network className="h-5 w-5" />
              </div>
              <div>
                <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">
                  Orchestrator Workflow
                </p>
                <CardTitle className="mt-1 text-xl">Pipeline Visibility</CardTitle>
                <p className="mt-2 max-w-xl text-sm leading-6 text-slate-500">
                  The orchestrator coordinates research, critique, summarization, optional vision,
                  and synthesis into a structured final report.
                </p>
              </div>
            </div>
            <Badge variant={orchestratorStatus === "done" ? "success" : orchestratorStatus === "running" ? "primary" : "outline"}>
              {orchestratorStatus === "done" ? "Run Completed" : orchestratorStatus === "running" ? "Run Active" : "Ready"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <MetricTile label="Research Query" value={query.trim() ? "Loaded" : "Missing"} icon={Route} />
            <MetricTile label="Source Target" value={`${sourceCount} sources`} icon={Cpu} />
            <MetricTile
              label="Vision Path"
              value={includeVision && imageName ? "Enabled" : "Standby"}
              icon={Sparkles}
            />
            <MetricTile label="Pipeline Progress" value={`${progress}%`} icon={Clock3} />
          </div>
          <div>
            <div className="mb-2 flex items-center justify-between text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
              <span>Execution Flow</span>
              <span>{completedAgents}/{runnableAgents} complete</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-400 transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="relative space-y-4 pl-6">
        <div className="agent-connector absolute bottom-8 left-[14px] top-4 w-px rounded-full" />
        {agents.map((agent, index) => (
          <div key={agent.id} className="relative">
            <span className="absolute -left-[18px] top-8 h-3 w-3 rounded-full border-4 border-background bg-blue-500 shadow-soft" />
            <AgentStatusCard agent={agent} initiallyExpanded={index === 0 || agent.status === "running"} />
          </div>
        ))}
      </div>
    </div>
  );
}

function MetricTile({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: string;
  icon: typeof Network;
}) {
  return (
    <div className="rounded-2xl bg-slate-50/90 p-4">
      <div className="flex items-center gap-2 text-slate-500">
        <Icon className="h-4 w-4" />
        <span className="text-[11px] font-semibold uppercase tracking-[0.18em]">{label}</span>
      </div>
      <p className="mt-2 text-base font-semibold text-slate-900">{value}</p>
    </div>
  );
}
