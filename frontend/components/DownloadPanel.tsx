"use client";

import { useState } from "react";

export function DownloadPanel({
  filename,
  mimeType,
  content,
}: {
  filename: string;
  mimeType: string;
  content: string;
}) {
  const [copied, setCopied] = useState(false);

  const onDownload = () => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  const onCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  };

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4">
      <h3 className="text-base font-semibold">Download Config</h3>
      <p className="mt-1 text-sm text-slate-600">{filename}</p>
      <div className="mt-3 flex gap-2">
        <button
          type="button"
          onClick={onDownload}
          className="rounded-md bg-accent px-4 py-2 text-sm font-semibold text-white"
        >
          Download
        </button>
        <button
          type="button"
          onClick={onCopy}
          className="rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700"
        >
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
    </section>
  );
}
