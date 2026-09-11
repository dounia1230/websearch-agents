import { FileStack, ImagePlus, Layers3, Play, ScanSearch, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

interface ControlPanelProps {
  query: string;
  sourceCount: number;
  deepResearch: boolean;
  includeVision: boolean;
  includeCitations: boolean;
  imageName: string | null;
  isRunning: boolean;
  onQueryChange: (value: string) => void;
  onSourceCountChange: (value: number) => void;
  onToggleChange: (field: "deepResearch" | "includeVision" | "includeCitations", value: boolean) => void;
  onImageChange: (file: File | null) => void;
  onRun: () => void;
}

const SOURCE_COUNT_OPTIONS = [4, 6, 8, 10];

export function ControlPanel({
  query,
  sourceCount,
  deepResearch,
  includeVision,
  includeCitations,
  imageName,
  isRunning,
  onQueryChange,
  onSourceCountChange,
  onToggleChange,
  onImageChange,
  onRun,
}: ControlPanelProps) {
  return (
    <Card className="flex h-full flex-col overflow-hidden">
      <CardHeader className="border-b border-slate-100 pb-5">
        <div className="flex items-start gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-950 text-white">
            <ScanSearch className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">
              Input / Control
            </p>
            <CardTitle className="mt-1 text-xl">Research Run Setup</CardTitle>
            <CardDescription>
              Shape the orchestrator run before dispatching it through the agent workflow.
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-1 space-y-6 overflow-y-auto pt-6">
        <div className="space-y-3">
          <Label htmlFor="research-query">Research Query</Label>
          <Textarea
            id="research-query"
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            placeholder="Example: Evaluate the market opportunity and operational risks for AI-native research platforms in higher education."
          />
        </div>

        <div className="space-y-3">
          <Label htmlFor="image-upload">Image Upload</Label>
          <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50/80 p-4">
            <label
              htmlFor="image-upload"
              className="flex cursor-pointer items-center justify-between gap-3 rounded-2xl bg-white px-4 py-3 shadow-sm transition hover:bg-slate-50"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-blue-50 text-blue-700">
                  <ImagePlus className="h-4.5 w-4.5" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-800">
                    {imageName ?? "Upload screenshot, chart, or artifact"}
                  </p>
                  <p className="text-xs text-slate-500">
                    Optional. Activates the vision agent when included.
                  </p>
                </div>
              </div>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                Browse
              </span>
            </label>
            <Input
              id="image-upload"
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(event) => onImageChange(event.target.files?.[0] ?? null)}
            />
          </div>
        </div>

        <div className="space-y-4">
          <Label>Run Options</Label>
          <div className="space-y-3">
            <ToggleRow
              title="Deep Research"
              description="Expand retrieval breadth and allow a more deliberate critique pass."
              checked={deepResearch}
              onCheckedChange={(value) => onToggleChange("deepResearch", value)}
              icon={Sparkles}
            />
            <ToggleRow
              title="Include Vision Analysis"
              description="Inspect uploaded images and merge visible evidence into the final report."
              checked={includeVision}
              onCheckedChange={(value) => onToggleChange("includeVision", value)}
              icon={ImagePlus}
            />
            <ToggleRow
              title="Include Citations"
              description="Keep source handles visible in the final report preview."
              checked={includeCitations}
              onCheckedChange={(value) => onToggleChange("includeCitations", value)}
              icon={FileStack}
            />
          </div>
        </div>

        <div className="space-y-3">
          <Label htmlFor="source-count">Source Count</Label>
          <div className="relative">
            <select
              id="source-count"
              value={sourceCount}
              onChange={(event) => onSourceCountChange(Number(event.target.value))}
              className="h-12 w-full appearance-none rounded-2xl border border-slate-200 bg-white px-4 text-sm font-medium text-slate-800 shadow-sm outline-none transition focus:border-blue-300 focus:ring-2 focus:ring-blue-100"
            >
              {SOURCE_COUNT_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option} sources
                </option>
              ))}
            </select>
            <Layers3 className="pointer-events-none absolute right-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          </div>
        </div>

        <div className="rounded-3xl bg-slate-950 p-4 text-white">
          <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-300">
            Run Profile
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {[
              deepResearch ? "Deep mode" : "Standard mode",
              includeVision && imageName ? "Vision active" : "Vision standby",
              includeCitations ? "Citations visible" : "Citations compact",
            ].map((item) => (
              <span
                key={item}
                className="rounded-full bg-white/10 px-3 py-1 text-xs font-semibold text-slate-100"
              >
                {item}
              </span>
            ))}
          </div>
        </div>
      </CardContent>
      <div className="border-t border-slate-100 p-6">
        <Button size="lg" className="w-full" onClick={onRun} disabled={isRunning || !query.trim()}>
          <Play className="h-4 w-4" />
          {isRunning ? "Running Analysis..." : "Run Analysis"}
        </Button>
      </div>
    </Card>
  );
}

function ToggleRow({
  title,
  description,
  checked,
  onCheckedChange,
  icon: Icon,
}: {
  title: string;
  description: string;
  checked: boolean;
  onCheckedChange: (value: boolean) => void;
  icon: typeof Sparkles;
}) {
  return (
    <div
      className={cn(
        "flex items-start justify-between gap-4 rounded-2xl border border-slate-200 bg-white/85 px-4 py-3 transition",
        checked && "border-blue-200 bg-blue-50/60",
      )}
    >
      <div className="flex gap-3">
        <div
          className={cn(
            "mt-0.5 flex h-10 w-10 items-center justify-center rounded-2xl",
            checked ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-600",
          )}
        >
          <Icon className="h-4.5 w-4.5" />
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-800">{title}</p>
          <p className="text-sm leading-6 text-slate-500">{description}</p>
        </div>
      </div>
      <Switch checked={checked} onCheckedChange={onCheckedChange} />
    </div>
  );
}
