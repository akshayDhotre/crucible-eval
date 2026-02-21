import type { TestCase } from "../lib/types";

export function TestCaseTable({ testCases }: { testCases: TestCase[] }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-slate-50 text-slate-700">
          <tr>
            <th className="px-3 py-2">Category</th>
            <th className="px-3 py-2">Input</th>
            <th className="px-3 py-2">Criteria</th>
            <th className="px-3 py-2">Severity</th>
          </tr>
        </thead>
        <tbody>
          {testCases.map((tc) => (
            <tr key={tc.id} className="border-t border-slate-100 align-top">
              <td className="px-3 py-2">{tc.category}</td>
              <td className="px-3 py-2">{tc.input}</td>
              <td className="px-3 py-2">{tc.evalCriteria.join(", ")}</td>
              <td className="px-3 py-2 uppercase">{tc.severity}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
