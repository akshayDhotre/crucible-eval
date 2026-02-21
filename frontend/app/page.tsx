import Link from "next/link";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-16">
      <p className="text-sm uppercase tracking-[0.2em] text-slate-600">Crucible Eval</p>
      <h1 className="mt-3 max-w-3xl text-4xl font-semibold leading-tight md:text-5xl">
        Generate runnable evaluation suites for your LLM app in minutes.
      </h1>
      <p className="mt-4 max-w-2xl text-lg text-slate-700">
        Describe your system prompt, select a provider, and download framework-ready configs for Promptfoo,
        DeepEval, or Ragas.
      </p>
      <div className="mt-8">
        <Link
          className="rounded-md bg-accent px-5 py-3 text-sm font-semibold text-white transition hover:opacity-90"
          href="/forge"
        >
          Open Forge
        </Link>
      </div>

      <section className="mt-8 rounded-xl border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-semibold">Quick Guidelines For Better Outcomes</h2>
        <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-700">
          <li>Paste your real system prompt, not a summary.</li>
          <li>Set domain precisely (for example: healthcare, legal, finance, ecommerce).</li>
          <li>Add 2 realistic example interactions to improve specificity.</li>
          <li>Choose output format based on what you will run immediately.</li>
          <li>Use 25 or 50 cases when validating safety and adversarial behavior.</li>
        </ul>
      </section>
    </main>
  );
}
