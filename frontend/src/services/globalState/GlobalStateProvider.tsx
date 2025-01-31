"use client";

import { useStore } from "zustand";
import { useShallow } from "zustand/react/shallow";
import { createStore, StoreApi } from "zustand/vanilla";

import { createContext, useContext, useRef, type ReactNode } from "react";

import { FilterOption } from "src/components/search/SearchFilterAccordion/SearchFilterAccordion";

type GlobalStateItems = {
  agencyOptions: FilterOption[];
  flattenedAgencyOptions: FilterOption[];
};

type GlobalStateActions = {
  setAgencyOptions: (options: FilterOption[]) => void;
};

type GlobalState = GlobalStateItems & GlobalStateActions;

type GlobalStore = StoreApi<GlobalState>;

interface GlobalStateProviderProps {
  children: ReactNode;
}

const defaultInitState: GlobalStateItems = {
  agencyOptions: [],
  flattenedAgencyOptions: [],
};

// gives us a flattened list of all filter options and children
const flattenChildren = (options: FilterOption[]): FilterOption[] => {
  return options.reduce((flattened, option) => {
    return option.children
      ? flattened.concat([option, ...option.children])
      : flattened.concat([option]);
  }, [] as FilterOption[]);
};

const createGlobalStore = (initState = defaultInitState) => {
  return createStore<GlobalState>()((set) => ({
    ...initState,
    setAgencyOptions: (agencyOptions: FilterOption[]) =>
      set(() => ({
        agencyOptions,
        flattenedAgencyOptions: flattenChildren(agencyOptions),
      })),
  }));
};

const GlobalStateContext = createContext<GlobalStore | undefined>(undefined);

// ref usage works around Next JS weirdness - see https://zustand.docs.pmnd.rs/guides/nextjs
export const GlobalStateProvider = ({ children }: GlobalStateProviderProps) => {
  const storeRef = useRef<GlobalStore>(undefined);
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
  // references the store created and passed down as value in the provider
  const globalStateStore = useContext(GlobalStateContext);

  if (!globalStateStore) {
    throw new Error("useGlobalState must be used within GlobalStateProvider");
  }

  // not sure what useShallow is doing here but it's necessary :shrug:
  return useStore(globalStateStore, useShallow(selector));
};
