import clsx from "clsx";

import SpriteSVG from "public/img/uswds-sprite.svg";

interface IconProps {
  name: string;
  className?: string;
  height?: string;
}

// eslint-disable-next-line @typescript-eslint/no-unsafe-member-access
const sprite_uri = SpriteSVG.src as string;

// height prop doesn't seem to work
// do we want to go all in on this rather than the trussworks component?
export function USWDSIcon(props: IconProps) {
  return (
    <svg
      className={clsx("usa-icon", props.className)}
      aria-hidden="true"
      height={props.height}
      role="img"
    >
      <use href={`${sprite_uri}#${props.name}`}></use>
    </svg>
  );
}
