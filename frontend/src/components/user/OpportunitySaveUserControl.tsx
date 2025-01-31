"use client";

import { useUser } from "src/services/auth/useUser";

import { useTranslations } from "next-intl";
import { useRef } from "react";
import { ModalRef, ModalToggleButton } from "@trussworks/react-uswds";

import { LoginModal } from "src/components/LoginModal";
import SaveButton from "src/components/SaveButton";
import { USWDSIcon } from "src/components/USWDSIcon";

export const OpportunitySaveUserControl = () => {
  const t = useTranslations("OpportunityListing");
  const modalRef = useRef<ModalRef>(null);

  const { user } = useUser();
  const loading = false;
  const saved =  false;

  return (
    <>
      {!user?.token && (
        <>
          <ModalToggleButton
            modalRef={modalRef}
            opener
            className="simpler-save-button usa-button usa-button--outline"
          >
            <USWDSIcon name="star_outline" />
            {t("save_button.save")}
          </ModalToggleButton>
          <LoginModal
            modalRef={modalRef as React.RefObject<ModalRef>}
            helpText={t("save_login_modal.help")}
            buttonText={t("save_login_modal.button")}
            closeText={t("save_login_modal.close")}
            descriptionText={t("save_login_modal.description")}
            titleText={t("save_login_modal.title")}
          />
        </>
      )}
      {!!user?.token && (
        <SaveButton
          defaultText={t("save_button.save")}
          savedText={t("save_button.saved")}
          loadingText={t("save_button.loading")}
          saved={saved}
          loading={loading}
        />
      )}
    </>
  );
};
