/**
 * LangGraph SDK API Client
 * ========================
 * Extracted from deer-flow's api-client.ts. Key patterns:
 *
 * 1. Cached client singleton (getAPIClient)
 * 2. CSRF header injection via onRequest hook
 * 3. Stream options sanitization (remove unsupported modes)
 * 4. Terminal-run reconnect short-circuit (prevents infinite loading)
 * 5. Cancel 409 handling for already-finished runs
 *
 * Usage:
 *   import { getAPIClient } from "@/core/api/api-client";
 *   const client = getAPIClient();
 *   const stream = client.runs.stream(threadId, "chat_agent", payload);
 */

"use client";

import { Client as LangGraphClient } from "@langchain/langgraph-sdk/client";

import { getLangGraphBaseURL } from "../config";
import { isStateChangingMethod, readCsrfCookie } from "./fetcher";
import { sanitizeRunStreamOptions } from "./stream-mode";

// ============================================================================
// CSRF Injection
// ============================================================================

function injectCsrfHeader(_url: URL, init: RequestInit): RequestInit {
  if (!isStateChangingMethod(init.method ?? "GET")) {
    return init;
  }
  const token = readCsrfCookie();
  if (!token) return init;
  const headers = new Headers(init.headers);
  if (!headers.has("X-CSRF-Token")) {
    headers.set("X-CSRF-Token", token);
  }
  return { ...init, headers };
}

// ============================================================================
// Terminal Run Handling
// ============================================================================

const TERMINAL_RUN_STATUSES = new Set([
  "success",
  "error",
  "timeout",
  "interrupted",
]);

async function shouldSkipReconnect(
  client: LangGraphClient,
  threadId: string,
  runId: string,
): Promise<boolean> {
  try {
    const run = await client.runs.get(threadId, runId);
    return TERMINAL_RUN_STATUSES.has(run.status);
  } catch {
    return false;
  }
}

// ============================================================================
// Client Factory
// ============================================================================

function createClient(): LangGraphClient {
  const apiUrl = getLangGraphBaseURL();
  const client = new LangGraphClient({
    apiUrl,
    onRequest: injectCsrfHeader,
  });

  // --- Wrap stream to sanitize options ---
  const originalRunStream = client.runs.stream.bind(client.runs);
  client.runs.stream = ((threadId, assistantId, payload) =>
    originalRunStream(
      threadId,
      assistantId,
      sanitizeRunStreamOptions(payload),
    )) as typeof client.runs.stream;

  // --- Wrap cancel to swallow 409 on already-finished runs ---
  const originalCancel = client.runs.cancel.bind(client.runs);
  client.runs.cancel = (async (threadId, runId, wait, action, options) => {
    try {
      return await originalCancel(threadId, runId, wait, action, options);
    } catch (error: any) {
      if (
        error?.status === 409 &&
        error?.message?.includes("is not cancellable")
      ) {
        return; // Run already finished — cancel is a no-op
      }
      throw error;
    }
  }) as typeof client.runs.cancel;

  // --- Wrap joinStream to short-circuit terminal runs ---
  const originalJoinStream = client.runs.joinStream.bind(client.runs);
  client.runs.joinStream = async function* (threadId, runId, options) {
    if (threadId && (await shouldSkipReconnect(client, threadId, runId))) {
      return; // Already finished — nothing to rejoin
    }
    yield* originalJoinStream(
      threadId,
      runId,
      sanitizeRunStreamOptions(options),
    );
  } as typeof client.runs.joinStream;

  return client;
}

// ============================================================================
// Singleton Accessor
// ============================================================================

let _client: LangGraphClient | null = null;

export function getAPIClient(): LangGraphClient {
  if (!_client) {
    _client = createClient();
  }
  return _client;
}
