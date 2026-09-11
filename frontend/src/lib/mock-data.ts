export type AgentStatus = "idle" | "running" | "done" | "failed";

export type AgentIconKey =
  | "planner"
  | "research"
  | "critic"
  | "summarizer"
  | "vision"
  | "synthesizer"
  | "orchestrator";

export interface AgentCardModel {
  id: string;
  name: string;
  description: string;
  iconKey: AgentIconKey;
  status: AgentStatus;
  preview: string;
  metric: string;
  details: string[];
  runningPreview: string;
  enabled: boolean;
}

export interface SourceItem {
  title: string;
  domain: string;
  url: string;
  trustScore: number;
  relevanceScore?: number;
}

export interface FinalReportModel {
  executiveSummary: string;
  keyInsights: string[];
  opportunities: string[];
  risks: string[];
  confidence: number;
  sources: SourceItem[];
}

export interface DashboardRunOptions {
  query: string;
  deepResearch: boolean;
  includeVision: boolean;
  includeCitations: boolean;
  sourceCount: number;
  imageName: string | null;
}

const SOURCE_LIBRARY: SourceItem[] = [
  {
    title: "EDUCAUSE: Generative AI and Academic Research Workflows",
    domain: "educause.edu",
    url: "https://www.educause.edu",
    trustScore: 0.96,
    relevanceScore: 0.94,
  },
  {
    title: "UNESCO Guidance on Generative AI in Education and Research",
    domain: "unesco.org",
    url: "https://www.unesco.org",
    trustScore: 0.91,
    relevanceScore: 0.9,
  },
  {
    title: "Nature: Research Integrity and AI-Assisted Scholarly Work",
    domain: "nature.com",
    url: "https://www.nature.com",
    trustScore: 0.93,
    relevanceScore: 0.88,
  },
  {
    title: "Inside Higher Ed: Faculty Adoption of AI Research Tools",
    domain: "insidehighered.com",
    url: "https://www.insidehighered.com",
    trustScore: 0.95,
    relevanceScore: 0.87,
  },
  {
    title: "NIST AI Risk Management Framework Overview",
    domain: "nist.gov",
    url: "https://www.nist.gov",
    trustScore: 0.89,
    relevanceScore: 0.79,
  },
  {
    title: "MIT Sloan: Enterprise Adoption Lessons for AI Knowledge Systems",
    domain: "mitsloan.mit.edu",
    url: "https://mitsloan.mit.edu",
    trustScore: 0.94,
    relevanceScore: 0.82,
  },
  {
    title: "Stanford HAI: Institutional Readiness for AI Deployment",
    domain: "hai.stanford.edu",
    url: "https://hai.stanford.edu",
    trustScore: 0.98,
    relevanceScore: 0.84,
  },
  {
    title: "Chronicle of Higher Education: AI Tooling in Research Offices",
    domain: "chronicle.com",
    url: "https://www.chronicle.com",
    trustScore: 0.88,
    relevanceScore: 0.83,
  },
];

