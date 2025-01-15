import { ServerSideSearchParams } from "src/types/searchRequestURLTypes";

export enum Breakpoints {
  CARD = "card",
  CARD_LG = "card-lg",
  MOBILE = "mobile",
  MOBILE_LG = "mobile-lg",
  TABLET = "tablet",
  TABLET_LG = "tablet-lg",
  DESKTOP = "desktop",
  DESKTOP_LG = "desktop-lg",
  WIDESCREEN = "widescreen",
}

export type WithFeatureFlagProps = {
  searchParams: Promise<ServerSideSearchParams>;
};

export interface ErrorProps {
  // Next's error boundary also includes a reset function as a prop for retries,
  // but it was not needed as users can retry with new inputs in the normal page flow.
  error: Error & { digest?: string };
}
