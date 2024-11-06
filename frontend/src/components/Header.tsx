"use client";

import { useFeatureFlags } from "src/hooks/useFeatureFlags";
import { assetPath } from "src/utils/assetPath";

import { useTranslations } from "next-intl";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useMemo, useState } from "react";
import {
  GovBanner,
  NavMenuButton,
  PrimaryNav,
  Title,
  Header as USWDSHeader,
} from "@trussworks/react-uswds";

type PrimaryLink = {
  text?: string;
  href?: string;
};

type Props = {
  logoPath?: string;
  locale?: string;
};

const NavLinks = ({
  mobileExpanded,
  onToggleMobileNav,
}: {
  mobileExpanded: boolean;
  onToggleMobileNav: () => unknown;
}) => {
  const t = useTranslations("Header");
  const { featureFlagsManager } = useFeatureFlags();
  const path = usePathname();

  const getSearchLink = useCallback(
    (onSearch: boolean, enabled: boolean) => {
      if (!enabled) {
        return {};
      }
      return {
        text: t("nav_link_search"),
        href: onSearch ? "/search?refresh=true" : "/search",
      };
    },
    [t],
  );

  const navLinkList = useMemo(() => {
    return [
      { text: t("nav_link_home"), href: "/" },
      getSearchLink(
        path.includes("/search"),
        featureFlagsManager.isFeatureEnabled("showSearchV0"),
      ),
      { text: t("nav_link_process"), href: "/process" },
      { text: t("nav_link_research"), href: "/research" },
      { text: t("nav_link_subscribe"), href: "/subscribe" },
    ];
  }, [t, path, featureFlagsManager, getSearchLink]);

  const navItems = useMemo(() => {
    return navLinkList.map((link: PrimaryLink) => {
      if (!link.text || !link.href) {
        return <></>;
      }
      return (
        <Link href={link.href} key={link.href}>
          {link.text}
        </Link>
      );
    });
  }, [navLinkList]);

  return (
    <PrimaryNav
      items={navItems}
      mobileExpanded={mobileExpanded}
      onToggleMobileNav={onToggleMobileNav}
    ></PrimaryNav>
  );
};

const Header = ({ logoPath, locale }: Props) => {
  const t = useTranslations("Header");
  const [isMobileNavExpanded, setIsMobileNavExpanded] =
    useState<boolean>(false);
  const handleMobileNavToggle = () => {
    setIsMobileNavExpanded(!isMobileNavExpanded);
  };
  const language = locale && locale.match("/^es/") ? "spanish" : "english";

  return (
    <>
      <div
        className={`usa-overlay ${isMobileNavExpanded ? "is-visible" : ""}`}
      />
      <GovBanner language={language} />
      <USWDSHeader basic={true}>
        <div className="usa-nav-container">
          <div className="usa-navbar">
            <Title className="desktop:margin-top-2">
              <div className="display-flex flex-align-center">
                {logoPath && (
                  <span className="margin-right-1">
                    <img
                      className="width-3 desktop:width-5 text-bottom margin-right-05"
                      src={assetPath(logoPath)}
                      alt="Site logo"
                    />
                  </span>
                )}
                <span className="font-sans-lg flex-fill">{t("title")}</span>
              </div>
            </Title>
            <NavMenuButton
              onClick={handleMobileNavToggle}
              label={t("nav_menu_toggle")}
            />
          </div>
          <NavLinks
            mobileExpanded={isMobileNavExpanded}
            onToggleMobileNav={handleMobileNavToggle}
          />
        </div>
      </USWDSHeader>
    </>
  );
};

export default Header;
