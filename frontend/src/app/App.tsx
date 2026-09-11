import {
  startTransition,
  useEffect,
  useMemo,
  useState,
  type Dispatch,
  type SetStateAction,
} from "react";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { TopNavbar } from "@/components/layout/top-navbar";
import { ControlPanel } from "@/components/panels/control-panel";
import { ReportPanel } from "@/components/panels/report-panel";
import { WorkflowPanel } from "@/components/panels/workflow-panel";
import { runResearchRequest } from "@/lib/api";
import {
  createInitialAgents,
  createResolvedAgents,
  type AgentCardModel,
  type DashboardRunOptions,
  type FinalReportModel,
} from "@/lib/mock-data";

type RunState = "idle" | "running" | "completed";

const DEFAULT_QUERY =
  "Assess the market opportunity, adoption barriers, and strategic risks for AI-native research assistants in higher education institutions.";

function App() {
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [deepResearch, setDeepResearch] = useState(true);
  const [includeVision, setIncludeVision] = useState(false);
  const [includeCitations, setIncludeCitations] = useState(true);
  const [sourceCount, setSourceCount] = useState(8);
  const [imageName, setImageName] = useState<string | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [runState, setRunState] = useState<RunState>("idle");
  const [hasRun, setHasRun] = useState(false);
  const [agents, setAgents] = useState<AgentCardModel[]>([]);
  const [report, setReport] = useState<FinalReportModel | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);

  const runOptions = useMemo<DashboardRunOptions>(
    () => ({
      query,
      deepResearch,
      includeVision,
      includeCitations,
      sourceCount,
      imageName,
    }),
    [deepResearch, imageName, includeCitations, includeVision, query, sourceCount],
  );

  useEffect(() => {
    if (runState === "running") {
      return;
    }
    setAgents(createInitialAgents(runOptions));
  }, [runOptions, runState]);

  async function handleRunAnalysis() {
    if (!query.trim() || runState === "running") {
      return;
    }

    const initialAgents = createInitialAgents(runOptions);
    const resolvedAgents = createResolvedAgents(runOptions);
    const runnableAgents = resolvedAgents.filter((agent) => agent.enabled || agent.id !== "vision");

    setRunState("running");
    setHasRun(true);
    setReport(null);
    setReportError(null);
    setAgents(initialAgents);

    const reportPromise = runResearchRequest({
      question: query,
      imageFile: includeVision ? imageFile : null,
    });

    await animateWorkflow(runnableAgents, setAgents);

    try {
      const fetchedReport = await reportPromise;

      startTransition(() => {
        setReport(fetchedReport);
        setRunState("completed");
        setAgents(createResolvedAgents(runOptions, fetchedReport.sources.length));
      });
    } catch (error: unknown) {
      setAgents((currentAgents) =>
        currentAgents.map((agent) =>
          agent.id === "synthesizer" ? { ...agent, status: "failed", preview: "Backend request failed" } : agent,
        ),
      );
      setRunState("completed");
      setReportError(error instanceof Error ? error.message : "Unknown backend error.");
    }
  }

  return (
    <div className="min-h-screen">
      <TopNavbar />
      <DashboardShell
        left={
          <ControlPanel
            query={query}
            sourceCount={sourceCount}
            deepResearch={deepResearch}
            includeVision={includeVision}
            includeCitations={includeCitations}
            imageName={imageName}
            isRunning={runState === "running"}
            onQueryChange={setQuery}
            onSourceCountChange={setSourceCount}
            onToggleChange={(field, value) => {
              if (field === "deepResearch") setDeepResearch(value);
              if (field === "includeVision") setIncludeVision(value);
              if (field === "includeCitations") setIncludeCitations(value);
            }}
            onImageChange={(file) => {
              setImageFile(file ?? null);
              setImageName(file?.name ?? null);
              if (file) {
                setIncludeVision(true);
              }
            }}
            onRun={handleRunAnalysis}
          />
        }
        center={
          <WorkflowPanel
            agents={agents}
            query={query}
            sourceCount={sourceCount}
            includeVision={includeVision}
            imageName={imageName}
            isRunning={runState === "running"}
            hasRun={hasRun}
          />
        }
        right={
          <ReportPanel
            report={report}
            isRunning={runState === "running"}
            errorMessage={reportError}
          />
        }
      />
    </div>
  );
}

async function animateWorkflow(
  runnableAgents: AgentCardModel[],
  setAgents: Dispatch<SetStateAction<AgentCardModel[]>>,
) {
  for (const resolvedAgent of runnableAgents) {
    setAgents((currentAgents) =>
      currentAgents.map((agent) =>
        agent.id === resolvedAgent.id
          ? {
              ...agent,
              status: "running",
              preview: resolvedAgent.runningPreview,
              metric: "Processing",
            }
          : agent,
      ),
    );

    await wait(800);

    setAgents((currentAgents) =>
      currentAgents.map((agent) => (agent.id === resolvedAgent.id ? resolvedAgent : agent)),
    );

    await wait(450);
  }
}

function wait(milliseconds: number) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, milliseconds);
  });
}

export default App;
