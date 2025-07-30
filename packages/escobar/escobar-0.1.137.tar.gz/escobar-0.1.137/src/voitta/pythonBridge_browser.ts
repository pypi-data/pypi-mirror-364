export var voittal_call_log = {}
export const stopped_messages = {}

import { integer } from "yaml-language-server";
import { compressString, encodeBase64 } from "../utils/compression"

export function generateUUID() {
  const timestamp = Date.now().toString(16);
  return 'M-xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  }) + '-' + timestamp;
}

// Interface for pending requests
interface PendingRequest {
  resolve: (value: any) => void;
  reject: (reason?: any) => void;
  timeout: any;
}

// Map to store pending requests by call_id
const pendingRequests: Map<string, PendingRequest> = new Map();

// Default timeout for requests in milliseconds
const DEFAULT_TIMEOUT = 1000 * 60 * 60;

// Function registry type definitions
interface FunctionRegistryEntry {
  fn: Function;
  obj: object | null;
  isAsync: boolean;
  returns: boolean;
}

type FunctionRegistry = {
  [key: string]: FunctionRegistryEntry;
};

// Function registry to store registered functions
const registry: FunctionRegistry = {};

let ws: WebSocket | null = null;
let isConnected = false;
export var connectionPromise: Promise<void> | null = null;

// Keepalive pinger variables
let keepaliveInterval: any = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000; // 3 seconds
const PING_INTERVAL = 50000; // 50 seconds (10 seconds before nginx 60s timeout)

// Custom events for callPython execution state
export const PYTHON_CALL_EVENTS = {
  START: 'escobar-python-call-start',
  END: 'escobar-python-call-end',
  STOP: 'escobar-stop-event'
};

export function get_ws() {
  return ws;
}

function chunked_transmit(data: string, chunk_size: number = 8096): void {
  const wire_id = generateUUID();
  const totalChunks = Math.ceil(data.length / chunk_size);

  for (let chunk_id = 0; chunk_id < totalChunks; chunk_id++) {
    const start = chunk_id * chunk_size;
    const end = Math.min(start + chunk_size, data.length);
    const chunk_data = data.substring(start, end);
    const is_last = chunk_id === totalChunks - 1;

    const chunk_message = {
      message_type: 'chunk',
      wire_id: wire_id,
      chunk_id: chunk_id,
      is_last: is_last,
      data: chunk_data,
      total_chunks: totalChunks
    };

    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(chunk_message));
    } else {
      throw new Error('WebSocket not connected');
    }
  }
}


/**
 * Start the keepalive pinger to prevent nginx timeout using native WebSocket ping/pong
 */
export function startKeepalivePinger(): void {
  // Clear any existing pinger first
  if (keepaliveInterval) {
    clearInterval(keepaliveInterval);
    keepaliveInterval = null;
  }

  console.log('🏓 Starting native WebSocket keepalive pinger');

  // Send ping every 50 seconds (10 seconds before nginx 60s timeout)
  keepaliveInterval = setInterval(() => {
    // Check connection state before pinging
    if (!ws || ws.readyState !== WebSocket.OPEN || !isConnected) {
      console.log('🏓 Connection lost, attempting reconnection...');
      stopKeepalivePinger();

      reconnectWebSocket().then(() => {
        console.log('🏓 Reconnection successful, pinger restarted');
      }).catch((error) => {
        console.error('🏓 Reconnection failed:', error);
      });
      return;
    }

    try {
      // Use native WebSocket ping frame - no application-level message needed
      (ws as any).ping?.(); // Some WebSocket implementations have ping() method
      console.log('🏓 Sent native WebSocket ping frame');
      reconnectAttempts = 0; // Reset reconnect attempts on successful ping
    } catch (error) {
      console.log('🏓 Native ping not supported, using alternative keepalive method');

      // Fallback: send a minimal data frame to keep connection alive
      try {
        ws.send(''); // Send empty string as keepalive
        console.log('🏓 Sent keepalive data frame');
        reconnectAttempts = 0;
      } catch (sendError) {
        console.log('🏓 Keepalive failed, connection may be down:', sendError);
        // Connection is likely dead, let the next cycle handle reconnection
      }
    }
  }, PING_INTERVAL);
}

/**
 * Stop the keepalive pinger
 */
export function stopKeepalivePinger(): void {
  if (keepaliveInterval) {
    clearInterval(keepaliveInterval);
    keepaliveInterval = null;
    console.log('🏓 Keepalive pinger stopped');
  }
}

