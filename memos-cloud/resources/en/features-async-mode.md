# Async Mode

Async mode controls when MemOS processes submitted messages after `addMessage`.

## Modes

Use the `async_mode` parameter on `addMessage` when the API/SDK route supports it:

| Mode | Meaning | Use when |
| --- | --- | --- |
| Sync | Wait for memory processing before the request returns. | The next step must immediately search newly created memory. |
| Async, default | Return quickly and process in the background. | Most real-time chat products. |

## Notes

- Multimodal messages such as images and files require async processing because extraction takes longer.
- Processing status can be checked through `get/status` when available.
- In async mode, newly submitted memory may not appear in `searchMemory` immediately. It usually becomes searchable after a few seconds to tens of seconds.

## Verification Strategy

For first-time success tests:

1. Call `addMessage`.
2. Wait briefly if the route is async.
3. Call `searchMemory` with the same `user_id` and relevant query.
4. Treat a relevant search hit as success. A 2xx write response alone is not enough.
