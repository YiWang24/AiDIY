# 设计文档：使用 assistant-ui CLI 组件重构 AIChatWidget

**日期**：2026-05-23  
**项目**：AiDIY  
**作者**：Claude Code  

---

## 背景

当前 `src/components/AIChatWidget/index.tsx` 共 460 行，完全基于 `@assistant-ui/react` 的底层 primitives 手动拼装 Chat UI。这种做法需要自行处理所有样式和交互细节，维护成本高，且缺少 assistant-ui 上层组件自带的功能（消息编辑、复制、分支切换等）。

**目标**：用 `npx shadcn@latest add` 生成的 pre-built 组件替换手动拼装的实现，减少自维护代码量，获得更完整的功能。

---

## 方案：Option A — CLI 生成 + 最小化定制

### 核心原则

- 通过 CLI 生成标准组件，放入 `src/components/assistant-ui/`
- 只在必要处定制（AiDIY 品牌、欢迎页、KbSearch 工具 UI、弹窗样式）
- `AIChatWidget/index.tsx` 只保留会话管理 + 运行时初始化逻辑

---

## 文件结构

### 新增文件（CLI 生成）

```
src/components/assistant-ui/
  thread.tsx              ← 生成后定制欢迎页 / 建议问题
  assistant-modal.tsx     ← 生成后定制触发按钮 / 弹窗尺寸 / Header
  kb-search-tool.tsx      ← 手写，从旧代码提取 KbSearch 工具渲染器
  markdown-text.tsx       ← 生成，不改动
  tooltip-icon-button.tsx ← 生成，不改动
  tool-fallback.tsx       ← 生成，不改动
  tool-group.tsx          ← 生成，不改动
  attachment.tsx          ← 生成，不改动
  reasoning.tsx           ← 生成，不改动
```

### 修改文件

| 文件 | 改动 |
|---|---|
| `src/components/AIChatWidget/index.tsx` | 460 行 → ~80 行，只留会话管理 + 运行时 |
| `src/components/ui/dialog.tsx` | CLI 覆盖更新（更新版本） |
| `src/components/ui/collapsible.tsx` | CLI 覆盖更新 |

### 保持不变

- `src/components/AIChatWidget/hooks/useSessionId.ts`
- `src/components/AIChatWidget/types.ts`
- `api/chat.ts`、`api/messages.ts` 等后端文件

---

## 组件架构

```
AIChatWidget
 ├─ 加载桩按钮（历史记录加载前显示，样式与真实按钮一致）
 └─ ChatWidgetInner（历史记录加载完成后挂载）
     └─ AssistantRuntimeProvider
         ├─ KbSearchToolUI（不渲染，仅注册 kb_search 工具渲染器）
         └─ AssistantModal（接收 onClear prop）
             ├─ 触发按钮：AssistantModalButton（靛蓝渐变，56×56px）
             └─ 弹窗内容：h-[720px] max-h-[85vh] w-[440px] max-w-[95vw]
                 ├─ Header（"AiDIY Assistant" + RAG 副标题 + 清除按钮）
                 └─ Thread
                     ├─ ThreadWelcome（定制文案 + 3 条固定建议）
                     ├─ UserMessage
                     ├─ AssistantMessage（含 kb_search 工具渲染 + MarkdownText）
                     ├─ Composer（发送框）
                     ├─ ActionBar（复制 / 重新生成 / 导出）
                     └─ BranchPicker（多分支切换）
```

---

## 各文件定制说明

### `thread.tsx` 定制点

1. **ThreadWelcome**：替换文案
   - 标题：`How can I help you?`
   - 副标题：`Ask me about AgentOps, orchestration patterns, or anything else in the docs.`
   - 图标：SparklesIcon（靛蓝渐变）

2. **ThreadSuggestions**：改为固定 3 条，不用 `ThreadPrimitive.Suggestions`
   ```
   - "What is AgentOps and how does it work?"
   - "Explain the agent loop architecture"
   - "What are the patterns of agent orchestration?"
   ```

3. 其余部分（UserMessage、AssistantMessage、Composer、ActionBar、BranchPicker）保持生成内容不变。

### `assistant-modal.tsx` 定制点

1. **AssistantModalButton**：替换为靛蓝渐变按钮（沿用现有 `TRIGGER_CLS` 样式）
   - `MessageCircleIcon` + `SparklesIcon` 叠加效果
   - 打开时旋转 90° 显示 `XIcon`

2. **弹窗尺寸**：`h-[720px] max-h-[85vh] w-[440px] max-w-[95vw] rounded-[2.5rem]`

3. **弹窗内容**：在 `<Thread />` 前插入 `<Header onClear={onClear} />`

4. **接受 props**：`AssistantModal` 接收 `{ onClear: () => void; defaultOpen?: boolean }`

### `kb-search-tool.tsx`

从旧 `index.tsx` 提取，保持逻辑不变：
- `KbSearchToolUI = makeAssistantToolUI({ toolName: "kb_search", render: ... })`
- 渲染：运行中显示"Searching"脉冲图标；完成后显示可折叠的来源列表
- `dedupeChunks` 工具函数随文件迁移
- `toDocLink` 工具函数也随文件迁移

### `AIChatWidget/index.tsx` 精简后结构

```tsx
// ~80 行
export default function AIChatWidget() {
  // 1. 会话 ID 管理
  // 2. 加载历史记录（fetch /api/messages）
  // 3. 加载中：显示桩按钮
  // 4. 加载完成：挂载 ChatWidgetInner
}

function ChatWidgetInner({ sessionId, initialMessages, onStartNew, defaultOpen }) {
  // 1. AssistantChatTransport（带 x-aidiy-session header）
  // 2. useChatRuntime
  // 3. 渲染 AssistantRuntimeProvider + KbSearchToolUI + AssistantModal
}
```

---

## 新增依赖

CLI 安装时自动处理：
- `class-variance-authority`（按钮变体）
- `tw-shimmer`（加载动画）
- `zustand`（assistant-ui 内部状态）

---

## 新增功能（生成组件自带）

| 功能 | 说明 |
|---|---|
| 消息编辑 | 用户点击消息旁的编辑按钮可修改已发送内容 |
| 复制回答 | ActionBar 提供一键复制 |
| 重新生成 | ActionBar 提供重新生成按钮 |
| 导出 Markdown | ActionBar 的"更多"菜单提供导出 |
| 分支切换 | BranchPicker 支持在多个回复版本间切换 |
| 滚动到底部 | 自动显示/隐藏的滚动按钮 |

---

## 不改动的内容

- 后端 API（`api/chat.ts`、`api/messages.ts`、`api/sessions.ts`）
- `useSessionId` hook
- `types.ts`（`RetrievedChunk`、`RetrievalToolOutput`）
- `AssistantChatTransport` 配置（`x-aidiy-session` header）
- `useChatRuntime` 初始化方式
- 历史记录加载逻辑

---

## 风险

| 风险 | 应对 |
|---|---|
| CLI 覆盖 `dialog.tsx` / `collapsible.tsx` | 提前 diff 确认差异，生成后验证 |
| 生成组件的 CSS 变量与现有 Tailwind 冲突 | 用 `aui-root` 作用域隔离，实测验证 |
| `SuggestionPrimitive` API 与旧 `ThreadPrimitive.Suggestion` 不兼容 | 改用固定建议数组 + `ThreadPrimitive.Suggestion`，不依赖新 API |
