import clsx from "clsx";
import { UserProfile } from "src/services/auth/types";
import { useUser } from "src/services/auth/useUser";

import { useTranslations } from "next-intl";
import { useCallback, useState } from "react";
import {
  IconListContent,
  Menu,
  NavDropDownButton,
} from "@trussworks/react-uswds";

import { LoginButtonModal } from "src/components/LoginButtonModal";
import { USWDSIcon } from "src/components/USWDSIcon";

// used in three different places
// 1. on desktop - nav item drop down button content
// 2. on mobile - nav item drop down button content, without email text
// 3. on mobile - nav sub item content
const UserEmailItem = ({
  email,
  isSubnav,
}: {
  email?: string;
  isSubnav: boolean;
}) => {
  return (
    <a
      className={clsx("flex-align-center", "display-flex", {
        "padding-x-0": !isSubnav,
        "desktop:display-none": isSubnav,
        "usa-nav__submenu-item": isSubnav,
        "usa-button": isSubnav,
        "border-y-0": isSubnav,
      })}
    >
      <USWDSIcon
        name="account_circle"
        className="usa-icon--size-3 display-block"
      />
      <div
        className={clsx("padding-left-1", {
          "display-none": !isSubnav,
          "desktop:display-block": !isSubnav,
        })}
      >
        {email}
      </div>
    </a>
  );
};

const UserDropdown = ({
  user,
  navLogoutLinkText,
  logout,
}: {
  user: UserProfile;
  navLogoutLinkText: string;
  logout: () => Promise<void>;
}) => {
  const [userProfileMenuOpen, setUserProfileMenuOpen] = useState(false);

  const logoutNavItem = (
    <a
      className="display-flex usa-button usa-button--unstyled text-no-underline"
      // eslint-disable-next-line
      onClick={() => logout()}
    >
      <USWDSIcon name="logout" className="usa-icon--size-3 display-block" />
      <IconListContent className="font-sans-sm">
        {navLogoutLinkText}
      </IconListContent>
    </a>
  );

  return (
    <div className="usa-nav__primary-item border-top-0 mobile-nav-dropdown-uncollapsed-override position-relative">
      <NavDropDownButton
        className="padding-y-0 padding-x-2 margin-right-2 height-6"
        // The NavDropDownButton needlessly restricts the label to a string, when passing an Element works
        // perfectly well.
        // eslint-disable-next-line
        // @ts-ignore: Type 'Element' is not assignable to type 'string'
        label={<UserEmailItem isSubnav={false} email={user.email} />}
        isOpen={userProfileMenuOpen}
        onToggle={() => setUserProfileMenuOpen(!userProfileMenuOpen)}
        isCurrent={false}
        menuId="user-control"
      />
      <Menu
        className="position-absolute desktop:width-full z-200 right-0"
        id="user-control"
        items={[
          <UserEmailItem key="email" isSubnav={true} email={user.email} />,
          logoutNavItem,
        ]}
        type="subnav"
        isOpen={userProfileMenuOpen}
      />
    </div>
  );
};

export const UserControl = () => {
  const t = useTranslations("Header");

  const { user, refreshUser } = useUser();

  const logout = useCallback(async (): Promise<void> => {
    await fetch("/api/auth/logout", {
      method: "POST",
    });
    await refreshUser();
  }, [refreshUser]);

  return (
    <>
      {!user?.token && (
        <LoginButtonModal navLoginLinkText={t("nav_link_login")} />
      )}
      {!!user?.token && (
        <UserDropdown
          user={user}
          navLogoutLinkText={t("nav_link_logout")}
          logout={logout}
        />
      )}
    </>
  );
};
