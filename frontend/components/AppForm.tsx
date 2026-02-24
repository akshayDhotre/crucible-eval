"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { useForgeStore } from "../lib/store";
import type { AppDetails, AppType, GenerateResponse, OutputFormat, Provider } from "../lib/types";
import { ProviderSelector } from "./ProviderSelector";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const DEFAULT_PROVIDER = process.env.NEXT_PUBLIC_DEFAULT_PROVIDER ?? "openai";
const DEFAULT_MODEL_NAME = process.env.NEXT_PUBLIC_DEFAULT_MODEL_NAME ?? "";
const extensionByFormat: Record<OutputFormat, string> = {
  promptfoo: ".yaml",
  deepeval: ".py",
  ragas: ".json",
  raw: ".json",
};

const isProvider = (value: string): value is Provider =>
  ["openai", "anthropic", "google", "ollama", "lmstudio"].includes(value);

type DemoPreset = {
  label: string;
  payload: AppDetails;
};

const demoPresets: DemoPreset[] = [
  {
    label: "RAG Support",
    payload: {
      appType: "rag",
      systemPrompt: "You are a support assistant that must answer only from approved policy snippets.",
      description: "Support assistant for refunds and shipping ETA.",
      domain: "e-commerce",
      provider: "openai",
      testCaseCount: 25,
      outputFormat: "promptfoo",
      exampleInteractions: [
        { input: "Can I return an opened item?", output: "Open-box returns are allowed within 14 days." },
        { input: "Where is my order?", output: "Share your tracking ID and I can verify status." },
      ],
    },
  },
  {
    label: "Agent Finance",
    payload: {
      appType: "agent",
      systemPrompt: "You are an analyst agent. Use tools for calculations and data lookup before answering.",
      description: "Internal finance analyst assistant for quarterly reporting.",
      domain: "finance",
      provider: "anthropic",
      testCaseCount: 25,
      outputFormat: "deepeval",
      exampleInteractions: [
        { input: "Compute q/q revenue growth from 18.3M to 19.9M", output: "Growth is approximately 8.74%." },
        { input: "Summarize net retention risk", output: "Flag accounts with spend decline over 20% over 2 quarters." },
      ],
    },
  },
  {
    label: "Chatbot Healthcare",
    payload: {
      appType: "chatbot",
      systemPrompt: "You provide general health guidance and must refuse diagnosis or prescriptions.",
      description: "Consumer-facing wellness chatbot with strict refusal boundaries.",
      domain: "healthcare",
      provider: "google",
      testCaseCount: 10,
      outputFormat: "ragas",
      exampleInteractions: [
        { input: "I have chest pain, what medicine should I take?", output: "I cannot prescribe medication; seek immediate medical care." },
        { input: "How much water should adults drink daily?", output: "Roughly 2 to 3 liters, adjusted for activity and climate." },
      ],
    },
  },
];

const defaultPayload: AppDetails = {
  appType: "rag",
  systemPrompt: "You are a helpful support assistant that answers only from policy documents.",
  description: "Customer support assistant for ecommerce return and shipping policy.",
  domain: "e-commerce",
  provider: isProvider(DEFAULT_PROVIDER) ? DEFAULT_PROVIDER : "openai",
  testCaseCount: 25,
  outputFormat: "promptfoo",
  exampleInteractions: [
    { input: "What is your return window?", output: "Returns are accepted within 30 days with receipt." },
    { input: "Can I return digital goods?", output: "Digital goods are non-refundable after download." },
  ],
};

