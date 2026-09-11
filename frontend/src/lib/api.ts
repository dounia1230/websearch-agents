import type { FinalReportModel } from "@/lib/mock-data";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

export interface RunResearchParams {
  question: string;
  imageFile?: File | null;
}

interface ApiReportSource {
  id: string;
  title: string;
  url: string;
  source_type: "web" | "private_data";
  quality_score: number | null;
  quality_label: "high" | "medium" | "low" | "unknown";
  relevance_score?: number | null;
  critic_score?: number | null;
}

interface ApiFinalReport {
  executive_summary: string;
  key_insights: string[];
  opportunities: string[];
  risks: string[];
  limitations?: string[];
  confidence: number;
  sources: ApiReportSource[];
}

interface ApiResearchResponse {
  question: string;
  image_paths: string[];
  research_passes: number;
  report: ApiFinalReport;
}

export async function runResearchRequest({
  question,
  imageFile,
}: RunResearchParams): Promise<FinalReportModel> {
  const apiBaseUrl = resolveApiBaseUrl();
  const response = imageFile
    ? await fetch(`${apiBaseUrl}/research/upload`, buildMultipartRequest(question, imageFile))
    : await fetch(`${apiBaseUrl}/research`, buildJsonRequest(question));

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const payload = (await response.json()) as ApiResearchResponse;
  return mapApiReportToUiModel(payload.report);
}


function buildJsonRequest(question: string): RequestInit {
  return {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      image_paths: [],
    }),
  };
}


function buildMultipartRequest(question: string, imageFile: File): RequestInit {
  const formData = new FormData();
  formData.append("question", question);
  formData.append("files", imageFile);

  return {
    method: "POST",
    body: formData,
  };
}


async function readErrorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: string | { message?: string } };
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
    if (payload.detail && typeof payload.detail === "object" && "message" in payload.detail) {
      return String(payload.detail.message);
    }
  } catch {
    // Ignore parse failures and fall through to a generic error.
  }

  return `Backend request failed with status ${response.status}.`;
}


function mapApiReportToUiModel(report: ApiFinalReport): FinalReportModel {
  return {
    executiveSummary: report.executive_summary,
    keyInsights: report.key_insights,
    opportunities: report.opportunities,
    risks: report.risks,
    confidence: report.confidence,
    sources: report.sources.map((source) => ({
      title: source.title,
      domain: extractDomain(source.url),
      url: source.url,
      trustScore: source.quality_score ?? source.critic_score ?? 0,
      relevanceScore: source.relevance_score ?? source.critic_score ?? undefined,
    })),
  };
}


function extractDomain(url: string): string {
  try {
    const parsedUrl = new URL(url);
    return parsedUrl.hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}


function resolveApiBaseUrl(): string {
  const configuredUrl = import.meta.env.VITE_API_BASE_URL as string | undefined;
  return (configuredUrl?.trim() || DEFAULT_API_BASE_URL).replace(/\/$/, "");
}
