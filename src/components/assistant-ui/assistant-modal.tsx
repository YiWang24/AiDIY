import { MessageCircleIcon, RotateCcwIcon, SparklesIcon, XIcon } from "lucide-react";
import { type FC, forwardRef } from "react";
import { AssistantModalPrimitive } from "@assistant-ui/react";

import { Thread } from "src/components/assistant-ui/thread";

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
        className="aui-root aui-modal-content aidiy-modal z-[70]"
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
>((props, ref) => (
  <button
    type="button"
    ref={ref}
    aria-label="AiDIY Assistant"
    className="aidiy-trigger"
    {...props}
  >
    <span className="aidiy-trigger-icons">
      <MessageCircleIcon size={26} strokeWidth={2} />
      <SparklesIcon className="aidiy-trigger-sparkle" strokeWidth={2.4} />
    </span>
    <span className="aidiy-trigger-close">
      <XIcon size={24} strokeWidth={2.4} />
    </span>
  </button>
));

AssistantModalButton.displayName = "AssistantModalButton";

// ─── Modal header ──────────────────────────────────────────────────────────────

function ModalHeader({ onClear }: { onClear: () => void }) {
  return (
    <div className="aidiy-header">
      <div className="aidiy-header-left">
        <div className="aidiy-header-avatar">
          <SparklesIcon size={18} strokeWidth={2.2} />
        </div>
        <div>
          <div className="aidiy-header-title">AiDIY Assistant</div>
          <div className="aidiy-header-subtitle">
            Powered by RAG Knowledge Base
          </div>
        </div>
      </div>
      <button
        type="button"
        onClick={onClear}
        aria-label="New conversation"
        title="New conversation"
        className="aidiy-header-action"
      >
        <RotateCcwIcon size={16} strokeWidth={2} />
      </button>
    </div>
  );
}
