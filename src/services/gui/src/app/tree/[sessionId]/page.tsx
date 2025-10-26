"use client";

import JobTreeViewer from "@/components/tree-viewer/JobTreeViewer";

export default function TreePage({
  params,
}: {
  params: { sessionId: string };
}) {
  const { sessionId } = params;
  return <JobTreeViewer sessionId={decodeURIComponent(sessionId)} />;
}
