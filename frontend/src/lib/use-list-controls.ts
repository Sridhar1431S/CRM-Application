import { useCallback, useState } from "react";
import { useDebouncedValue } from "@/lib/use-debounced-value";

export interface ListControls {
  page: number;
  setPage: (page: number) => void;
  search: string;
  setSearch: (search: string) => void;
  /** Debounced `search`, so typing doesn't fire a request per keystroke. */
  debouncedSearch: string;
  ordering: string;
  /** Changing the sort resets back to the first page. */
  setOrdering: (ordering: string) => void;
}

/** Pagination, debounced search, and ordering state shared by the list pages. */
export function useListControls(defaultOrdering = "-created_at"): ListControls {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [ordering, setOrderingValue] = useState(defaultOrdering);
  const debouncedSearch = useDebouncedValue(search);

  const setOrdering = useCallback((next: string) => {
    setOrderingValue(next);
    setPage(1);
  }, []);

  return { page, setPage, search, setSearch, debouncedSearch, ordering, setOrdering };
}
