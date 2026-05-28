import { MarkdownText } from "src/components/assistant-ui/markdown-text";
import {
  Reasoning,
  ReasoningContent,
  ReasoningRoot,
  ReasoningText,
  ReasoningTrigger,
} from "src/components/assistant-ui/reasoning";
import {
  ToolGroupContent,
  ToolGroupRoot,
  ToolGroupTrigger,
} from "src/components/assistant-ui/tool-group";
import { ToolFallback } from "src/components/assistant-ui/tool-fallback";
import { cn } from "src/lib/utils";
import {
  ActionBarPrimitive,
  AuiIf,
  BranchPickerPrimitive,
  ComposerPrimitive,
  ErrorPrimitive,
  getMcpAppFromToolPart,
  MessagePrimitive,
  ThreadPrimitive,
  useAuiState,
} from "@assistant-ui/react";
import {
  ArrowDownIcon,
  ArrowRightIcon,
  ArrowUpIcon,
  CheckIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CopyIcon,
  PencilIcon,
  RefreshCwIcon,
  SparklesIcon,
  SquareIcon,
} from "lucide-react";
import type { FC } from "react";

export const Thread: FC = () => {
  return (
    <ThreadPrimitive.Root className="aidiy-thread">
      <ThreadPrimitive.Viewport
        turnAnchor="bottom"
        data-slot="aui_thread-viewport"
        className="aidiy-viewport"
      >
        <div className="aidiy-thread-inner">
          <AuiIf condition={(s) => s.thread.isEmpty}>
            <ThreadWelcome />
          </AuiIf>

          <div
            data-slot="aui_message-group"
            className="aidiy-message-group"
          >
            <ThreadPrimitive.Messages>
              {() => <ThreadMessage />}
            </ThreadPrimitive.Messages>
          </div>

          <ThreadPrimitive.ViewportFooter className="aidiy-composer-wrap">
            <ThreadScrollToBottom />
            <Composer />
          </ThreadPrimitive.ViewportFooter>
        </div>
      </ThreadPrimitive.Viewport>
    </ThreadPrimitive.Root>
  );
};

const ThreadMessage: FC = () => {
  const role = useAuiState((s) => s.message.role);
  const isEditing = useAuiState((s) => s.message.composer.isEditing);

  if (isEditing) return <EditComposer />;
  if (role === "user") return <UserMessage />;
  return <AssistantMessage />;
};

const ThreadScrollToBottom: FC = () => {
  return (
    <ThreadPrimitive.ScrollToBottom asChild>
      <button
        type="button"
        aria-label="Scroll to bottom"
        title="Scroll to bottom"
        className="aidiy-scroll-bottom"
      >
        <ArrowDownIcon />
      </button>
    </ThreadPrimitive.ScrollToBottom>
  );
};

const AIDIY_SUGGESTIONS = [
  {
    label: "What is AgentOps and how does it work?",
    query: "What is AgentOps and how does it work?",
  },
  {
    label: "Explain the agent loop architecture",
    query: "Explain the agent loop architecture",
  },
  {
    label: "Patterns for agent orchestration?",
    query: "What are the patterns of agent orchestration?",
  },
] as const;

const ThreadWelcome: FC = () => {
  return (
    <div className="aidiy-welcome">
      <div className="aidiy-welcome-icon">
        <SparklesIcon size={30} strokeWidth={2} />
      </div>
      <div>
        <h2 className="aidiy-welcome-title">How can I help you?</h2>
        <p className="aidiy-welcome-subtitle">
          Ask me about AgentOps, orchestration patterns, or anything else in
          the docs.
        </p>
      </div>
      <div className="aidiy-suggestions">
        {AIDIY_SUGGESTIONS.map((s) => (
          <ThreadPrimitive.Suggestion
            key={s.query}
            prompt={s.query}
            method="replace"
            autoSend
            className="aidiy-suggestion"
          >
            <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {s.label}
            </span>
            <ArrowRightIcon size={14} strokeWidth={2} className="aidiy-suggestion-icon" />
          </ThreadPrimitive.Suggestion>
        ))}
      </div>
    </div>
  );
};

