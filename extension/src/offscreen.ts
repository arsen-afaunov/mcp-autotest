import { McpRequestSchema, RegisterCommandSchema, REQUEST_TYPES } from './types/protocol';
import type { z } from 'zod';

const WS_URL = `ws://${__BUILD_WS_HOST__}:${__BUILD_WS_PORT__}`;

let ws = new WebSocket(WS_URL);

// TODO: implement reconnect logic (ws.onclose + setTimeout)
// TODO: resend registration message after reconnect

type RegisterCommand = z.infer<typeof RegisterCommandSchema>;

ws.addEventListener('open', () => {
  const registerMsg: RegisterCommand = {
    id: 'register-1',
    type: REQUEST_TYPES.REGISTER,
    payload: null,
  };
  ws.send(JSON.stringify(registerMsg));
});

ws.addEventListener('message', async (event) => {
  let parsed: unknown;
  try {
    parsed = JSON.parse(event.data);
  } catch {
    return;
  }

  const result = McpRequestSchema.safeParse(parsed);
  if (!result.success) {
    return;
  }

  const request = result.data;
  console.log('[Offscreen] Received request:', request);

  try {
    await chrome.runtime.sendMessage({
      source: 'offscreen',
      type: 'command',
      payload: request,
    });
    console.log('[Offscreen] Sent to SW:', request);
  } catch (e) {
    console.error('[Offscreen] Failed to send to SW:', e);
  }
});
