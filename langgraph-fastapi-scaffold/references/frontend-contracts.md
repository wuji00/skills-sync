# Frontend Architecture & Contracts

## Technology Stack

| Package | Version | Purpose |
|---------|---------|---------|
| next | ≥16.2.6 | App Router, RSC |
| react | ≥19.0.0 | UI library |
| tailwindcss | ≥4.0.15 | Utility-first CSS |
| @langchain/langgraph-sdk | ≥1.5.3 | LangGraph API client + React hooks |
| @tanstack/react-query | ≥5.90.17 | Server state management |
| ai (Vercel AI SDK) | ≥6.0.33 | Chat UI primitives |
| lucide-react | ≥0.562.0 | Icons |
| class-variance-authority | ≥0.7.1 | Component variants |
| tailwind-merge + clsx | latest | Utility (`cn` helper) |
| zod | ≥3.24.2 | Schema validation |

## Directory Conventions

```
frontend/src/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx          # Root layout (providers)
│   ├── page.tsx            # Landing page
│   ├── login/              # Login page
│   ├── setup/              # First-boot admin setup
│   └── workspace/          # Main app
│       ├── layout.tsx      # Auth-gated layout
│       └── chats/[threadId]/  # Chat view
├── components/
│   ├── ai-elements/        # AI-specific UI primitives
│   └── ui/                 # Generic UI (shadcn)
├── core/                   # Business logic (no JSX)
│   ├── api/                # API client, fetcher
│   ├── auth/               # Auth provider, types
│   ├── config/             # Env-based config
│   ├── threads/            # Thread hooks, types
│   └── utils/              # uuid, etc.
└── lib/
    └── utils.ts            # cn() helper
```

## Component Contracts

### Conversation

```tsx
// Scroll-to-bottom chat shell using use-stick-to-bottom
<Conversation>
  <ConversationContent>
    {messages.map(m => <Message key={m.id}>...</Message>)}
  </ConversationContent>
  <ConversationScrollButton />
</Conversation>
```

### PromptInput

```tsx
// Compound component for the chat composer
<PromptInputProvider>
  <PromptInput>
    <PromptInputTextarea />
    <PromptInputAttachments />
    <PromptInputSubmit />
  </PromptInput>
</PromptInputProvider>
```

### Message

```tsx
// Message bubble primitives
<Message>
  <MessageContent>
    <MessageResponse>Markdown content</MessageResponse>
    <MessageActions>
      <MessageAction onClick={copy}>Copy</MessageAction>
    </MessageActions>
  </MessageContent>
</Message>
```

## API Client

### getAPIClient()

```ts
// Cached LangGraph SDK client with CSRF injection
import { getAPIClient } from "@/core/api/api-client";

const client = getAPIClient(); // or getAPIClient(isMock?: boolean)

// Wrapped methods handle CSRF, stream sanitization, terminal-run reconnect:
client.runs.stream(threadId, assistantId, payload);
client.runs.cancel(threadId, runId);
client.runs.joinStream(threadId, runId);
```

### fetch() wrapper

```ts
// Drop-in fetch replacement with CSRF + 401 redirect
import { fetch } from "@/core/api/fetcher";

const res = await fetch("/api/threads", {
  method: "POST",
  body: JSON.stringify({ metadata: {} }),
});
// Auto-injects X-CSRF-Token on POST/PUT/DELETE/PATCH
// Auto-redirects to /login on 401
```

## Core Hooks

### useThreadStream

```ts
// Primary streaming hook — combines useStream + history + optimistic UI
const {
  messages,       // Merged: history + live stream + optimistic
  isLoading,      // True while stream is active
  error,          // Stream error if any
  submit,         // (content: string) => void
  stop,           // Cancel current run
  regenerate,     // Re-run last message
  threadId,       // Current thread ID
} = useThreadStream({ threadId, assistantId: "chat_agent" });
```

### useThreadHistory

```ts
// Paginated archived message loader
const {
  messages,       // Archived messages (older than live stream)
  hasMore,        // Whether more pages exist
  loadMore,       // () => void — load next page
} = useThreadHistory({ threadId, beforeSeq: oldestLiveSeq });
```

### useInfiniteThreads

```ts
// Paginated thread list for sidebar
const {
  threads,        // Thread[] (merged pages)
  hasNextPage,    // Boolean
  fetchNextPage,  // () => void
  isFetching,     // Boolean
} = useInfiniteThreads({ limit: 20 });
```

### useCreateThread

```ts
// Mutation: POST /api/threads
const createThread = useCreateThread();
const threadId = await createThread.mutateAsync({ metadata: {} });
```

## TypeScript Types

### Thread

```ts
interface ThreadState {
  messages: Message[];
  // Extend with your state fields
}

interface ThreadContext {
  thread_id: string;
  model_name?: string;
  // Extend with your config fields
}

type AppThread = Thread<ThreadState>;
```

### Message

Uses `@langchain/langgraph-sdk` types:
```ts
type Message = AIMessage | HumanMessage | ToolMessage | SystemMessage;
```

### Run

```ts
interface Run {
  run_id: string;
  thread_id: string;
  assistant_id: string;
  status: "pending" | "running" | "success" | "error" | "timeout" | "interrupted";
  created_at: string;
  updated_at: string;
}
```

## Streaming and Optimistic UI

1. **Submit flow**: User message → optimistic `human` message appended → files upload → optimistic `ai` placeholder → `client.runs.stream()` starts
2. **Stream processing**: `useStream` from SDK manages SSE events → `thread.messages` updates reactively
3. **Message merging**: `mergeMessages(archivedHistory, liveMessages, optimisticMessages)` dedupes by id
4. **Terminal reconnect**: `joinStream` short-circuits if run is already finished (prevents infinite loading after page reload)
5. **Error handling**: SSE errors → `onError` callback → toast notification
