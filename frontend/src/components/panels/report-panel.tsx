import {
  BarChart3,
  BriefcaseBusiness,
  Compass,
  ExternalLink,
  FileSearch,
  ShieldAlert,
  Sparkle,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { ReportSectionCard } from "@/components/report-section-card";
import type { FinalReportModel } from "@/lib/mock-data";

interface ReportPanelProps {
  report: FinalReportModel | null;
  isRunning: boolean;
  errorMessage?: string | null;
}

export function ReportPanel({ report, isRunning, errorMessage }: ReportPanelProps) {
  if (isRunning) {
    return (
      <div className="space-y-5">
        <LoadingCard />
        <LoadingCard />
        <LoadingCard />
      </div>
    );
  }

  if (errorMessage) {
    return (
      <Card className="flex min-h-[420px] items-center justify-center">
        <CardContent className="flex max-w-md flex-col items-center justify-center py-16 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-rose-50 text-rose-700">
            <ShieldAlert className="h-7 w-7" />
          </div>
          <h2 className="mt-6 text-2xl font-extrabold text-slate-950">Backend Request Failed</h2>
          <p className="mt-3 text-sm leading-7 text-slate-500">{errorMessage}</p>
          <p className="mt-3 text-xs font-medium uppercase tracking-[0.18em] text-slate-400">
            Make sure FastAPI is running on <span className="font-mono">http://127.0.0.1:8000</span> or set <span className="font-mono">VITE_API_BASE_URL</span>.
          </p>
        </CardContent>
      </Card>
    );
  }

  if (!report) {
    return (
      <Card className="flex min-h-[720px] items-center justify-center">
        <CardContent className="flex max-w-md flex-col items-center justify-center py-16 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-blue-50 text-blue-700">
            <FileSearch className="h-7 w-7" />
          </div>
          <h2 className="mt-6 text-2xl font-extrabold text-slate-950">Final Report Panel</h2>
          <p className="mt-3 text-sm leading-7 text-slate-500">
            Run the orchestrator to populate the executive summary, insights, opportunities,
            risks, confidence score, and source ledger.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-5">
      <ReportSectionCard title="Executive Summary" icon={Sparkle}>
        <p className="text-sm leading-7 text-slate-600">{report.executiveSummary}</p>
      </ReportSectionCard>

      <div className="grid gap-5 2xl:grid-cols-2">
        <ReportSectionCard title="Key Insights" icon={Compass}>
          <InsightList items={report.keyInsights} tone="blue" />
        </ReportSectionCard>
        <ReportSectionCard title="Opportunities" icon={BriefcaseBusiness}>
          <InsightList items={report.opportunities} tone="emerald" />
        </ReportSectionCard>
      </div>

      <div className="grid gap-5 2xl:grid-cols-[minmax(0,1.1fr)_minmax(280px,0.9fr)]">
        <ReportSectionCard title="Risks" icon={ShieldAlert}>
          <InsightList items={report.risks} tone="amber" />
        </ReportSectionCard>
        <ReportSectionCard title="Confidence" icon={BarChart3}>
          <div className="space-y-5">
            <div className="rounded-3xl bg-slate-950 p-5 text-white">
              <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-300">
                Confidence Score
              </p>
              <div className="mt-3 flex items-end justify-between gap-4">
                <p className="text-4xl font-extrabold">
                  {Math.round(report.confidence * 100)}
                  <span className="text-xl text-slate-400">/100</span>
                </p>
                <Badge variant="success">High trust signal</Badge>
              </div>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-gradient-to-r from-blue-700 via-blue-500 to-cyan-400"
                style={{ width: `${report.confidence * 100}%` }}
              />
            </div>
            <p className="text-sm leading-6 text-slate-500">
              Confidence reflects source quality, consistency across agents, and whether the critic
              accepted the evidence base without major unresolved gaps.
            </p>
          </div>
        </ReportSectionCard>
      </div>

      <ReportSectionCard title="Filtered Sources" icon={FileSearch}>
        <p className="mb-4 text-sm leading-6 text-slate-500">
          Only critic-approved, intent-aligned sources appear here. Raw Tavily hits and rejected
          broad-context pages are excluded from the final report.
        </p>
        <div className="space-y-3">
          {report.sources.map((source) => (
            <a
              key={`${source.domain}-${source.title}`}
              href={source.url}
              target="_blank"
              rel="noreferrer"
              className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white/70 p-4 transition hover:border-blue-200 hover:bg-blue-50/40 sm:flex-row sm:items-center sm:justify-between"
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-slate-900">{source.title}</p>
                <p className="mt-1 text-sm text-slate-500">{source.domain}</p>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant="outline">Trust {Math.round(source.trustScore * 100)}%</Badge>
                {typeof source.relevanceScore === "number" ? (
                  <Badge variant="primary">Relevant {Math.round(source.relevanceScore * 100)}%</Badge>
                ) : null}
                <ExternalLink className="h-4 w-4 text-slate-400" />
              </div>
            </a>
          ))}
        </div>
      </ReportSectionCard>
    </div>
  );
}

function InsightList({
  items,
  tone,
}: {
  items: string[];
  tone: "blue" | "emerald" | "amber";
}) {
  const toneClasses = {
    blue: "bg-blue-500",
    emerald: "bg-emerald-500",
    amber: "bg-amber-500",
  } as const;

  return (
    <ul className="space-y-3">
      {items.map((item) => (
        <li key={item} className="flex items-start gap-3 rounded-2xl bg-slate-50/90 p-4 text-sm leading-7 text-slate-600">
          <span className={`mt-2 h-2 w-2 shrink-0 rounded-full ${toneClasses[tone]}`} />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

function LoadingCard() {
  return (
    <Card>
      <CardContent className="space-y-4 py-6">
        <div className="h-5 w-40 animate-pulse rounded-full bg-slate-200" />
        <div className="h-24 animate-pulse rounded-3xl bg-slate-100" />
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="h-20 animate-pulse rounded-3xl bg-slate-100" />
          <div className="h-20 animate-pulse rounded-3xl bg-slate-100" />
        </div>
      </CardContent>
    </Card>
  );
}
