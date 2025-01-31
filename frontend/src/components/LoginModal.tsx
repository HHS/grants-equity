"use-client";

import { RefObject } from "react";
import {
  ButtonGroup,
  Modal,
  ModalFooter,
  ModalHeading,
  ModalRef,
  ModalToggleButton,
} from "@trussworks/react-uswds";

import { USWDSIcon } from "src/components/USWDSIcon";

export const LOGIN_URL = "/api/auth/login";

export const LoginModal = ({
  modalRef,
  helpText,
  titleText,
  descriptionText,
  buttonText,
  closeText,
}: {
  modalRef: RefObject<ModalRef>;
  helpText: string;
  titleText: string;
  descriptionText: string;
  buttonText: string;
  closeText: string;
}) => {
  return (
    <Modal
      ref={modalRef}
      forceAction
      aria-labelledby="login-modal-heading"
      aria-describedby="login-modal-description"
      id="login-modal"
      renderToPortal={false}
    >
      <ModalHeading id="login-modal-heading">{titleText}</ModalHeading>
      <div className="usa-prose">
        <p>{helpText}</p>
        <p className="font-sans-2xs margin-y-4">{descriptionText}</p>
      </div>
      <ModalFooter>
        <ButtonGroup>
          <a href={LOGIN_URL} key="login-link" className="usa-button">
            {buttonText}
            <USWDSIcon
              className="usa-icon margin-right-05 margin-left-neg-05"
              name="launch"
              key="login-gov-link-icon"
            />
          </a>
          <ModalToggleButton
            modalRef={modalRef}
            closer
            unstyled
            className="padding-105 text-center"
          >
            {closeText}
          </ModalToggleButton>
        </ButtonGroup>
      </ModalFooter>
    </Modal>
  );
};
