// Route param prop for app router server-side pages
export interface ServerSideRouteParams {
  slug: string;
  locale: string;
}

// Query param prop for app router server-side pages
export interface OptionalStringDict {
  [key: string]: string | undefined;
}
