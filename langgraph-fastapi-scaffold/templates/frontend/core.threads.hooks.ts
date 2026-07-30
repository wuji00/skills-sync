/**
 * Thread Hooks
 * ============
 * Extracted from deer-flow's hooks.ts. Key patterns:
 *
 * 1. useThreadStream — primary hook combining useStream + history + optimistic UI
 * 2. useThreadHistory — paginated archived message loading
 * 3. useCreateThread — mutation for creating new threads
 * 4. useInfiniteThreads — paginated thread list for sidebar
 * 5. Message merging helpers for optimistic UI consistency
 */

"use client";

import { useCallback, useMemo, useRef } from "react";
import { useStream } from "@langchain/langgraph-sdk/react";
import {
  useInfiniteQuery,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { getAPIClient } from "../api/api-client";
import {
  createThread,
  deleteThread,
  getThreadHistory,
  getThreadState,
  listMessages,
  listThreads,
  renameThread,
} from "./api";
import type { ThreadState } from "./types";

// ============================================================================
// useThreadStream — Main streaming hook
// ============================================================================

interface UseThreadStreamOptions {
  threadId: string;
  assistantId?: string;
}

export function useThreadStream({
  threadId,
  assistantId = "chat_agent",
}: UseThreadStreamOptions) {
  const client = getAPIClient();
  const queryClient = useQueryClient();

  const stream = useStream<ThreadState>({
    client,
    threadId,
    assistantId,
    reconnectOnMount: true,
  });

  const messages = useMemo(() => {
    return stream.messages ?? [];
  }, [stream.messages]);

  const submit = useCallback(
    async (content: string) => {
      await stream.submit(
        { messages: [{ type: "human", content }] },
        {
          streamMode: ["messages", "values"],
          config: { configurable: { thread_id: threadId } },
        },
      );
    },
    [stream, threadId],
  );

  const stop = useCallback(() => {
    stream.stop();
  }, [stream]);

  return {
    messages,
    isLoading: stream.isLoading,
    error: stream.error,
    submit,
    stop,
    threadId,
    stream,
  };
}

// ============================================================================
// useThreadHistory — Archived messages
// ============================================================================

interface UseThreadHistoryOptions {
  threadId: string;
}

export function useThreadHistory({ threadId }: UseThreadHistoryOptions) {
  return useQuery({
    queryKey: ["thread", "history", threadId],
    queryFn: () => getThreadHistory(threadId, { limit: 100 }),
    enabled: !!threadId,
  });
}

// ============================================================================
// useCreateThread
// ============================================================================

export function useCreateThread() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (metadata?: Record<string, unknown>) =>
      createThread({ metadata }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["threads"] });
    },
  });
}

// ============================================================================
// useInfiniteThreads — Paginated thread list
// ============================================================================

export function useInfiniteThreads(limit = 20) {
  return useInfiniteQuery({
    queryKey: ["threads", "infinite", limit],
    queryFn: ({ pageParam = 0 }) =>
      listThreads({ limit, offset: pageParam as number }),
    getNextPageParam: (lastPage, allPages) => {
      if (!lastPage || lastPage.length < limit) return undefined;
      return allPages.length * limit;
    },
    initialPageParam: 0,
  });
}

// ============================================================================
// useDeleteThread
// ============================================================================

export function useDeleteThread() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (threadId: string) => deleteThread(threadId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["threads"] });
    },
  });
}

// ============================================================================
// useRenameThread
// ============================================================================

export function useRenameThread() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      threadId,
      title,
    }: {
      threadId: string;
      title: string;
    }) => renameThread(threadId, title),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["threads"] });
    },
  });
}

// ============================================================================
// Message Merging Helpers
// ============================================================================

export function mergeMessages(
  archived: any[],
  live: any[],
  optimistic: any[] = [],
): any[] {
  const seen = new Set<string>();
  const result: any[] = [];

  for (const msg of [...archived, ...live, ...optimistic]) {
    const key = msg.id ?? msg.tool_call_id ?? JSON.stringify(msg);
    if (!seen.has(key)) {
      seen.add(key);
      result.push(msg);
    }
  }

  return result;
}
