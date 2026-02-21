import type { BenchmarkRef } from "../lib/types";

export function BenchmarkCard({ benchmark }: { benchmark: BenchmarkRef }) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4">
      <h3 className="text-base font-semibold">{benchmark.name}</h3>
      <p className="mt-1 text-sm text-slate-600">{benchmark.reason}</p>
      {benchmark.link ? (
        <a className="mt-3 inline-block text-sm text-accent" href={benchmark.link} target="_blank" rel="noreferrer">
          Reference
        </a>
      ) : null}
    </article>
  );
}