const Composer: FC = () => {
  return (
    <ComposerPrimitive.Root className="aui-composer-root">
      <ComposerPrimitive.AttachmentDropzone asChild>
        <div data-slot="aui_composer-shell" className="aidiy-composer-shell">
          <ComposerPrimitive.Input
            placeholder="Ask about the docs..."
            className="aidiy-composer-input"
            rows={1}
            autoFocus
            aria-label="Message input"
          />
          <ComposerAction />
        </div>
      </ComposerPrimitive.AttachmentDropzone>
    </ComposerPrimitive.Root>
  );
};

const ComposerAction: FC = () => {
  return (
    <div className="aidiy-composer-bar">
      <span className="aidiy-composer-hint">Press Enter to send</span>
      <AuiIf condition={(s) => !s.thread.isRunning}>
        <ComposerPrimitive.Send asChild>
          <button
            type="button"
            aria-label="Send message"
            title="Send message"
            className="aidiy-composer-send"
          >
            <ArrowUpIcon strokeWidth={2.4} />
          </button>
        </ComposerPrimitive.Send>
      </AuiIf>
      <AuiIf condition={(s) => s.thread.isRunning}>
        <ComposerPrimitive.Cancel asChild>
          <button
            type="button"
            aria-label="Stop generating"
            title="Stop generating"
            className="aidiy-composer-cancel"
          >
            <SquareIcon fill="currentColor" />
          </button>
        </ComposerPrimitive.Cancel>
      </AuiIf>
    </div>
  );
};

const MessageError: FC = () => {
  return (
    <MessagePrimitive.Error>
      <ErrorPrimitive.Root className="aui-message-error-root">
        <ErrorPrimitive.Message className="aui-message-error-message" />
      </ErrorPrimitive.Root>
    </MessagePrimitive.Error>
  );
};

const AssistantMessage: FC = () => {
  return (
    <MessagePrimitive.Root
      data-slot="aui_assistant-message-root"
      data-role="assistant"
      className="aidiy-msg-assistant"
    >
      <div
        data-slot="aui_assistant-message-content"
        className="aidiy-msg-assistant-body"
      >
        <MessagePrimitive.GroupedParts
          groupBy={(part) => {
            if (part.type === "reasoning")
              return ["group-chainOfThought", "group-reasoning"];
            if (part.type === "tool-call") {
              if (getMcpAppFromToolPart(part)) return null;
              return ["group-chainOfThought", "group-tool"];
            }
            return null;
          }}
        >
          {({ part, children }) => {
            switch (part.type) {
              case "group-chainOfThought":
                return <div data-slot="aui_chain-of-thought">{children}</div>;
              case "group-reasoning": {
                const running = part.status.type === "running";
                return (
                  <ReasoningRoot defaultOpen={running}>
                    <ReasoningTrigger active={running} />
                    <ReasoningContent aria-busy={running}>
                      <ReasoningText>{children}</ReasoningText>
                    </ReasoningContent>
                  </ReasoningRoot>
                );
              }
              case "group-tool":
                return (
                  <ToolGroupRoot variant="ghost">
                    <ToolGroupTrigger
                      count={part.indices.length}
                      active={part.status.type === "running"}
                    />
                    <ToolGroupContent>{children}</ToolGroupContent>
                  </ToolGroupRoot>
                );
              case "text":
                return <MarkdownText />;
              case "reasoning":
                return <Reasoning {...part} />;
              case "tool-call":
                return part.toolUI ?? <ToolFallback {...part} />;
              default:
                return null;
            }
          }}
        </MessagePrimitive.GroupedParts>
        <MessageError />
      </div>

      <div
        data-slot="aui_assistant-message-footer"
        className="aidiy-msg-actionbar"
      >
        <BranchPicker />
        <AssistantActionBar />
      </div>
    </MessagePrimitive.Root>
  );
};

