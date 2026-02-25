import type { Provider } from "../lib/types";

type Props = {
  value: Provider;
  onChange: (provider: Provider) => void;
};

const options: Provider[] = ["openai", "anthropic", "google", "ollama"];

export function ProviderSelector({ value, onChange }: Props) {
  return (
    <div className="grid grid-cols-2 gap-2 md:grid-cols-5">
      {options.map((option) => (
        <button
          key={option}
          type="button"
          onClick={() => onChange(option)}
          className={`rounded-md border px-3 py-2 text-sm capitalize transition ${
            value === option ? "border-accent bg-orange-50" : "border-slate-300 bg-white"
          }`}
        >
          {option}
        </button>
      ))}
    </div>
  );
}