export function createInitialAgents(options: DashboardRunOptions): AgentCardModel[] {
  const visionEnabled = options.includeVision && Boolean(options.imageName);

  return [
    {
      id: "planner",
      name: "Planner Agent",
      description: "Interprets user intent and expands the search into precise retrieval queries.",
      iconKey: "planner",
      status: "idle",
      preview: "Waiting to interpret the user request",
      metric: "Intent planning",
      details: [
        "No search plan has been generated yet.",
        "Intent scope and exclusions will be defined before Tavily runs.",
      ],
      runningPreview: "Resolving user intent into focused search queries",
      enabled: true,
    },
    {
      id: "research",
      name: "Research Agent",
      description: "Runs the planned Tavily queries, merges results, and enriches source content.",
      iconKey: "research",
      status: "idle",
      preview: "Awaiting query dispatch",
      metric: `${options.sourceCount} source target`,
      details: [
        "Planner output will drive search breadth.",
        "Reader extraction queue is empty.",
      ],
      runningPreview: "Collecting primary and high-signal secondary sources",
      enabled: true,
    },
    {
      id: "critic",
      name: "Critic Agent",
      description: "Rejects weak evidence, surfaces blind spots, and requests follow-up research.",
      iconKey: "critic",
      status: "idle",
      preview: "Waiting for research brief",
      metric: "Coverage gate",
      details: [
        "Revision decision pending research output.",
        "No unsupported claims flagged yet.",
      ],
      runningPreview: "Checking evidence strength and missing angles",
      enabled: true,
    },
    {
      id: "summarizer",
      name: "Summarizer Agent",
      description: "Compresses validated findings into decision-ready synthesis notes.",
      iconKey: "summarizer",
      status: "idle",
      preview: "Summary layer not started",
      metric: "Structured brief",
      details: [
        "Key insight extraction not started.",
        "Opportunity and risk framing pending.",
      ],
      runningPreview: "Distilling findings into concise insight blocks",
      enabled: true,
    },
    {
      id: "vision",
      name: "Vision Agent",
      description: "Extracts visible evidence from charts, screenshots, or uploaded images.",
      iconKey: "vision",
      status: "idle",
      preview: visionEnabled ? "Ready to inspect uploaded image" : "Inactive until image input exists",
      metric: visionEnabled ? "Vision enabled" : "Optional path",
      details: visionEnabled
        ? [`Image queued: ${options.imageName}`]
        : ["Upload an image and enable vision to activate this stage."],
      runningPreview: "Inspecting visual evidence and OCR-like content",
      enabled: visionEnabled,
    },
    {
      id: "synthesizer",
      name: "Synthesizer Agent",
      description: "Assembles the final report with tradeoffs, confidence, and source traceability.",
      iconKey: "synthesizer",
      status: "idle",
      preview: "Final report not assembled",
      metric: "Decision output",
      details: [
        "Executive summary pending.",
        "Confidence and citations will be merged at the end.",
      ],
      runningPreview: "Composing the final analyst-ready report",
      enabled: true,
    },
  ];
}

export function createResolvedAgents(
  options: DashboardRunOptions,
  finalFilteredSourceCount?: number,
): AgentCardModel[] {
  const trustedSources = finalFilteredSourceCount ?? Math.max(4, Math.min(options.sourceCount - 1, 7));
  const claims = options.deepResearch ? 12 : 8;

  return [
    {
      id: "planner",
      name: "Planner Agent",
      description: "Interprets user intent and expands the search into precise retrieval queries.",
      iconKey: "planner",
      status: "done",
      preview: "Intent interpreted into focused Tavily searches and exclusions",
      metric: "3-5 queries",
      details: [
        "Translated the user request into an intent-aware query plan.",
        "Added exclusions to avoid broad off-context sources.",
      ],
      runningPreview: "Resolving user intent into focused search queries",
      enabled: true,
    },
    {
      id: "research",
      name: "Research Agent",
      description: "Runs the planned Tavily queries, merges results, and enriches source content.",
      iconKey: "research",
      status: "done",
      preview: `${options.sourceCount} sources found across the planner-guided search set`,
      metric: `${options.sourceCount} collected`,
      details: [
        `Normalized ${options.sourceCount} merged web results into source records.`,
        "Expanded top results with clean-page extraction.",
        options.deepResearch ? "Ran a deeper pass to widen institutional coverage." : "Used the standard search budget.",
      ],
      runningPreview: "Collecting primary and high-signal secondary sources",
      enabled: true,
    },
    {
      id: "critic",
      name: "Critic Agent",
      description: "Rejects weak evidence, surfaces blind spots, and requests follow-up research.",
      iconKey: "critic",
      status: "done",
      preview: `${trustedSources} trusted and intent-aligned sources kept after critique`,
      metric: `${trustedSources} validated`,
      details: [
        "Flagged low-signal and off-intent pages for exclusion.",
        "Confirmed the core evidence base before synthesis.",
        options.includeCitations ? "Preserved inline citation hooks for downstream reporting." : "Citations are hidden in the UI but still available in data.",
      ],
      runningPreview: "Checking evidence strength and missing angles",
      enabled: true,
    },
    {
      id: "summarizer",
      name: "Summarizer Agent",
      description: "Compresses validated findings into decision-ready synthesis notes.",
      iconKey: "summarizer",
      status: "done",
      preview: `${claims} claims extracted into grouped insight themes`,
      metric: `${claims} claims`,
      details: [
        "Grouped findings into executive, opportunity, and risk lenses.",
        "Collapsed repeated evidence into concise briefing points.",
      ],
      runningPreview: "Distilling findings into concise insight blocks",
      enabled: true,
    },
    {
      id: "vision",
      name: "Vision Agent",
      description: "Extracts visible evidence from charts, screenshots, or uploaded images.",
      iconKey: "vision",
      status: options.includeVision && Boolean(options.imageName) ? "done" : "idle",
      preview:
        options.includeVision && Boolean(options.imageName)
          ? `Image evidence merged from ${options.imageName}`
          : "Skipped because no image was provided",
      metric:
        options.includeVision && Boolean(options.imageName)
          ? "1 image analyzed"
          : "Skipped",
      details:
        options.includeVision && Boolean(options.imageName)
          ? [
              "Captured direct visual facts from the uploaded image.",
              "Separated visible evidence from interpretation.",
            ]
          : ["The multimodal path remains available for future image-based runs."],
      runningPreview: "Inspecting visual evidence and OCR-like content",
      enabled: options.includeVision && Boolean(options.imageName),
    },
    {
      id: "synthesizer",
      name: "Synthesizer Agent",
      description: "Assembles the final report with tradeoffs, confidence, and source traceability.",
      iconKey: "synthesizer",
      status: "done",
      preview: "Final report assembled with summary, risk, and evidence cards",
      metric: "Report ready",
      details: [
        "Built the executive summary and supporting sections.",
        "Included confidence scoring and source traceability.",
      ],
      runningPreview: "Composing the final analyst-ready report",
      enabled: true,
    },
  ];
}

