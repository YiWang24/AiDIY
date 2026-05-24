import { MessageCircleIcon, RotateCcwIcon, SparklesIcon, XIcon } from "lucide-react";
import { type FC, forwardRef } from "react";
import { AssistantModalPrimitive } from "@assistant-ui/react";

import { Thread } from "src/components/assistant-ui/thread";

// ─── Shared trigger button classes ────────────────────────────────────────────
const TRIGGER_CLS =
  "group size-full rounded-full bg-gradient-to-br from-indigo-500 to-sky-500 text-white shadow-lg shadow-indigo-500/20 ring-1 ring-white/10 transition-all duration-300 hover:scale-110 hover:shadow-indigo-500/40 data-[state=open]:rotate-90";

// ─── AssistantModal ────────────────────────────────────────────────────────────

interface AssistantModalProps {
  onClear: () => void;
}

export const AssistantModal: FC<AssistantModalProps> = ({ onClear }) => {
  return (
    <AssistantModalPrimitive.Root>
      <AssistantModalPrimitive.Anchor className="aui-root aui-modal-anchor fixed bottom-6 end-6 z-[60] size-14">
        <AssistantModalPrimitive.Trigger asChild>
          <AssistantModalButton />
        </AssistantModalPrimitive.Trigger>
      </AssistantModalPrimitive.Anchor>
      <AssistantModalPrimitive.Content
        sideOffset={16}
        className="aui-root aui-modal-content z-[70] flex h-[720px] max-h-[85vh] w-[440px] max-w-[95vw] flex-col overflow-hidden rounded-[2.5rem] border border-neutral-200 bg-white shadow-2xl dark:border-neutral-800 dark:bg-neutral-950"
      >
        <ModalHeader onClear={onClear} />
        <Thread />
      </AssistantModalPrimitive.Content>
    </AssistantModalPrimitive.Root>
  );
};

// ─── Trigger button ────────────────────────────────────────────────────────────

type AssistantModalButtonProps = { "data-state"?: "open" | "closed" };

const AssistantModalButton = forwardRef<
  HTMLButtonElement,
  AssistantModalButtonProps
>(({ "data-state": _state, ...rest }, ref) => (
  <button
    type="button"
    ref={ref}
    aria-label="AiDIY Assistant"
    className={TRIGGER_CLS}
    {...rest}
  >
    <div className="relative flex size-full items-center justify-center transition-transform group-data-[state=open]:opacity-0">
      <MessageCircleIcon className="size-8 fill-white/20" />
      <SparklesIcon className="absolute top-2.5 right-2.5 size-4 fill-white" />
    </div>
    <XIcon className="absolute inset-0 m-auto size-6 opacity-0 transition-opacity group-data-[state=open]:opacity-100" />
  </button>
));

AssistantModalButton.displayName = "AssistantModalButton";

// ─── Modal header ──────────────────────────────────────────────────────────────

function ModalHeader({ onClear }: { onClear: () => void }) {
  return (
    <div className="flex shrink-0 items-center justify-between border-b border-neutral-100 bg-white/80 px-6 py-4 backdrop-blur-md dark:border-neutral-800 dark:bg-neutral-950/80">
      <div className="flex items-center gap-3">
        <div className="flex size-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-sky-500 text-white shadow-sm">
          <SparklesIcon className="size-4.5" />
        </div>
        <div className="leading-tight">
          <div className="text-sm font-bold tracking-tight text-neutral-900 dark:text-neutral-100">
            AiDIY Assistant
          </div>
          <div className="text-[11px] font-medium text-neutral-500 dark:text-neutral-400">
            Powered by RAG Knowledge Base
          </div>
        </div>
      </div>
      <button
        type="button"
        onClick={onClear}
        aria-label="New conversation"
        className="rounded-lg p-2 text-neutral-400 transition-colors hover:bg-neutral-100 hover:text-neutral-900 dark:hover:bg-neutral-800 dark:hover:text-neutral-100"
      >
        <RotateCcwIcon className="size-4" />
      </button>
    </div>
  );
}