export function AppForm() {
  const [payload, setPayload] = useState<AppDetails>(defaultPayload);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const setResult = useForgeStore((state) => state.setResult);
  const router = useRouter();

  const update = <K extends keyof AppDetails>(key: K, value: AppDetails[K]) => {
    setPayload((prev) => ({ ...prev, [key]: value }));
  };

  const updateExample = (index: number, key: "input" | "output", value: string) => {
    const next = [...(payload.exampleInteractions ?? [])];
    const existing = next[index] ?? { input: "", output: "" };
    next[index] = { ...existing, [key]: value };
    update("exampleInteractions", next);
  };

  const parseError = async (response: Response): Promise<string> => {
    try {
      const body = (await response.json()) as { detail?: string };
      return body.detail ?? `API error: ${response.status}`;
    } catch {
      return `API error: ${response.status}`;
    }
  };

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const cleanedExamples = (payload.exampleInteractions ?? []).filter(
        (item) => item.input.trim() && item.output.trim(),
      );
      const requestBody = { ...payload, exampleInteractions: cleanedExamples };

      const response = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(await parseError(response));
      }

      const data = (await response.json()) as GenerateResponse;
      setResult(requestBody, data);
      router.push("/result");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate test suite");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold">Forge Eval Suite</h2>

      <div className="rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
        Mode is automatic: if selected provider keys are configured, generation runs in live mode. Otherwise, backend
        attempts local LLM (`ollama` or `lmstudio`) and falls back to static demo output.
      </div>

      <div className="rounded-md border border-slate-200 bg-white p-3 text-sm">
        <span className="font-semibold text-slate-700">Active provider:</span>{" "}
        <span className="rounded bg-slate-100 px-2 py-0.5 font-mono text-xs">{payload.provider}</span>
        <span className="ml-3 font-semibold text-slate-700">Model:</span>{" "}
        <span className="rounded bg-slate-100 px-2 py-0.5 font-mono text-xs">
          {DEFAULT_MODEL_NAME || "provider default"}
        </span>
      </div>

      <div className="rounded-md border border-slate-200 p-3">
        <p className="mb-2 text-sm font-medium text-slate-700">Quick Presets</p>
        <div className="flex flex-wrap gap-2">
          {demoPresets.map((preset) => (
            <button
              key={preset.label}
              type="button"
              onClick={() => setPayload(preset.payload)}
              className="rounded-md border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700"
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      <label className="block text-sm font-medium">
        App Type
        <select
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
          value={payload.appType}
          onChange={(e) => update("appType", e.target.value as AppType)}
        >
          <option value="rag">RAG</option>
          <option value="chatbot">Chatbot</option>
          <option value="agent">Agent</option>
          <option value="codegen">Codegen</option>
          <option value="custom">Custom</option>
        </select>
      </label>

      <label className="block text-sm font-medium">
        System Prompt
        <textarea
          className="mt-1 min-h-28 w-full rounded-md border border-slate-300 px-3 py-2"
          value={payload.systemPrompt}
          onChange={(e) => update("systemPrompt", e.target.value)}
        />
      </label>

      <label className="block text-sm font-medium">
        Description
        <textarea
          className="mt-1 min-h-24 w-full rounded-md border border-slate-300 px-3 py-2"
          value={payload.description}
          onChange={(e) => update("description", e.target.value)}
        />
      </label>

      <label className="block text-sm font-medium">
        Domain
        <input
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
          value={payload.domain}
          onChange={(e) => update("domain", e.target.value)}
        />
      </label>

      <div className="rounded-md border border-slate-200 p-3">
        <p className="mb-2 text-sm font-medium">Example Interactions (optional)</p>
        {[0, 1].map((index) => (
          <div key={index} className="mb-3 grid gap-2 md:grid-cols-2">
            <input
              className="rounded-md border border-slate-300 px-3 py-2 text-sm"
              placeholder={`Example input ${index + 1}`}
              value={payload.exampleInteractions?.[index]?.input ?? ""}
              onChange={(e) => updateExample(index, "input", e.target.value)}
            />
            <input
              className="rounded-md border border-slate-300 px-3 py-2 text-sm"
              placeholder={`Expected output ${index + 1}`}
              value={payload.exampleInteractions?.[index]?.output ?? ""}
              onChange={(e) => updateExample(index, "output", e.target.value)}
            />
          </div>
        ))}
      </div>

      <label className="block text-sm font-medium">
        Provider
        <div className="mt-1">
          <ProviderSelector value={payload.provider} onChange={(p) => update("provider", p as Provider)} />
        </div>
      </label>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <label className="block text-sm font-medium">
          Test Case Count
          <select
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
            value={payload.testCaseCount}
            onChange={(e) => update("testCaseCount", Number(e.target.value) as 10 | 25 | 50)}
          >
            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
          </select>
        </label>

        <label className="block text-sm font-medium">
          Output Format
          <select
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
            value={payload.outputFormat}
            onChange={(e) => update("outputFormat", e.target.value as OutputFormat)}
          >
            <option value="promptfoo">Promptfoo</option>
            <option value="deepeval">DeepEval</option>
            <option value="ragas">Ragas</option>
            <option value="raw">Raw JSON</option>
          </select>
          <p className="mt-1 text-xs text-slate-500">
            Download file extension: <span className="font-semibold">{extensionByFormat[payload.outputFormat]}</span>
          </p>
        </label>
      </div>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}

      <button
        type="submit"
        disabled={loading}
        className="rounded-md bg-accent px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
      >
        {loading ? "Generating..." : "Generate Test Suite"}
      </button>
    </form>
  );
}
