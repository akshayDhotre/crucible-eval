export type AppType = "rag" | "chatbot" | "agent" | "codegen" | "custom";
export type Provider = "openai" | "anthropic" | "google" | "ollama" | "lmstudio";
export type OutputFormat = "promptfoo" | "deepeval" | "ragas" | "raw";

export type AppDetails = {
  appType: AppType;
  systemPrompt: string;
  description: string;
  domain: string;
  exampleInteractions?: { input: string; output: string }[];
  provider: Provider;
  testCaseCount: 10 | 25 | 50;
  outputFormat: OutputFormat;
};

export type TestCategory =
  | "happy_path"
  | "adversarial"
  | "edge_case"
  | "refusal"
  | "hallucination_probe"
  | "context_relevance"
  | "jailbreak"
  | "prompt_injection"
  | "off_topic";

export type TestCase = {
  id: string;
  category: TestCategory;
  input: string;
  expectedOutput?: string;
  evalCriteria: string[];
  severity: "critical" | "high" | "medium" | "low";
  notes?: string;
};

export type BenchmarkRef = {
  name: string;
  reason: string;
  link?: string;
};

export type TestSuite = {
  appType: AppType;
  generatedAt: string;
  totalCases: number;
  testCases: TestCase[];
  benchmarks: BenchmarkRef[];
  frameworkConfig: Record<string, unknown>;
};

export type GenerateResponse = {
  suite: TestSuite;
  exportFilename: string;
  exportMimeType: string;
  exportContent: string;
};