/**
 * Reconnect WebSocket without full initialization
 */
export async function reconnectWebSocket(): Promise<void> {
  if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
    console.error('🔄 Max reconnection attempts reached, giving up');
    throw new Error('Max reconnection attempts reached');
  }

  reconnectAttempts++;
  console.log(`🔄 Attempting WebSocket reconnection (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);

  // Stop any existing pinger
  stopKeepalivePinger();

  // Close existing connection if it exists
  if (ws) {
    ws.close();
    ws = null;
    isConnected = false;
  }

  // Wait before reconnecting
  await new Promise(resolve => setTimeout(resolve, RECONNECT_DELAY));

  // Get current settings for URL
  const currentSettings = (window as any).escobarCurrentSettings;
  const serverUrl = currentSettings?.serverUrl || '/ws';

  // Re-establish connection using existing initPythonBridge
  await initPythonBridge(serverUrl);

  console.log('🔄 WebSocket reconnection complete');
}

/**
 * Resolve WebSocket URL for JupyterHub environment
 * @param url - The URL to resolve (can be relative or absolute)
 * @returns Resolved URL with proper JupyterHub user path if needed
 */
function resolveWebSocketURL(url: string): string {
  console.log(`##>>## Original URL: ${url}`);

  // If it's already an absolute URL (starts with ws:// or wss://), return as-is
  if (url.startsWith('ws://') || url.startsWith('wss://')) {
    console.log(`##>>## Absolute URL, using as-is: ${url}`);
    return url;
  }

  // Check if we're in JupyterHub environment
  const currentPath = window.location.pathname;
  const hubUserMatch = currentPath.match(/^\/user\/([^\/]+)\//);

  if (hubUserMatch) {
    // In JupyterHub - construct user-specific URL
    const userPath = hubUserMatch[0]; // "/user/roman.semein@gmail.com/"
    const resolvedPath = userPath.slice(0, -1) + url; // "/user/roman.semein@gmail.com/ws"

    // Construct full WebSocket URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const fullURL = `${protocol}//${host}${resolvedPath}`;

    console.log(`##>>## JupyterHub detected, resolved URL: ${fullURL}`);
    console.log(`##>>## User path: ${userPath}`);
    console.log(`##>>## Resolved path: ${resolvedPath}`);

    return fullURL;
  } else {
    // Standalone JupyterLab - construct normal URL
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const fullURL = `${protocol}//${host}${url}`;

    console.log(`##>>## Standalone JupyterLab, resolved URL: ${fullURL}`);

    return fullURL;
  }
}

let stopEventListenerAdded = false;
let stopRequested = false;

/**
 * Initializes the WebSocket connection to the Python server.
 * If a connection attempt is already in progress or the connection is active, it returns that promise.
 *
 * @param url - The WebSocket URL (default: "ws://127.0.0.1:8777/ws")
 * @returns A Promise that resolves when the connection is successfully established.
 */
export function initPythonBridge(url: string = "ws://127.0.0.1:8777/ws"): Promise<void> {
  console.log("Entering initPythonBridge");
  // If already connected, return a resolved promise.
  if (ws && isConnected && ws.readyState === WebSocket.OPEN) {
    return Promise.resolve();
  }

  if (!stopEventListenerAdded) {
    window.addEventListener(PYTHON_CALL_EVENTS.STOP, handleStopEvent);
    stopEventListenerAdded = true;
  }


  // If a connection attempt is in progress, return that promise.

  /*
  if (connectionPromise) {
    return connectionPromise;
  }
  */

  connectionPromise = new Promise<void>((resolve, reject) => {
    // Always resolve the URL for JupyterHub environment (never connect directly to bonnieUrl)
    let resolvedURL = resolveWebSocketURL(url);

    // Check if we need to add bonnieUrl as query parameter for backend proxy
    const currentSettings = (window as any).escobarCurrentSettings;
    if (currentSettings?.bonnieUrl && url.startsWith('/')) {
      console.log(`>>> Adding bonnieUrl as proxy target: ${currentSettings.bonnieUrl}`);

      // Add bonnieUrl as query parameter for backend to use as proxy target
      const separator = resolvedURL.includes('?') ? '&' : '?';
      resolvedURL += `${separator}bonnie_url=${encodeURIComponent(currentSettings.bonnieUrl)}`;

      console.log(`>>> Final URL with bonnieUrl parameter: ${resolvedURL}`);
    } else {
      console.log(">>> No bonnieUrl parameter needed");
    }

    console.log(">>> Connecting to " + resolvedURL);
    ws = new WebSocket(resolvedURL);

    ws.addEventListener('open', (event) => {
      isConnected = true;
      reconnectAttempts = 0; // Reset reconnect attempts on successful connection

      // Start keepalive pinger
      startKeepalivePinger();

      // Connection established successfully
      resolve();
      connectionPromise = null;
    });


    ws.addEventListener('error', (event) => {

      console.error("Error connecting to Python server:", event);
      reject(event);
      connectionPromise = null;
    });

    ws.addEventListener('close', (event) => {
      isConnected = false;

      // Stop keepalive pinger
      stopKeepalivePinger();

      // Auto-reconnect after a delay (unless intentionally closed)
      if (event.code !== 1000 && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) { // 1000 = normal closure
        console.log(`🔄 Connection lost (code: ${event.code}), attempting reconnection in ${RECONNECT_DELAY}ms...`);
        setTimeout(async () => {
          try {
            await reconnectWebSocket();
            console.log('🔄 Auto-reconnection successful');
          } catch (error) {
            console.error('🔄 Auto-reconnection failed:', error);
          }
        }, RECONNECT_DELAY);
      } else if (event.code === 1000) {
        console.log('🔄 WebSocket closed normally');
      } else {
        console.log('🔄 Max reconnection attempts reached, giving up');
      }
    });

    // Add pong event listener for native WebSocket ping/pong
    (ws as any).addEventListener?.('pong', () => {
      console.log('🏓 Received native WebSocket pong response');
      reconnectAttempts = 0; // Reset reconnect attempts on successful ping/pong
    });

    ws.addEventListener('message', async (event: any) => {
      //const messageStr = typeof data === 'string' ? data : data.toString('utf-8');
      const messageStr = event.data;

      // Skip processing empty messages (keepalive frames)
      if (!messageStr || messageStr === '') {
        console.log('🏓 Received keepalive response (empty message)');
        return;
      }

      try {
        var jsonData: any = messageStr;
        if (typeof messageStr === 'string') {
          //console.log("parsing:", typeof messageStr, messageStr);
          jsonData = JSON.parse(messageStr);
        }

        let message_type = jsonData.message_type;

        if (message_type === "response") {
          // Check if this is a response to a pending request

          const call_id = jsonData.call_id;
          const finish_reason = jsonData.finish_reason;
          console.log(`Finish Reason: ${finish_reason}`);

          // Received response for call_id

          if (call_id && pendingRequests.has(call_id)) {
            // Found pending request for this call_id
            // Get the pending request
            const pendingRequest = pendingRequests.get(call_id)!;

            // Check if this is a final response or intermediate response
            const isFinalResponse = !finish_reason || finish_reason !== "tool_calls";

            if (isFinalResponse) {
              // Final response - clean up and resolve
              clearTimeout(pendingRequest.timeout);
              pendingRequests.delete(call_id);

              // Extract the response data
              const responseData = jsonData.data || jsonData.response || jsonData;

              // Pass finish_reason to the resolve callback for stop button control
              pendingRequest.resolve({ ...responseData, finish_reason });
            } else {
              // Intermediate response with tool_calls - handle but don't resolve yet
              console.log(`Intermediate response with finish_reason: ${finish_reason} - keeping request pending`);

              // TODO: Handle intermediate responses - could call a separate handler here
              // For now, we just log and keep the request pending for the final response
            }
          } else if (registry['handleResponse']) {
            // Using registered handleResponse function
            // Extract the response data
            const responseData = {
              ...(jsonData.data || jsonData.response || jsonData),
              function: "handleResponse",
              params: { value: jsonData.value || "-- value not found in response --" }
            };
            // Call the registered response handler
            callRegisteredFunction(responseData);
          } else {
            console.warn("Received response with no matching request or handler");
          }
        } else if (message_type === "request") {
          let function_name = jsonData.function;
          let msg_call_id = jsonData.__msg_call_id__;
          let call_id = jsonData.call_id;
          if (stopped_messages[msg_call_id] != undefined) {
            // Message ignored because it was stopped
            const entry = registry[function_name];
            if (entry.returns) {
              bridgeReturn(call_id, "__stopped__")
            }
            return;
          }

          let params = jsonData.params;

          //console.log(`<r> ${function_name}  ${jsonData.call_id} ${params.id} ${params.msg_call_id}`)

          // Check if the function exists in the registry
          if (!registry[function_name]) {
            console.error(`Function "${function_name}" not found in registry`);
            return;
          }

          let is_async = registry[function_name].isAsync;
          if (is_async) {
            let result = await callRegisteredFunctionAsync(jsonData);
          } else {
            let result = callRegisteredFunction(jsonData);
          }
        }
      } catch (error) {
        console.error("Error parsing JSON message:", error);
      }
    });
  });

  return connectionPromise;
}


function handleStopEvent() {
  stopRequested = true;

  // Clear all pending requests
  for (const [call_id, request] of pendingRequests.entries()) {
    clearTimeout(request.timeout);
    const error = new Error('Operation stopped by user');
    (error as any).stop = true;
    request.reject(error);
    pendingRequests.delete(call_id);
  }

  // Reset the flag after a short delay
  setTimeout(() => {
    stopRequested = false;
  }, 100);
}



/**
 * Sends a message to the Python server and waits for a response.
 * If the connection is not yet established, it attempts to initialize it.
 * Dispatches events when the call starts and ends to allow UI elements to respond.
 *
 * @param message - The typed message object to send.
 * @param timeoutMs - Optional timeout in milliseconds (default: 30000)
 * @param waitForResponse - Whether to wait for a response
 * @param showStopButton - Whether to show the stop button for this operation (default: false)
 * @returns A Promise that resolves with the response data when received.
 */
export async function callPython(message: import('../types/protocol').ProtocolMessage,
  timeoutMs: number = DEFAULT_TIMEOUT,
  waitForResponse: boolean = true,
  showStopButton: boolean = false
): Promise<any> {
  const timestamp = new Date().toISOString();

  // === FUNCTION ENTRY LOGGING ===
  console.log(`[callPython] ${timestamp} Function entry with parameters:`, {
    messageType: message.message_type,
    method: (message as any).method || 'unknown',
    timeoutMs,
    waitForResponse,
    showStopButton,
    originalMessage: message
  });

  // Only dispatch start event for operations that wait for responses AND should show the stop button
  if (waitForResponse && showStopButton) {
    console.log(`[callPython] ${timestamp} Dispatching START event for stop button`);
    window.dispatchEvent(new CustomEvent(PYTHON_CALL_EVENTS.START));
  }

  // === CONNECTION STATE VALIDATION ===
  const wsState = ws ? ws.readyState : 'null';
  const wsStateNames = ['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'];
  const wsStateName = ws ? wsStateNames[ws.readyState] || 'UNKNOWN' : 'NULL';

  console.log(`[callPython] ${timestamp} Connection state check:`, {
    wsExists: !!ws,
    isConnected,
    wsReadyState: wsState,
    wsStateName,
    connectionOK: ws && isConnected && ws.readyState === WebSocket.OPEN
  });

  if (!ws || !isConnected || ws.readyState !== WebSocket.OPEN) {
    console.warn(`[callPython] ${timestamp} Connection not ready - continuing anyway`);
  }

  // === MESSAGE PROCESSING ===
  // Generate a unique call ID
  const call_id = generateUUID();
  console.log(`[callPython] ${timestamp} Generated call_id: ${call_id}`);

  let user_id = '';
  let session_id = '';

  // Get username from global variable set by the chat widget
  if ((window as any).escobarUsername) {
    user_id = (window as any).escobarUsername;
    console.log(`[callPython] ${timestamp} Retrieved user_id from global: ${user_id}`);
  } else {
    // Fallback to default if global variable not available
    console.warn(`[callPython] ${timestamp} Username not available from global variable, using default`);
    user_id = 'VoittaDefaultUser';
  }

  // Get session_id from the message if it's a chat-related message
  if ('chatID' in message) {
    session_id = (message as any).chatID;
    console.log(`[callPython] ${timestamp} Retrieved session_id from message: ${session_id}`);
  } else {
    // Fallback to a default session ID
    session_id = 'temp-session';
    console.log(`[callPython] ${timestamp} Using fallback session_id: ${session_id}`);
  }

  // Enrich the message with metadata - ensure user_id and session_id are always sent
  const enrichedMessage = {
    ...message,
    user_id: user_id,
    session_id: session_id,
    call_id: call_id,
    msg_call_id: message.call_id || call_id,
    message_type: 'request' as const
  };

  console.log(`[callPython] ${timestamp} Message enrichment complete:`, {
    originalKeys: Object.keys(message),
    enrichedKeys: Object.keys(enrichedMessage),
    addedMetadata: {
      user_id,
      session_id,
      call_id,
      msg_call_id: enrichedMessage.msg_call_id
    }
  });

  // === JSON.STRINGIFY DIAGNOSTIC LOGGING ===
  console.log(`[callPython] ${timestamp} Pre-stringify analysis:`, {
    enrichedMessageKeys: Object.keys(enrichedMessage),
    enrichedMessageOwnKeys: Object.getOwnPropertyNames(enrichedMessage),
    enrichedMessageEntries: Object.entries(enrichedMessage).map(([key, value]) => [
      key,
      {
        type: typeof value,
        isFunction: typeof value === 'function',
        isUndefined: value === undefined,
        isNull: value === null,
        constructor: value?.constructor?.name || 'N/A',
        value: typeof value === 'function' ? '[Function]' : value
      }
    ]),
    originalMessageDescriptors: Object.getOwnPropertyDescriptors(message),
    enrichedMessageDescriptors: Object.getOwnPropertyDescriptors(enrichedMessage)
  });

  // Test what gets lost in stringification
  const testStringified = JSON.parse(JSON.stringify(enrichedMessage));
  const allKeys = Object.getOwnPropertyNames(enrichedMessage);
  const stringifiedKeys = Object.keys(testStringified);
  const lostKeys = allKeys.filter(key => !(key in testStringified));
  const lostKeyDetails = lostKeys.map(key => ({
    key,
    value: enrichedMessage[key],
    type: typeof enrichedMessage[key],
    isFunction: typeof enrichedMessage[key] === 'function',
    isUndefined: enrichedMessage[key] === undefined,
    descriptor: Object.getOwnPropertyDescriptor(enrichedMessage, key)
  }));

  console.log(`[callPython] ${timestamp} JSON.stringify analysis:`, {
    totalKeysBeforeStringify: allKeys.length,
    totalKeysAfterStringify: stringifiedKeys.length,
    lostKeysCount: lostKeys.length,
    lostKeys: lostKeys,
    lostKeyDetails: lostKeyDetails,
    keptKeys: stringifiedKeys,
    originalSize: JSON.stringify(enrichedMessage).length,
    testStringifiedSize: JSON.stringify(testStringified).length
  });

  // Send directly - no double JSON encoding!
  const payload = JSON.stringify(enrichedMessage);

  console.log(`[callPython] Payload size: ${payload.length}`)

  console.log(`[callPython] ${timestamp} Payload prepared:`, {
    payloadLength: payload.length,
    payloadPreview: payload.substring(0, 200) + (payload.length > 200 ? '...' : ''),
    fullPayload: enrichedMessage,
    stringifiedPayloadPreview: payload.substring(0, 500) + (payload.length > 500 ? '...' : '')
  });

  // === PROMISE LIFECYCLE LOGGING ===
  console.log(`[callPython] ${timestamp} Creating promise for call_id: ${call_id}`);

  // Return a promise that resolves when the response is received
  return new Promise((resolve, reject) => {
    console.log(`[callPython] ${timestamp} Promise executor started for call_id: ${call_id}`);

    // === WEBSOCKET OPERATIONS ===
    // If the connection is now open, send the message.
    if (ws && isConnected && ws.readyState === WebSocket.OPEN) {
      console.log(`[callPython] ${timestamp} WebSocket ready, proceeding with send for call_id: ${call_id}`);

      // Set up a timeout to reject the promise if no response is received
      console.log(`[callPython] ${timestamp} Setting up timeout (${timeoutMs}ms) for call_id: ${call_id}`);
      const timeout = setTimeout(() => {
        console.error(`[callPython] ${timestamp} TIMEOUT reached for call_id: ${call_id} after ${timeoutMs}ms`);
        console.log(`[callPython] ${timestamp} Cleaning up timeout - removing from pending requests: ${call_id}`);

        // Remove from pending requests
        const wasInPending = pendingRequests.has(call_id);
        pendingRequests.delete(call_id);
        console.log(`[callPython] ${timestamp} Removed from pending (was present: ${wasInPending}), remaining pending: ${pendingRequests.size}`);

        // Only dispatch end event on timeout if we were waiting for a response AND showing stop button
        if (waitForResponse && showStopButton) {
          console.log(`[callPython] ${timestamp} Dispatching END event due to timeout for call_id: ${call_id}`);
          window.dispatchEvent(new CustomEvent(PYTHON_CALL_EVENTS.END));
        }

        reject(new Error(`Request timed out after ${timeoutMs}ms`));
      }, timeoutMs);

      // Store the promise callbacks and timeout in the pending requests map
      if (waitForResponse) {
        console.log(`[callPython] ${timestamp} Registering pending request for call_id: ${call_id} (waitForResponse=true)`);

        pendingRequests.set(call_id, {
          resolve: (value: any) => {
            console.log(`[callPython] ${timestamp} RESOLVE called for call_id: ${call_id}`, {
              valueKeys: value ? Object.keys(value) : 'null',
              finishReason: value?.finish_reason,
              value
            });

            // Only dispatch END event if showStopButton is true AND finish_reason is NOT "tool_calls"
            // Hide stop button when: finish_reason is undefined/null OR finish_reason !== "tool_calls"
            const shouldHideStopButton = !value.finish_reason || value.finish_reason !== "tool_calls";

            if (shouldHideStopButton && showStopButton) {
              console.log(`[callPython] ${timestamp} Dispatching END event due to normal completion for call_id: ${call_id}`);
              window.dispatchEvent(new CustomEvent(PYTHON_CALL_EVENTS.END));
            } else if (shouldHideStopButton && !showStopButton) {
              console.log(`[callPython] ${timestamp} Normal completion but no stop button was shown for call_id: ${call_id}`);
            } else {
              console.log(`[callPython] ${timestamp} Tool calls continue - keeping stop button visible for call_id: ${call_id}`);
            }

            // TODO: Handle multiple responses in sequence - may need to track conversation state
            // TODO: Consider implementing a conversation state machine for complex tool call flows
            // TODO: May need to differentiate between intermediate and final responses

            resolve(value);
          },
          reject: (reason?: any) => {
            console.error(`[callPython] ${timestamp} REJECT called for call_id: ${call_id}`, {
              reason,
              reasonType: typeof reason,
              isError: reason instanceof Error,
              errorMessage: reason instanceof Error ? reason.message : 'N/A',
              stack: reason instanceof Error ? reason.stack : 'N/A'
            });

            // Only hide stop button on errors if it was shown
            if (showStopButton) {
              console.log(`[callPython] ${timestamp} Dispatching END event due to error for call_id: ${call_id}`);
              window.dispatchEvent(new CustomEvent(PYTHON_CALL_EVENTS.END));
            }
            reject(reason);
          },
          timeout
        });

        console.log(`[callPython] ${timestamp} Pending request registered. Total pending: ${pendingRequests.size}`);
      } else {
        console.log(`[callPython] ${timestamp} Not waiting for response (waitForResponse=false), cleaning up immediately for call_id: ${call_id}`);
        pendingRequests.delete(call_id);
        // No stop button events for operations that don't wait for responses
      }

      // Send the message
      try {
        console.log(`[callPython] ${timestamp} Attempting WebSocket send for call_id: ${call_id}`);

        //ws.send(payload);
        chunked_transmit(payload);

      } catch (sendError) {
        console.error(`[callPython] ${timestamp} WebSocket send FAILED for call_id: ${call_id}`, {
          error: sendError,
          errorMessage: sendError instanceof Error ? sendError.message : 'Unknown error',
          wsReadyState: ws.readyState,
          wsStateName: wsStateNames[ws.readyState] || 'UNKNOWN'
        });

        // Clean up on send failure
        clearTimeout(timeout);
        pendingRequests.delete(call_id);
        if (showStopButton) {
          console.log(`[callPython] ${timestamp} Dispatching END event due to send failure for call_id: ${call_id}`);
          window.dispatchEvent(new CustomEvent(PYTHON_CALL_EVENTS.END));
        }
        reject(sendError);
      }
    } else {
      // === ERROR CONDITIONS ===
      console.error(`[callPython] ${timestamp} WebSocket not ready for call_id: ${call_id}`, {
        wsExists: !!ws,
        isConnected,
        wsReadyState: ws ? ws.readyState : 'null',
        wsStateName,
        errorCondition: 'WebSocket not connected after attempting to reconnect'
      });

      // Only dispatch end event on immediate rejection if stop button was shown
      if (showStopButton) {
        console.log(`[callPython] ${timestamp} Dispatching END event due to connection failure for call_id: ${call_id}`);
        window.dispatchEvent(new CustomEvent(PYTHON_CALL_EVENTS.END));
      }
      reject(new Error("Cannot send message. WebSocket is not connected after attempting to reconnect."));
    }
  });
}





/**
 * Registers a function in the registry to be called later.
 * 
 * @param name - The name to register the function under
 * @param isAsync - Whether the function is asynchronous
 * @param fn - The function to register
 */
export function registerFunction(name: string, isAsync: boolean,
  fn: Function, obj: object | null = null, returns: boolean = false): void {

  if (registry[name]) {
    console.warn(`Function "${name}" already exists in the registry. Overwriting`);
  }

  registry[name] = {
    fn,
    obj,
    isAsync,
    returns
  };
}


export function bridgeReturn(call_id: string, value: any) {
  // Returning value to bridge

  const payload = {
    call_id: call_id,
    message_type: "response"
  }

  if (typeof value == "string") {
    payload["value"] = value;
  } else {
    payload["binary_value"] = value;
  }

  if (ws !== null) {
    if (typeof payload == "string") {
      chunked_transmit(payload)
      //ws.send(payload);
    } else {
      //ws.send(JSON.stringify(payload));
      chunked_transmit(JSON.stringify(payload));
    }
  } else {
    console.error("WebSocket is null. Cannot send message.");
  }
}


/**
 * Calls a registered function by name with the provided arguments.
 * 
 * @param name - The name of the registered function to call
 * @param args - The arguments to pass to the function
 * @returns The result of the function call, or a Promise if the function is async
 * @throws Error if the function is not found in the registry
 */

export async function callRegisteredFunctionAsync(jsonData: any): Promise<any> {
  const call_id = jsonData["call_id"] || "";

  const function_name = jsonData["function"] || "";
  var params = jsonData["params"] || {};
  const partial = params["partial"] || false;

  var param = params["param"] || {};
  if (partial) {
    param = params["text"] || "";
  }

  const entry = registry[function_name];

  if (!entry) {
    throw new Error(`Function "${function_name}" not found in registry`);
  }

  try {
    var result;
    if ((function_name == "diffToFile") || (function_name == "writeToFile") ||
      (function_name == "insertExecuteCell") || (function_name == "editExecuteCell")
    ) {
      result = await entry.fn.call(entry.obj, params, false, call_id);
    } else {
      result = await entry.fn.call(entry.obj, params);
    }
    if (entry.returns) {
      bridgeReturn(call_id, result);
    }
  } catch (error) {
    console.error(`Error calling function "${function_name}":`, error);
    throw error;
  }
  voittal_call_log[call_id] = true;
}


export function callRegisteredFunction(jsonData: any): any {
  const call_id = jsonData["call_id"] || "";
  const function_name = jsonData["function"] || "";
  var params = jsonData["params"] || {};
  const partial = params["partial"] || false;
  const msg_call_id = params["msg_call_id"] // effectively references the single query session

  if ((function_name != "tool_say") && (function_name != "say")) {
    const ours = true;
  }

  var param = params["param"] || {};
  if (partial) {
    param = params["text"] || "";
  }

  const entry = registry[function_name];

  if (!entry) {
    throw new Error(`Function "${function_name}" not found in registry`);
  }
  try {
    let result = entry.fn.call(entry.obj, params);
    if (entry.returns) {
      bridgeReturn(call_id, result);
    }
  } catch (error) {
    console.error(`Error calling function "${function_name}":`, error);
    throw error;
  }
}

/**
 * Gets the registry of functions.
 * 
 * @returns The function registry with an added call method for each function
 */
export function getFunctionRegistry(): FunctionRegistry & {
  [key: string]: FunctionRegistryEntry & {
    call: (name: string, args: any) => any
  }
} {
  // Create a proxy to add a 'call' method to each registry entry
  return new Proxy(registry, {
    get(target, prop) {
      if (typeof prop === 'string' && prop in target) {
        // Add a call method to the registry entry
        const entry = target[prop];
        return {
          ...entry,
          call: (name: string, args: any) => {
            try {
              return entry.fn.call(null, args);
            } catch (error) {
              console.error(`Error calling function "${name}":`, error);
              throw error;
            }
          }
        };
      }
      return Reflect.get(target, prop);
    }
  }) as any;
}