const AssistantActionBar: FC = () => {
  return (
    <ActionBarPrimitive.Root
      hideWhenRunning
      autohide="not-last"
      className="aui-assistant-action-bar-root flex items-center gap-1"
    >
      <ActionBarPrimitive.Copy asChild>
        <button type="button" aria-label="Copy" title="Copy" className="aidiy-icon-btn">
          <AuiIf condition={(s) => s.message.isCopied}>
            <CheckIcon />
          </AuiIf>
          <AuiIf condition={(s) => !s.message.isCopied}>
            <CopyIcon />
          </AuiIf>
        </button>
      </ActionBarPrimitive.Copy>
      <ActionBarPrimitive.Reload asChild>
        <button type="button" aria-label="Refresh" title="Refresh" className="aidiy-icon-btn">
          <RefreshCwIcon />
        </button>
      </ActionBarPrimitive.Reload>
    </ActionBarPrimitive.Root>
  );
};

const UserMessage: FC = () => {
  return (
    <MessagePrimitive.Root
      data-slot="aui_user-message-root"
      className="aidiy-msg-user"
      data-role="user"
    >
      <div className="aidiy-msg-user-bubble">
        <MessagePrimitive.Parts />
      </div>
      <UserActionBar />
    </MessagePrimitive.Root>
  );
};

const UserActionBar: FC = () => {
  return (
    <ActionBarPrimitive.Root
      hideWhenRunning
      autohide="not-last"
      className="aui-user-action-bar-root"
      style={{ display: "none" }}
    >
      <ActionBarPrimitive.Edit asChild>
        <button type="button" aria-label="Edit" title="Edit" className="aidiy-icon-btn">
          <PencilIcon />
        </button>
      </ActionBarPrimitive.Edit>
    </ActionBarPrimitive.Root>
  );
};

const EditComposer: FC = () => {
  return (
    <MessagePrimitive.Root
      data-slot="aui_edit-composer-wrapper"
      className="aidiy-msg-user"
    >
      <ComposerPrimitive.Root className="aidiy-composer-shell" style={{ maxWidth: "85%" }}>
        <ComposerPrimitive.Input
          className="aidiy-composer-input"
          autoFocus
        />
        <div className="aidiy-composer-bar" style={{ justifyContent: "flex-end" }}>
          <ComposerPrimitive.Cancel asChild>
            <button type="button" className="aidiy-icon-btn" style={{ width: "auto", padding: "4px 10px", fontSize: 12 }}>
              Cancel
            </button>
          </ComposerPrimitive.Cancel>
          <ComposerPrimitive.Send asChild>
            <button type="button" className="aidiy-composer-send" style={{ width: "auto", height: "auto", padding: "4px 10px", fontSize: 12, borderRadius: 999 }}>
              Update
            </button>
          </ComposerPrimitive.Send>
        </div>
      </ComposerPrimitive.Root>
    </MessagePrimitive.Root>
  );
};

const BranchPicker: FC<BranchPickerPrimitive.Root.Props> = ({
  className,
  ...rest
}) => {
  return (
    <BranchPickerPrimitive.Root
      hideWhenSingleBranch
      className={cn("aui-branch-picker-root inline-flex items-center text-xs", className)}
      {...rest}
    >
      <BranchPickerPrimitive.Previous asChild>
        <button type="button" aria-label="Previous" title="Previous" className="aidiy-icon-btn">
          <ChevronLeftIcon />
        </button>
      </BranchPickerPrimitive.Previous>
      <span className="aui-branch-picker-state" style={{ fontWeight: 500 }}>
        <BranchPickerPrimitive.Number /> / <BranchPickerPrimitive.Count />
      </span>
      <BranchPickerPrimitive.Next asChild>
        <button type="button" aria-label="Next" title="Next" className="aidiy-icon-btn">
          <ChevronRightIcon />
        </button>
      </BranchPickerPrimitive.Next>
    </BranchPickerPrimitive.Root>
  );
};
