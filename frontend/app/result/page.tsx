"use client";

import Link from "next/link";
import { useState } from "react";

import { BenchmarkCard } from "../../components/BenchmarkCard";
import { DownloadPanel } from "../../components/DownloadPanel";
import { TestCaseTable } from "../../components/TestCaseTable";
import { useForgeStore } from "../../lib/store";

export default function ResultPage() {
  const result = useForgeStore((state) => state.result);
  const [copiedPreview, setCopiedPreview] = useState(false);

  if (!result) {
    return (
      <main className="mx-auto max-w-4xl px-4 py-10">
        <p className="text-slate-700">No result available yet.</p>
        <Link className="mt-3 inline-block text-accent" href="/forge">
          Go to Forge
        </Link>
      </main>
    );
  }

  const mode = String(result.suite.frameworkConfig?.mode ?? "live");

  const onCopyPreview = async () => {
    await navigator.clipboard.writeText(result.exportContent);
    setCopiedPreview(true);
    window.setTimeout(() => setCopiedPreview(false), 1200);
  };

  return (
    <main className="mx-auto max-w-5xl space-y-6 px-4 py-10 md:px-6">
      <section className="rounded-lg border border-slate-200 bg-white p-4">
        <h1 className="text-xl font-semibold">Generated Test Suite</h1>
        <p className="mt-1 text-sm text-slate-600">
          {result.suite.totalCases} cases • {result.suite.appType} • {new Date(result.suite.generatedAt).toLocaleString()}
        </p>
        <p className="mt-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Mode: {mode}</p>
      </section>

      <DownloadPanel
        filename={result.exportFilename}
        mimeType={result.exportMimeType}
        content={result.exportContent}
      />

      <section className="rounded-lg border border-slate-200 bg-white p-4">
        <div className="mb-3 flex items-center justify-between gap-2">
          <h2 className="text-lg font-semibold">Config Preview</h2>
          <button
            type="button"
            onClick={onCopyPreview}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700"
          >
            {copiedPreview ? "Copied" : "Copy Preview"}
          </button>
        </div>
        <pre
          className="max-h-80 overflow-auto rounded-md border border-slate-700 p-3 text-xs"
          style={{ backgroundColor: "#0b1220", color: "#e5edff" }}
        >
          {result.exportContent}
        </pre>
      </section>

      <TestCaseTable testCases={result.suite.testCases} />

      <section>
        <h2 className="mb-3 text-lg font-semibold">Benchmark Recommendations</h2>
        <div className="grid gap-3 md:grid-cols-2">
          {result.suite.benchmarks.map((item) => (
            <BenchmarkCard key={item.name} benchmark={item} />
          ))}
        </div>
      </section>
    </main>
  );
}
