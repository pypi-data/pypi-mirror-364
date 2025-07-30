import { JupyterFrontEnd } from '@jupyterlab/application';
import { app, functions } from './jupyter_integrations';
import { streamingState } from "./jupyter_integrations";
import { CodeMirrorEditor, jupyterTheme, jupyterHighlightStyle } from '@jupyterlab/codemirror';
import { Widget } from '@lumino/widgets';

// Import necessary CodeMirror modules
import { StateEffect, StateField, EditorState, Text, Extension, Compartment } from '@codemirror/state';
import { Decoration, EditorView, ViewPlugin } from '@codemirror/view';
import { MergeView } from '@codemirror/merge';
import { LanguageSupport, syntaxHighlighting } from '@codemirror/language';

// Import language support modules
import { python } from '@codemirror/lang-python';
import { javascript } from '@codemirror/lang-javascript';
import { json } from '@codemirror/lang-json';
import { markdown } from '@codemirror/lang-markdown';
import { html } from '@codemirror/lang-html';
import { css } from '@codemirror/lang-css';

// Import diff utilities from the llm-diff-utils module



function unescapeString(input: string): string {
    // Return early for null, undefined, or empty string
    if (input === null || input === undefined) {
        return '';
    }

    if (input === '') {
        return '';
    }

    return input.replace(/\\"/g, '"')
        .replace(/\\'/g, "'")
        .replace(/\\\\/g, '\\')
        .replace(/\\n/g, '\n')
        .replace(/\\t/g, '\t')
        .replace(/\\r/g, '\r')
        .replace(/\\b/g, '\b')
        .replace(/\\f/g, '\f')
        .replace(/\\v/g, '\v')
        .replace(/\\0/g, '\0')
        .replace(/\\x([0-9A-Fa-f]{2})/g, (_, hex) =>
            String.fromCharCode(parseInt(hex, 16))
        )
        .replace(/\\u([0-9A-Fa-f]{4})/g, (_, hex) =>
            String.fromCharCode(parseInt(hex, 16))
        )
        .replace(/\\u\{([0-9A-Fa-f]+)\}/g, (_, hex) =>
            String.fromCodePoint(parseInt(hex, 16))
        )
        .replace(/\\([0-3][0-7]{2}|[0-7]{1,2})/g, (_, octal) =>
            String.fromCharCode(parseInt(octal, 8))
        );
}

// Helper function to extract source code from Jupytext notebook structure
function extractSourceFromNotebook(notebookContent: any): string {
    if (!notebookContent || typeof notebookContent !== 'object') {
        return '';
    }

    // Handle Jupytext notebook structure
    if (notebookContent.cells && Array.isArray(notebookContent.cells)) {
        console.log('Extracting source from Jupytext notebook cells');
        return notebookContent.cells
            .map((cell: any) => {
                if (cell.source) {
                    let cellSource = '';
                    // Handle both string and array formats
                    if (typeof cell.source === 'string') {
                        cellSource = cell.source;
                    } else if (Array.isArray(cell.source)) {
                        cellSource = cell.source.join('');
                    }

                    // Ensure cell source ends with a newline for proper separation
                    if (cellSource && !cellSource.endsWith('\n')) {
                        cellSource += '\n';
                    }

                    return cellSource;
                }
                return '';
            })
            .filter(source => source.trim().length > 0) // Remove empty cells
            .join('\n'); // Join cells with additional newline for separation
    }

    // If it's not a recognizable notebook structure, stringify it
    return JSON.stringify(notebookContent, null, 2);
}

// Enhanced validation and safety functions
function validateFileContent(fileContent: any, filePath: string): string {
    if (!fileContent) {
        throw new Error(`File content is null or undefined for ${filePath}`);
    }

    // Handle different content formats based on JupyterLab's IModel interface
    if (fileContent.type === 'directory') {
        throw new Error(`Cannot process directory as file: ${filePath}`);
    }

    // Use mimetype as primary indicator (following JupyterLab's own logic)
    const mimetype = fileContent.mimetype || '';
    const fileType = fileContent.type || '';
    const format = fileContent.format || '';

    // PRIORITY 1: Handle text files based on mimetype (most reliable indicator)
    // This must come BEFORE checking fileType to handle Jupytext files correctly
    if (mimetype.startsWith('text/') || mimetype === 'application/x-python-code') {
        if (typeof fileContent.content === 'string') {
            return fileContent.content;
        } else if (typeof fileContent.content === 'object' && format === 'json') {
            // This is a Jupytext file - extract source from notebook cells
            try {
                const extractedSource = extractSourceFromNotebook(fileContent.content);
                return extractedSource;
            } catch (err) {
                console.error(`Failed to extract source from Jupytext file ${filePath}:`, err.message);
                throw new Error(`Failed to extract source from Jupytext file ${filePath}: ${err.message}`);
            }
        } else {
            throw new Error(`Text file ${filePath} has unexpected content type: ${typeof fileContent.content}`);
        }
    }

    // PRIORITY 1.5: Special case for Jupytext files with null mimetype
    // This handles the case where JupyterLab returns mimetype: null for Jupytext files
    if (fileType === 'notebook' &&
        format === 'json' &&
        (!mimetype || mimetype === '') &&
        filePath.endsWith('.py') &&
        typeof fileContent.content === 'object' &&
        fileContent.content?.metadata?.jupytext) {

        console.log(`✅ DETECTED JUPYTEXT FILE with null mimetype: ${filePath}`);

        try {
            const extractedSource = extractSourceFromNotebook(fileContent.content);
            return extractedSource;
        } catch (err) {
            console.error(`Failed to extract source from Jupytext file with null mimetype ${filePath}:`, err.message);
            throw new Error(`Failed to extract source from Jupytext file ${filePath}: ${err.message}`);
        }
    }

    // PRIORITY 2: Handle actual notebook files (only if mimetype is not text-based and not Jupytext)
    if ((fileType === 'notebook' || mimetype === 'application/x-ipynb+json') &&
        !mimetype.startsWith('text/') &&
        !(filePath.endsWith('.py') && fileContent.content?.metadata?.jupytext)) {

        if (fileContent.content === null) {
            return '';
        }
        try {
            const jsonString = JSON.stringify(fileContent.content, null, 2);
            return jsonString;
        } catch (err) {
            console.error(`Failed to stringify notebook content for ${filePath}:`, err.message);
            throw new Error(`Failed to stringify notebook content for ${filePath}: ${err.message}`);
        }
    }

    // Handle base64 encoded files
    if (format === 'base64' && typeof fileContent.content === 'string') {
        console.log(`Processing base64 file ${filePath}`);
        try {
            return atob(fileContent.content);
        } catch (err) {
            throw new Error(`Failed to decode base64 content for ${filePath}: ${err.message}`);
        }
    }

    // Handle standard text files (format: 'text', content: string)
    if (format === 'text' && typeof fileContent.content === 'string') {
        console.log(`Processing text file ${filePath} by format`);
        return fileContent.content;
    }

    // Handle edge cases where format might be null but content is string
    if (typeof fileContent.content === 'string') {
        console.log(`Processing file ${filePath} with string content (format: ${format})`);
        return fileContent.content;
    }

    // Handle case where content is object but we haven't matched any specific case
    if (typeof fileContent.content === 'object' && fileContent.content !== null) {
        console.warn(`Unexpected object content for ${filePath}, attempting to extract or stringify`);

        // Try to extract source if it looks like a notebook
        if (fileContent.content.cells) {
            try {
                return extractSourceFromNotebook(fileContent.content);
            } catch (err) {
                console.warn(`Failed to extract source, falling back to stringify: ${err.message}`);
            }
        }

        // Fall back to stringifying
        try {
            return JSON.stringify(fileContent.content, null, 2);
        } catch (err) {
            throw new Error(`Failed to process object content for ${filePath}: ${err.message}`);
        }
    }

    // If we get here, we have an unexpected content structure
    const errorDetails = {
        filePath,
        type: fileType,
        format: format,
        mimetype: mimetype,
        contentType: typeof fileContent.content,
        contentValue: fileContent.content
    };

    console.error('Unexpected content structure:', errorDetails);
    throw new Error(
        `Unexpected content structure for ${filePath}: ` +
        `type=${fileType}, format=${format}, mimetype=${mimetype}, ` +
        `contentType=${typeof fileContent.content}. ` +
        `Unable to determine how to process this file.`
    );
}

function ensureString(value: any, context: string): string {
    if (value === null || value === undefined) {
        console.warn(`${context}: value is null/undefined, using empty string`);
        return '';
    }
    if (typeof value !== 'string') {
        console.warn(`${context}: value is not a string (${typeof value}), converting`);
        return String(value);
    }
    return value;
}

async function readFileWithRetry(contents: any, filePath: string, maxRetries = 3): Promise<any> {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            const result = await contents.get(filePath);

            if (!result) {
                throw new Error(`File read returned null/undefined on attempt ${attempt}`);
            }

            return result;
        } catch (err) {
            if (attempt === maxRetries) {
                throw new Error(`Failed to read file ${filePath} after ${maxRetries} attempts: ${err.message}`);
            }

            // Progressive delay between retries
            const delay = 100 * attempt;
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
}

function createMergeViewSafely(originalContent: string, diffResult: string, languageExtensions: any[], filePath: string): MergeView {
    // Validate inputs with detailed logging
    const safeOriginal = ensureString(originalContent, `originalContent for ${filePath}`);
    const safeDiff = ensureString(diffResult, `diffResult for ${filePath}`);

    console.log(`Creating MergeView for ${filePath}:`, {
        originalLength: safeOriginal.length,
        diffLength: safeDiff.length,
        originalType: typeof safeOriginal,
        diffType: typeof safeDiff,
        hasExtensions: Array.isArray(languageExtensions),
        extensionsCount: languageExtensions?.length
    });

    try {
        const mergeView = new MergeView({
            a: {
                doc: safeOriginal,
                extensions: languageExtensions
            },
            b: {
                doc: safeDiff,
                extensions: languageExtensions
            },
            highlightChanges: true
        });

        console.log(`MergeView created successfully for ${filePath}`);
        return mergeView;
    } catch (err) {
        const errorDetails = {
            filePath,
            originalType: typeof safeOriginal,
            diffType: typeof safeDiff,
            originalLength: safeOriginal?.length,
            diffLength: safeDiff?.length,
            originalSample: safeOriginal?.substring(0, 100),
            diffSample: safeDiff?.substring(0, 100),
            error: err.message,
            stack: err.stack
        };

        console.error("MergeView creation failed:", errorDetails);
        throw new Error(`MergeView creation failed for ${filePath}: ${err.message}`);
    }
}

function safeStringReplace(content: string, search: string, replace: string, context: string): string {
    const safeContent = ensureString(content, `content for ${context}`);
    const safeSearch = ensureString(search, `search string for ${context}`);
    const safeReplace = ensureString(replace, `replace string for ${context}`);

    console.log(`🔍 DEBUGGING STRING REPLACEMENT for ${context}:`);
    console.log(`📝 Search string: "${safeSearch}" (length: ${safeSearch.length})`);
    console.log(`📝 Search char codes:`, Array.from(safeSearch).map(c => c.charCodeAt(0)));
    console.log(`🔄 Replace string: "${safeReplace}" (length: ${safeReplace.length})`);
    console.log(`📄 Content length: ${safeContent.length}`);

    try {
        if (safeSearch === '+') {
            return safeContent + unescapeString(safeReplace);
        } else if (safeSearch === '-') {
            return unescapeString(safeReplace) + safeContent;
        } else {
            // For regular search/replace, debug the process step by step
            const unescapedReplace = unescapeString(safeReplace);
            console.log(`🔄 After unescaping: "${unescapedReplace}" (length: ${unescapedReplace.length})`);
            console.log(`🔄 Unescaped char codes:`, Array.from(unescapedReplace).map(c => c.charCodeAt(0)));

            // Check if search string exists in content
            const searchIndex = safeContent.indexOf(safeSearch);
            console.log(`🎯 Search index in content: ${searchIndex}`);

            if (searchIndex >= 0) {
                // Show context around the match
                const contextStart = Math.max(0, searchIndex - 50);
                const contextEnd = Math.min(safeContent.length, searchIndex + safeSearch.length + 50);
                const contextStr = safeContent.substring(contextStart, contextEnd);
                console.log(`📍 Context around match (${contextStart}-${contextEnd}): "${contextStr}"`);
                console.log(`📍 Context char codes:`, Array.from(contextStr).map(c => c.charCodeAt(0)));
            } else {
                console.log(`❌ Search string NOT FOUND in content!`);
                // Show a sample of the content to help debug
                const contentSample = safeContent.substring(0, 200);
                console.log(`📄 Content sample (first 200 chars): "${contentSample}"`);
                console.log(`📄 Content sample char codes:`, Array.from(contentSample).map(c => c.charCodeAt(0)));
            }

            // Perform the replacement
            const result = safeContent.replace(safeSearch, unescapedReplace);

            // Check if replacement actually happened
            const replacementHappened = result !== safeContent;
            console.log(`✅ Replacement happened: ${replacementHappened}`);
            console.log(`📊 Result length: ${result.length} (was: ${safeContent.length})`);

            if (replacementHappened) {
                console.log(`🎉 SUCCESS: Replaced "${safeSearch}" with "${unescapedReplace}"`);
            } else {
                console.log(`❌ FAILURE: No replacement occurred - search string not found or identical`);
            }

            return result;
        }
    } catch (err) {
        console.error(`String replacement failed for ${context}:`, {
            error: err.message,
            stack: err.stack,
            contentType: typeof safeContent,
            searchType: typeof safeSearch,
            replaceType: typeof safeReplace
        });
        throw new Error(`String replacement failed for ${context}: ${err.message}`);
    }
}


// Debug function to log information about the editor state
function debugEditorState(editor: EditorView, label: string) {
    console.log(`Debug ${label}:`, {
        hasFocus: editor.hasFocus,
        docLength: editor.state.doc.length
    });
}

// Function to get language extensions for a file based on its extension
function getLanguageExtensionsForFile(filePath: string): Extension[] {
    const fileExtension = filePath.split('.').pop()?.toLowerCase() || '';
    const extensions: Extension[] = [];

    // Always add JupyterLab's syntax highlighting
    extensions.push(syntaxHighlighting(jupyterHighlightStyle));

    // Add language support based on file extension
    let languageSupport: Extension | null = null;

    switch (fileExtension) {
        case 'py':
            languageSupport = python();
            break;
        case 'js':
            languageSupport = javascript();
            break;
        case 'ts':
            languageSupport = javascript({ typescript: true });
            break;
        case 'jsx':
            languageSupport = javascript({ jsx: true });
            break;
        case 'tsx':
            languageSupport = javascript({ jsx: true, typescript: true });
            break;
        case 'json':
            languageSupport = json();
            break;
        case 'md':
            languageSupport = markdown();
            break;
        case 'html':
        case 'htm':
            languageSupport = html();
            break;
        case 'css':
            languageSupport = css();
            break;
        // Add more language support as needed
    }

    if (languageSupport) {
        extensions.push(languageSupport);
        console.log(`Added language support for ${fileExtension}`);
    } else {
        console.log(`No specific language support for ${fileExtension}, using default highlighting`);
    }

    return extensions;
}

var mergeViews = {};
var mergeWidgets = {}

// Network-resilient features for remote server scenarios
var fileOperationLocks = new Map<string, Promise<void>>();
var lastOperationTime = new Map<string, number>();
const MIN_OPERATION_INTERVAL = 150; // Minimum ms between operations on same file

// Streaming content state management
var streamingContent = new Map<string, string>();
var streamingCallIds = new Map<string, string>(); // Maps filePath to current call_id

// Network-resilient helper functions
async function waitForFileOperationLock(filePath: string): Promise<void> {
    const existingLock = fileOperationLocks.get(filePath);
    if (existingLock) {
        console.log(`⏳ Waiting for existing operation on ${filePath} to complete...`);
        try {
            await existingLock;
        } catch (err) {
            console.warn(`Previous operation on ${filePath} failed, continuing:`, err.message);
        }
    }
}

async function enforceOperationInterval(filePath: string): Promise<void> {
    const lastTime = lastOperationTime.get(filePath);
    if (lastTime) {
        const timeSinceLastOp = Date.now() - lastTime;
        if (timeSinceLastOp < MIN_OPERATION_INTERVAL) {
            const waitTime = MIN_OPERATION_INTERVAL - timeSinceLastOp;
            console.log(`⏱️ Enforcing ${waitTime}ms delay for ${filePath} to prevent race conditions`);
            await new Promise(resolve => setTimeout(resolve, waitTime));
        }
    }
}

function createFileOperationLock(filePath: string, operation: () => Promise<any>): Promise<any> {
    const lockPromise = (async () => {
        try {
            // Wait for any existing operations
            await waitForFileOperationLock(filePath);

            // Enforce minimum interval between operations
            await enforceOperationInterval(filePath);

            // Update last operation time
            lastOperationTime.set(filePath, Date.now());

            console.log(`🔒 Acquired operation lock for ${filePath}`);

            // Execute the operation
            const result = await operation();

            console.log(`🔓 Released operation lock for ${filePath}`);
            return result;
        } catch (err) {
            console.error(`❌ Operation failed for ${filePath}:`, err);
            throw err;
        } finally {
            // Always clean up the lock
            fileOperationLocks.delete(filePath);
        }
    })();

    // Store the lock promise
    fileOperationLocks.set(filePath, lockPromise);

    return lockPromise;
}

async function readFileWithNetworkResilience(contents: any, filePath: string, maxRetries = 3): Promise<any> {
    return createFileOperationLock(filePath, async () => {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            const startTime = Date.now();
            try {
                console.log(`📖 Reading file ${filePath}, attempt ${attempt}/${maxRetries}`);

                const result = await contents.get(filePath);
                const duration = Date.now() - startTime;

                console.log(`✅ File read attempt ${attempt} took ${duration}ms`, {
                    hasResult: !!result,
                    resultType: typeof result,
                    hasContent: !!result?.content,
                    contentType: typeof result?.content,
                    fileType: result?.type,
                    format: result?.format,
                    mimetype: result?.mimetype
                });

                if (!result) {
                    throw new Error(`File read returned null/undefined on attempt ${attempt}`);
                }

                // Additional validation for remote server scenarios
                if (result.mimetype === null && result.type === 'notebook' && filePath.endsWith('.py')) {
                    console.log(`🔍 Detected potential Jupytext file with null mimetype on remote server`);
                }

                return result;
            } catch (err) {
                const duration = Date.now() - startTime;
                console.error(`❌ File read attempt ${attempt} failed:`, {
                    error: err.message,
                    stack: err.stack,
                    filePath,
                    networkLatency: duration
                });

                if (attempt === maxRetries) {
                    throw new Error(`Failed to read file ${filePath} after ${maxRetries} attempts: ${err.message}`);
                }

                // Exponential backoff with jitter for network issues
                const baseDelay = 200 * Math.pow(2, attempt - 1);
                const jitter = Math.random() * 100;
                const delay = Math.min(baseDelay + jitter, 2000);

                console.log(`⏳ Retrying in ${Math.round(delay)}ms with exponential backoff...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    });
}

export function init_diff() {
    functions["diffToFile"] = {
        "def": {
            "name": "diffToFile",
            "description": "Makes tagreted change in file. Search must match the entire piece exactly. Use it in as a diff",
            "arguments": {
                "filePath": {
                    "type": "string",
                    "name": "Relative path to the file to display in merge view. Relative! "
                },
                "search": {
                    "type": "string",
                    "name": "text to be removed. Pass '+' string to append to file, '-' to add at the beginning"
                },
                "replace": {
                    "type": "string",
                    "name": "text to insert instead of the removed text"
                }
            }
        },
        "func": async (args: any, streaming: boolean = false, call_id: string = undefined): Promise<string> => {
            function updateDocB(mergeView: MergeView, newContent: string): boolean {
                try {
                    // Validate inputs
                    if (!mergeView) {
                        console.error('MergeView is null or undefined');
                        return false;
                    }

                    const safeContent = ensureString(newContent, 'updateDocB newContent');

                    // Try to access the editor for doc B directly through the mergeView object
                    if (!mergeView.b || !mergeView.b.state) {
                        console.error('Could not access state for doc B');
                        return false;
                    }

                    // Get the current state and create a new state with the updated content
                    const currentState = mergeView.b.state;

                    if (!currentState.doc) {
                        console.error('Current state doc is null or undefined');
                        return false;
                    }

                    console.log('Updating doc B:', {
                        currentDocLength: currentState.doc.length,
                        newContentLength: safeContent.length,
                        newContentType: typeof safeContent
                    });

                    // Create a transaction to replace the entire document content
                    mergeView.b.dispatch({
                        changes: {
                            from: 0,
                            to: currentState.doc.length,
                            insert: safeContent
                        }
                    });

                    console.log('Successfully updated doc B');
                    return true;
                } catch (err) {
                    console.error('Error updating doc B:', {
                        error: err.message,
                        stack: err.stack,
                        mergeViewExists: !!mergeView,
                        newContentType: typeof newContent
                    });
                    return false;
                }
            }




            const applySyntaxHighlighting = (mergeView) => {
                try {
                    const editors = mergeView.dom.querySelectorAll('.cm-editor');
                    console.log(`Found ${editors.length} editors in merge view`);

                    editors.forEach((editorElement, index) => {
                        const editorView = (editorElement as any).view;
                        if (editorView) {
                            debugEditorState(editorView, `Editor ${index}`);

                            // Add a class to the editor element based on file extension
                            const fileExtension = filePath.split('.').pop()?.toLowerCase() || '';
                            editorElement.classList.add(`language-${fileExtension}`);

                            // Force a refresh of the editor view using requestAnimationFrame for better performance
                            requestAnimationFrame(() => {
                                try {
                                    // Dispatch a dummy transaction to force a refresh
                                    editorView.dispatch({});
                                } catch (err) {
                                    console.error(`Error refreshing editor ${index}:`, err);
                                }
                            });
                        } else {
                            console.log(`Could not access view for editor ${index}`);
                        }
                    });
                } catch (err) {
                    console.error("Error applying syntax highlighting:", err);
                }
            };



            if (!app) {
                return JSON.stringify({ error: "JupyterLab app not initialized" });
            }

            const { contents } = app.serviceManager;
            const { filePath, search, replace } = args;

            if ((search == undefined) || (replace == undefined)) {
                return ""
            }

            try {
                const startTime = Date.now();
                console.log(`Starting diffToFile operation for ${filePath}`, {
                    streaming,
                    call_id,
                    search: search?.substring(0, 50) + (search?.length > 50 ? '...' : ''),
                    replace: replace?.substring(0, 50) + (replace?.length > 50 ? '...' : '')
                });

                // Handle streaming content state management
                let originalFileContent: string;
                let currentDisplayContent: string;
                let isFirstOperation = false;

                if (streamingContent.has(call_id + '_original')) {
                    // Use cached original content for ALL operations
                    originalFileContent = streamingContent.get(call_id + '_original');
                    currentDisplayContent = streamingContent.get(call_id) || originalFileContent;
                    console.log(`📋 Using cached original content for operation (${originalFileContent.length} chars)`);
                } else {
                    // Read from disk only for the very first operation
                    isFirstOperation = true;
                    let fileContent;
                    try {
                        fileContent = await readFileWithNetworkResilience(contents, filePath);
                    } catch (err) {
                        console.error(`File read failed for ${filePath}:`, {
                            error: err.message,
                            stack: err.stack
                        });
                        return JSON.stringify({
                            "status": "fail",
                            "message": `Cannot open file: ${filePath} - ${err.message}`,
                            "stack": err.stack
                        });
                    }

                    // Validate and extract content safely
                    try {
                        originalFileContent = validateFileContent(fileContent, filePath);
                        currentDisplayContent = originalFileContent;

                        // Cache original content permanently for ALL operations
                        streamingContent.set(call_id + '_original', originalFileContent);
                        streamingContent.set(call_id, originalFileContent);
                        streamingCallIds.set(filePath, call_id);
                        console.log(`💾 Cached original content for ALL operations (${originalFileContent.length} chars)`);
                    } catch (err) {
                        console.error(`File content validation failed for ${filePath}:`, {
                            error: err.message,
                            stack: err.stack,
                            fileContent: typeof fileContent,
                            hasContent: !!fileContent?.content
                        });
                        return JSON.stringify({
                            "status": "fail",
                            "message": `Invalid file content for ${filePath}: ${err.message}`,
                            "stack": err.stack
                        });
                    }
                }

                // Apply the diff with safe string operations - ALWAYS use original file content
                let diffResult: string;
                try {
                    // ALWAYS apply operations to the original file content
                    console.log(`🎯 Applying operation to original file content (${originalFileContent.length} chars)`);

                    if (search === '+') {
                        // Append: original + new content
                        diffResult = originalFileContent + unescapeString(replace);
                    } else if (search === '-') {
                        // Prepend: new content + original
                        diffResult = unescapeString(replace) + originalFileContent;
                    } else {
                        // Regular search/replace: apply to original content
                        diffResult = safeStringReplace(originalFileContent, search, replace, filePath);
                    }
                } catch (err) {
                    console.error(`String replacement failed for ${filePath}:`, {
                        error: err.message,
                        stack: err.stack
                    });
                    return JSON.stringify({
                        "status": "fail",
                        "message": `String replacement failed for ${filePath}: ${err.message}`,
                        "stack": err.stack
                    });
                }

                // Update cached content with the new result
                streamingContent.set(call_id, diffResult);
                console.log(`🔄 Updated cached content for ${streaming ? 'streaming' : 'final'} operation (${diffResult.length} chars)`);

                const processingTime = Date.now() - startTime;
                console.log(`File processing completed for ${filePath} in ${processingTime}ms`);

                if (mergeViews[call_id] != undefined) {
                    updateDocB(mergeViews[call_id], diffResult);
                } else if (mergeViews[call_id] == undefined) {

                    // Create a container for the merge view
                    const container = document.createElement('div');
                    container.style.height = '100%';
                    container.style.overflow = 'auto';

                    // Get language extensions for the file and add JupyterLab theme
                    const languageExtensions = [jupyterTheme, ...getLanguageExtensionsForFile(filePath)];

                    // Add a style element for syntax highlighting using JupyterLab's CSS variables
                    const styleElement = document.createElement('style');
                    styleElement.textContent = `
                        /* Basic syntax highlighting styles using JupyterLab variables */
                        .cm - keyword { color: var(--jp - mirror - editor - keyword - color); font - weight: bold; }
                        .cm - comment { color: var(--jp - mirror - editor - comment - color); }
                        .cm - string { color: var(--jp - mirror - editor - string - color); }
                        .cm - number { color: var(--jp - mirror - editor - number - color); }
                        .cm - operator { color: var(--jp - mirror - editor - operator - color); }
                        .cm - property { color: var(--jp - mirror - editor - property - color); }
                        .cm - variable { color: var(--jp - mirror - editor - variable - color); }
                        .cm - function, .cm - def { color: var(--jp - mirror - editor - def - color); }
                        .cm - atom { color: var(--jp - mirror - editor - atom - color); }
                        .cm - meta { color: var(--jp - mirror - editor - meta - color); }
                        .cm - tag { color: var(--jp - mirror - editor - tag - color); }
                        .cm - attribute { color: var(--jp - mirror - editor - attribute - color); }
                        .cm - qualifier { color: var(--jp - mirror - editor - qualifier - color); }
                        .cm - bracket { color: var(--jp - mirror - editor - bracket - color); }
                        .cm - builtin { color: var(--jp - mirror - editor - builtin - color); }
                        .cm - special { color: var(--jp - mirror - editor - string - 2 - color); }
    `;
                    document.head.appendChild(styleElement);

                    let mergeView: MergeView;
                    try {
                        mergeView = createMergeViewSafely(originalFileContent, diffResult, languageExtensions, filePath);
                    } catch (err) {
                        console.error(`MergeView creation failed for ${filePath}:`, {
                            error: err.message,
                            stack: err.stack
                        });
                        return JSON.stringify({
                            "status": "fail",
                            "message": `MergeView creation failed for ${filePath}: ${err.message}`,
                            "stack": err.stack
                        });
                    }


                    mergeViews[call_id] = mergeView;

                    container.appendChild(mergeView.dom);

                    // Apply syntax highlighting immediately using requestAnimationFrame for better performance
                    requestAnimationFrame(() => {
                        applySyntaxHighlighting(mergeView);
                    });

                    // Create a widget to hold the container
                    const widget = new Widget();
                    mergeWidgets[call_id] = widget;

                    widget.id = call_id;
                    widget.title.label = `Merge View: ${filePath} `;
                    widget.title.closable = true;
                    widget.node.appendChild(container);

                    // Add the widget to the main area and activate it
                    app.shell.add(widget, 'main');
                    app.shell.activateById(widget.id);

                }

                if (!streaming) {
                    // Clean up streaming cache when operation completes
                    streamingContent.delete(call_id);
                    streamingContent.delete(call_id + '_original'); // Clean up original content cache too
                    streamingCallIds.delete(filePath);
                    console.log(`🧹 Cleaned up streaming cache for ${filePath}`);

                    // Save the file to disk (ensures persistence)
                    await contents.save(filePath, {
                        type: 'file',
                        format: 'text',
                        content: diffResult
                    });

                    console.log(`💾 File saved successfully: ${filePath}`);

                    // Update any open editors with the new content (without reloading from disk)
                    try {
                        const docManager = app.serviceManager.contents;
                        const docRegistry = app.docRegistry;

                        // Find any open widgets for this file
                        const widgets = app.shell.widgets('main');
                        for (const widget of widgets) {
                            if (widget.title.label.includes(filePath.split('/').pop()) ||
                                (widget as any).context?.path === filePath) {

                                // Update the widget's content directly
                                const context = (widget as any).context;
                                if (context && context.model && typeof context.model.fromString === 'function') {
                                    context.model.fromString(diffResult);

                                    // Mark the document as saved to prevent "unsaved" state
                                    if (context.model.dirty !== undefined) {
                                        context.model.dirty = false;
                                    }

                                    // Trigger save state update if available
                                    if (typeof context.model.stateChanged?.emit === 'function') {
                                        context.model.stateChanged.emit({
                                            name: 'dirty',
                                            oldValue: true,
                                            newValue: false
                                        });
                                    }

                                    console.log(`📝 Updated open editor for ${filePath} and marked as saved`);
                                }
                            }
                        }
                    } catch (err) {
                        console.warn(`Could not update open editors: ${err.message}`);
                    }

                    // Log final content for debugging (instead of alert to avoid blocking)
                    const contentPreview = diffResult.length > 500 ?
                        diffResult.substring(0, 500) + '\n\n... (truncated)' :
                        diffResult;

                    console.log(`🔍 FINAL CONTENT DEBUG for ${filePath}:`);
                    console.log(`Length: ${diffResult.length} characters`);
                    console.log(`Search: "${search}"`);
                    console.log(`Replace: "${replace}"`);
                    console.log(`Content:\n${contentPreview}`);

                    // Close the diff view and open/focus the file
                    if (mergeViews[call_id]) {
                        const widget = mergeWidgets[call_id];
                        if (widget) {
                            // Close the diff view
                            widget.close();
                            console.log(`🗑️ Closed diff view for ${filePath}`);

                            // Open the file (or focus if already open)
                            try {
                                await app.commands.execute('docmanager:open', { path: filePath });
                                console.log(`📂 Opened/focused file: ${filePath}`);
                            } catch (err) {
                                console.warn(`Could not open file: ${err.message}`);
                            }
                        }
                    }

                    return JSON.stringify({
                        "status": "ok",
                        "new_content": diffResult
                    });

                }


            } catch (err) {
                return JSON.stringify({
                    "status": "fail",
                    "message": `Failed to open merge view: ${err.message} `,
                    "stack": err.stack
                });
            }
        }
    }
}
