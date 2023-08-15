import { Alert as USWDSAlert } from "@trussworks/react-uswds";

type Props = {
  type: "success" | "warning" | "error" | "info";
  children: React.ReactNode;
};

const Alert = ({ type, children }: Props) => {
  return (
    <USWDSAlert className="margin-bottom-1 border-left-0" type={type} headingLevel="h4" slim>
      {children}
    </USWDSAlert>
  );
};

export default Alert;
