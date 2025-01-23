"use client";

import { useStore } from "zustand";
import { useShallow } from "zustand/react/shallow";
import { createStore, StoreApi } from "zustand/vanilla";

import { createContext, useContext, useRef, type ReactNode } from "react";

import { FilterOption } from "src/components/search/SearchFilterAccordion/SearchFilterAccordion";

type GlobalStateItems = {
  agencyOptions: FilterOption[];
};

type GlobalStateActions = {
  setAgencyOptions: (options: FilterOption[]) => void;
};

// can break this into items vs actions if it gets too big
type GlobalState = GlobalStateItems & GlobalStateActions;

type GlobalStore = StoreApi<GlobalState>;

const defaultInitState: GlobalStateItems = {
  agencyOptions: [],
};

const createGlobalStore = (initState = defaultInitState) => {
  return createStore<GlobalState>()((set) => ({
    ...initState,
    setAgencyOptions: (agencyOptions: FilterOption[]) =>
      set(() => ({ agencyOptions })),
  }));
};

const GlobalStateContext = createContext<GlobalStore | undefined>(undefined);

interface GlobalStateProviderProps {
  children: ReactNode;
}

export const GlobalStateProvider = ({ children }: GlobalStateProviderProps) => {
  const storeRef = useRef<GlobalStore>();
  if (!storeRef.current) {
    storeRef.current = createGlobalStore();
  }

  return (
    <GlobalStateContext.Provider value={storeRef.current}>
      {children}
    </GlobalStateContext.Provider>
  );
};

// selector here is a generic function that will take the store as an argument and return
// whatever you want from that store
export const useGlobalState = <T extends Partial<GlobalState>>(
  selector: (store: GlobalState) => T,
): T => {
  // references the store created and passsed down as value in the provider
  const globalStateStore = useContext(GlobalStateContext);

  if (!globalStateStore) {
    throw new Error("useGlobalState must be used within GlobalStateProvider");
  }

  return useStore(globalStateStore, useShallow(selector)) as T;
};
