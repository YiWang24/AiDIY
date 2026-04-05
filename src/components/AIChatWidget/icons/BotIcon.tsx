import React from "react";

export default function BotIcon({
  size = 24,
  className,
}: {
  size?: number;
  className?: string;
}): JSX.Element {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <rect x="4" y="7" width="16" height="13" rx="3" />
      <path d="M9 7V4.5a1.5 1.5 0 0 1 1.5-1.5h3a1.5 1.5 0 0 1 1.5 1.5V7" />
      <circle cx="9.5" cy="12.5" r="1.5" fill="currentColor" stroke="none" />
      <circle cx="14.5" cy="12.5" r="1.5" fill="currentColor" stroke="none" />
      <path d="M10 16.5h4" />
    </svg>
  );
}
