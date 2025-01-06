/**
 * @file Middleware allows you to run code before a request is completed. Then, based on
 * the incoming request, you can modify the response by rewriting, redirecting,
 * modifying the request or response headers, or responding directly.
 * @see https://nextjs.org/docs/app/building-your-application/routing/middleware
 */
import { defaultLocale, locales } from "src/i18n/config";
import { featureFlagsManager } from "src/services/featureFlags/FeatureFlagManager";

import createIntlMiddleware from "next-intl/middleware";
import { NextRequest, NextResponse } from "next/server";

export const config = {
  matcher: [
    /*
     * Run Middleware on all request paths except these:
     * - Api routes
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - images (static files in public/images/ directory)
     */
    "/((?!api|_next/static|_next/image|sitemap|public|img|uswds|images|robots.txt|site.webmanifest).*)",
    /**
     * Fix issue where the pattern above was causing middleware
     * to not run on the homepage:
     */
    "/",
  ],
};

/**
 * Detect the user's preferred language and redirect to a localized route
 * if the preferred language isn't the current locale.
 */
const i18nMiddleware = createIntlMiddleware({
  locales,
  defaultLocale,
  // Don't prefix the URL with the locale when the locale is the default locale (i.e. "en-US")
  localePrefix: "as-needed",
});

export default function middleware(request: NextRequest): NextResponse {
  return featureFlagsManager.middleware(request, i18nMiddleware(request));
}