export function createMockReport(options: DashboardRunOptions): FinalReportModel {
  const queryLabel = options.query.trim() || "the active research topic";
  const sourceSlice = SOURCE_LIBRARY.slice(0, Math.max(4, Math.min(options.sourceCount, SOURCE_LIBRARY.length)));
  const citationSuffix = options.includeCitations ? " [S1][S2]" : "";
  const confidence = options.deepResearch ? 0.91 : 0.84;
  const visionLine =
    options.includeVision && options.imageName
      ? ` Uploaded visual evidence from ${options.imageName} reinforced the strongest themes.`
      : "";

  return {
    executiveSummary:
      `The orchestrator produced a decision-ready view of "${queryLabel}" by blending source discovery, critique, and synthesis.${visionLine} ` +
      `The strongest evidence points to a favorable near-term opportunity, but execution quality and source concentration remain meaningful constraints.${citationSuffix}`,
    keyInsights: [
      `Institutional and high-trust coverage converged on the same core signal: momentum is real, but uneven across segments.${citationSuffix}`,
      `The critic stage removed low-signal material and improved confidence in the final narrative.${citationSuffix}`,
      options.deepResearch
        ? `A deeper pass widened the evidence base and surfaced longer-horizon implications for leadership planning.${citationSuffix}`
        : `The standard run captured the primary evidence base, but a deep pass could widen long-horizon context.${citationSuffix}`,
    ],
    opportunities: [
      `Use the research brief to prioritize segments with consistent demand indicators and credible institutional validation.${citationSuffix}`,
      `Package the strongest sources into an internal memo or investor-style briefing for faster stakeholder alignment.${citationSuffix}`,
      options.includeVision && options.imageName
        ? `Reuse the uploaded visual artifact as supporting evidence inside a presentation or final report appendix.${citationSuffix}`
        : `Add screenshots or charts in a follow-up run to strengthen evidence communication for non-technical audiences.${citationSuffix}`,
    ],
    risks: [
      `Source concentration can distort confidence if too many conclusions rely on the same reporting loop.${citationSuffix}`,
      `Timing risk remains material because several signals are directional rather than fully confirmed.${citationSuffix}`,
      `If private documents are introduced later, retrieval quality and chunk provenance will need their own validation layer.${citationSuffix}`,
    ],
    confidence,
    sources: sourceSlice,
  };
}
