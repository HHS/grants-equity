import clsx from "clsx";

import Spinner from "./Spinner";
import { USWDSIcon } from "./USWDSIcon";

interface SaveButtonProps {
  onClick?: () => void;
  children?: React.ReactNode;
  saved: boolean;
  loading: boolean;
  defaultText: string;
  savedText: string;
  loadingText: string;
}

const SaveButton: React.FC<SaveButtonProps> = ({
  onClick,
  defaultText,
  savedText,
  saved = false,
  loading = false,
  loadingText,
}) => {
  const text = saved ? savedText : defaultText;
  return (
    <button
      className={clsx("simpler-save-button usa-button usa-button--outline", {
        "simpler-save-button--saved": saved,
        "simpler-save-button--loading": loading,
      })}
      onClick={onClick}
      disabled={loading}
    >
      {loading ? (
        <>
          <Spinner /> {loadingText}
        </>
      ) : (
        <>
          <USWDSIcon name={saved ? "star" : "star_outline"} /> {text}
        </>
      )}
    </button>
  );
};

export default SaveButton;
