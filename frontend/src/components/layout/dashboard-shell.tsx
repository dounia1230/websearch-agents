import type { ReactNode } from "react";

export function DashboardShell({
  left,
  center,
  right,
}: {
  left: ReactNode;
  center: ReactNode;
  right: ReactNode;
}) {
  return (
    <main className="mx-auto max-w-[1800px] px-5 py-6 sm:px-6 lg:px-8">
      <div className="grid gap-5 xl:grid-cols-[340px_minmax(0,480px)_minmax(0,1fr)] 2xl:grid-cols-[360px_minmax(0,520px)_minmax(0,1fr)]">
        <div className="xl:sticky xl:top-[88px] xl:h-[calc(100vh-112px)]">{left}</div>
        <div>{center}</div>
        <div>{right}</div>
      </div>
    </main>
  );
}
