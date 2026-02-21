import { create } from "zustand";

import type { AppDetails, GenerateResponse } from "./types";

type ForgeState = {
  lastRequest?: AppDetails;
  result?: GenerateResponse;
  setResult: (request: AppDetails, result: GenerateResponse) => void;
};

export const useForgeStore = create<ForgeState>((set) => ({
  setResult: (request, result) => set({ lastRequest: request, result }),
}));
