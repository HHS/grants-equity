import { useTranslations } from "next-intl";
import { useRef } from "react";
import { ModalRef, ModalToggleButton } from "@trussworks/react-uswds";

import { USWDSIcon } from "src/components/USWDSIcon";
import { LoginModal } from "./LoginModal";

export const LoginButtonModal = ({
  navLoginLinkText,
}: {
  navLoginLinkText: string;
}) => {
  const t = useTranslations("HeaderLoginModal");
  const modalRef = useRef<ModalRef>(null);

  return (
    <>
      <div className="usa-nav__primary margin-top-0 padding-top-2px text-no-wrap desktop:order-last margin-left-auto">
        <div className="usa-nav__primary-item border-0">
          <ModalToggleButton
            modalRef={modalRef}
            opener
            className="usa-nav__link text-ysaprimary font-sans-2xs display-flex text-normal border-0"
          >
            <USWDSIcon
              className="usa-icon margin-right-05 margin-left-neg-05"
              name="login"
              key="login-link-icon"
            />
            {navLoginLinkText}
          </ModalToggleButton>
        </div>
      </div>
      <LoginModal
        modalRef={modalRef as React.RefObject<ModalRef>}
        helpText={t("help")}
        buttonText={t("button")}
        closeText={t("close")}
        descriptionText={t("description")}
        titleText={t("title")}
      />
    </>
  );
};
