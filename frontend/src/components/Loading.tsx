import React, { JSX } from "react";

import Spinner from "src/components/Spinner";

export interface LoadingProps {
  message?: string;
}

export default function Loading({ message }: LoadingProps) {
  return (
    <div className="display-flex flex-align-center flex-justify-center margin-bottom-15 margin-top-15">
      <Spinner />
      <span
        className="font-body-2xl text-bold margin-left-2"
        data-testid="loading-message"
      >
        {message || "Loading"}...
      </span>
    </div>
  );
}
