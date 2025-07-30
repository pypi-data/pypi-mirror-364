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
    console.log('🔬 CELL-EXTRACTION: Starting extraction process', {
        hasNotebookContent: !!notebookContent,
        contentType: typeof notebookContent,
        contentKeys: notebookContent ? Object.keys(notebookContent) : []
    });

    if (!notebookContent || typeof notebookContent !== 'object') {
        console.log('❌ CELL-EXTRACTION: Invalid notebook content');
        return '';
    }

    // Handle Jupytext notebook structure
    if (notebookContent.cells && Array.isArray(notebookContent.cells)) {
        console.log('🔬 CELL-EXTRACTION: Processing notebook cells', {
            totalCells: notebookContent.cells.length,
            cellTypes: notebookContent.cells.map((cell: any) => cell.cell_type || 'unknown')
        });

        const processedCells = notebookContent.cells
            .map((cell: any, index: number) => {
                console.log(`🔬 CELL-EXTRACTION: Processing cell ${index}`, {
                    cellType: cell.cell_type,
                    hasSource: !!cell.source,
                    sourceType: typeof cell.source,
                    sourceIsArray: Array.isArray(cell.source),
                    sourceLength: Array.isArray(cell.source) ? cell.source.length :
                        typeof cell.source === 'string' ? cell.source.length : 0,
                    rawSource: cell.source
                });

                if (cell.source) {
                    let cellSource = '';

                    // Handle both string and array formats
                    if (typeof cell.source === 'string') {
                        cellSource = cell.source;
                        console.log(`📝 CELL-EXTRACTION: Cell ${index} - String source`, {
                            length: cellSource.length,
                            preview: cellSource.substring(0, 100) + (cellSource.length > 100 ? '...' : ''),
                            endsWithNewline: cellSource.endsWith('\n')
                        });
                    } else if (Array.isArray(cell.source)) {
                        // CRITICAL FIX: Preserve original line structure
                        cellSource = cell.source.join('');
                        console.log(`📝 CELL-EXTRACTION: Cell ${index} - Array source`, {
                            arrayLength: cell.source.length,
                            arrayElements: cell.source.map((line: string, i: number) => ({
                                index: i,
                                content: line,
                                length: line.length,
                                endsWithNewline: line.endsWith('\n')
                            })),
                            joinedLength: cellSource.length,
                            joinedPreview: cellSource.substring(0, 100) + (cellSource.length > 100 ? '...' : ''),
                            joinedEndsWithNewline: cellSource.endsWith('\n')
                        });
                    }

                    // CRITICAL FIX: Don't add extra newlines if content already has proper endings
                    // Only add newline if the cell doesn't end with one AND it's not empty
                    if (cellSource && !cellSource.endsWith('\n') && cellSource.trim().length > 0) {
                        console.log(`📝 CELL-EXTRACTION: Cell ${index} - Adding missing newline`);
                        cellSource += '\n';
                    }

                    console.log(`✅ CELL-EXTRACTION: Cell ${index} - Final processed`, {
                        finalLength: cellSource.length,
                        finalPreview: cellSource.substring(0, 100) + (cellSource.length > 100 ? '...' : ''),
                        finalEndsWithNewline: cellSource.endsWith('\n')
                    });

                    return cellSource;
                }

                console.log(`⚠️ CELL-EXTRACTION: Cell ${index} - No source content`);
                return '';
            })
            .filter((source, index) => {
                const hasContent = source.trim().length > 0;
                console.log(`🔍 CELL-EXTRACTION: Cell ${index} filter result`, {
                    hasContent,
                    trimmedLength: source.trim().length,
                    originalLength: source.length
                });
                return hasContent;
            });

        console.log('🔬 CELL-EXTRACTION: Joining processed cells', {
            totalProcessedCells: processedCells.length,
            cellLengths: processedCells.map(cell => cell.length),
            cellPreviews: processedCells.map((cell, i) => ({
                index: i,
                preview: cell.substring(0, 50) + (cell.length > 50 ? '...' : ''),
                endsWithNewline: cell.endsWith('\n')
            }))
        });

        // CRITICAL FIX: Don't add extra newlines between cells
        // The cells should already have proper line endings
        const finalResult = processedCells.join('');

        console.log('✅ CELL-EXTRACTION: Final result', {
            totalLength: finalResult.length,
            preview: finalResult.substring(0, 200) + (finalResult.length > 200 ? '...' : ''),
            endsWithNewline: finalResult.endsWith('\n'),
            lineCount: finalResult.split('\n').length
        });

        return finalResult;
    }

    // If it's not a recognizable notebook structure, stringify it
    console.log('⚠️ CELL-EXTRACTION: Not a notebook structure, stringifying');
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

    // COMPREHENSIVE DECISION LOGGING
    console.log(`🎯 FILE-TYPE: Starting validation decision process for ${filePath}`, {
        mimetype: mimetype,
        fileType: fileType,
        format: format,
        contentType: typeof fileContent.content,
        fileExtension: filePath.split('.').pop(),
        isPyFile: filePath.endsWith('.py')
    });

    // PRIORITY 1: Handle text files based on mimetype (most reliable indicator)
    // This must come BEFORE checking fileType to handle Jupytext files correctly
    const priority1Conditions = {
        mimetypeStartsWithText: mimetype.startsWith('text/'),
        mimetypeIsPythonCode: mimetype === 'application/x-python-code',
        matchesPriority1: mimetype.startsWith('text/') || mimetype === 'application/x-python-code'
    };

    console.log(`🎯 FILE-TYPE: Priority 1 check for ${filePath}`, {
        ...priority1Conditions,
        decision: priority1Conditions.matchesPriority1 ? 'TAKING_PRIORITY_1' : 'SKIPPING_PRIORITY_1',
        contentType: typeof fileContent.content,
        format: format
    });

    if (priority1Conditions.matchesPriority1) {
        if (typeof fileContent.content === 'string') {
            console.log(`✅ FILE-TYPE: Priority 1 - Processing as string content for ${filePath}`);
            return fileContent.content;
        } else if (typeof fileContent.content === 'object' && format === 'json') {
            console.log(`✅ FILE-TYPE: Priority 1 - Processing as Jupytext file (object content + json format) for ${filePath}`);
            // This is a Jupytext file - extract source from notebook cells
            try {
                const extractedSource = extractSourceFromNotebook(fileContent.content);
                return extractedSource;
            } catch (err) {
                console.error(`Failed to extract source from Jupytext file ${filePath}:`, err.message);
                throw new Error(`Failed to extract source from Jupytext file ${filePath}: ${err.message}`);
            }
        } else {
            console.error(`❌ FILE-TYPE: Priority 1 - Unexpected content type for text file ${filePath}:`, {
                contentType: typeof fileContent.content,
                format: format,
                mimetype: mimetype
            });
            throw new Error(`Text file ${filePath} has unexpected content type: ${typeof fileContent.content}`);
        }
    }

    // PRIORITY 1.5: Special case for Jupytext files with null mimetype
    // This handles the case where JupyterLab returns mimetype: null for Jupytext files
    // Expanded to support all Jupytext file extensions
    const JUPYTEXT_EXTENSIONS = ['.py', '.R', '.jl', '.md', '.Rmd', '.qmd'];
    const isJupytextExtension = JUPYTEXT_EXTENSIONS.some(ext => filePath.endsWith(ext));

    const priority1_5Conditions = {
        fileTypeIsNotebook: fileType === 'notebook',
        formatIsJson: format === 'json',
        mimetypeIsEmpty: !mimetype || mimetype === '',
        isJupytextExtension: isJupytextExtension,
        contentIsObject: typeof fileContent.content === 'object',
        hasJupytextMetadata: !!(fileContent.content?.metadata?.jupytext),
        matchesPriority1_5: fileType === 'notebook' &&
            format === 'json' &&
            (!mimetype || mimetype === '') &&
            isJupytextExtension &&
            typeof fileContent.content === 'object' &&
            fileContent.content?.metadata?.jupytext
    };

    console.log(`🎯 FILE-TYPE: Priority 1.5 (Jupytext null mimetype) check for ${filePath}`, {
        ...priority1_5Conditions,
        decision: priority1_5Conditions.matchesPriority1_5 ? 'TAKING_PRIORITY_1_5' : 'SKIPPING_PRIORITY_1_5',
        jupytextMetadata: fileContent.content?.metadata?.jupytext
    });

    if (priority1_5Conditions.matchesPriority1_5) {
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
    const priority2Conditions = {
        fileTypeIsNotebook: fileType === 'notebook',
        mimetypeIsNotebook: mimetype === 'application/x-ipynb+json',
        mimetypeNotText: !mimetype.startsWith('text/'),
        notJupytextFile: !(filePath.endsWith('.py') && fileContent.content?.metadata?.jupytext),
        matchesPriority2: (fileType === 'notebook' || mimetype === 'application/x-ipynb+json') &&
            !mimetype.startsWith('text/') &&
            !(filePath.endsWith('.py') && fileContent.content?.metadata?.jupytext)
    };

    console.log(`🎯 FILE-TYPE: Priority 2 (notebook) check for ${filePath}`, {
        ...priority2Conditions,
        decision: priority2Conditions.matchesPriority2 ? 'TAKING_PRIORITY_2' : 'SKIPPING_PRIORITY_2',
        contentIsNull: fileContent.content === null
    });

    if (priority2Conditions.matchesPriority2) {
        console.log(`✅ FILE-TYPE: Priority 2 - Processing as notebook file for ${filePath}`);

        if (fileContent.content === null) {
            console.log(`📝 FILE-TYPE: Priority 2 - Notebook content is null, returning empty string for ${filePath}`);
            return '';
        }
        try {
            const jsonString = JSON.stringify(fileContent.content, null, 2);
            console.log(`📝 FILE-TYPE: Priority 2 - Successfully stringified notebook content for ${filePath}`, {
                resultLength: jsonString.length
            });
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

function safeStringReplace(content: string, search: string, replace: string, context: string): { result: string, changePosition?: { line: number, ch: number } } {
    const safeContent = ensureString(content, `content for ${context}`);
    const safeSearch = ensureString(search, `search string for ${context}`);
    const safeReplace = ensureString(replace, `replace string for ${context}`);

    console.log(`🔧 STRING-REPLACE: Starting replacement for ${context}`, {
        contentLength: safeContent.length,
        searchLength: safeSearch.length,
        replaceLength: safeReplace.length,
        contentPreview: safeContent.substring(0, 200) + (safeContent.length > 200 ? '...' : ''),
        searchPreview: safeSearch.substring(0, 100) + (safeSearch.length > 100 ? '...' : ''),
        replacePreview: safeReplace.substring(0, 100) + (safeReplace.length > 100 ? '...' : ''),
        searchType: typeof safeSearch,
        isSpecialOperation: safeSearch === '+' || safeSearch === '-'
    });

    try {
        if (safeSearch === '+') {
            console.log(`🔧 STRING-REPLACE: Append operation for ${context}`);
            // Append: change is at the end of content
            const lines = safeContent.split('\n');
            const lastLineIndex = lines.length - 1;
            const lastLineLength = lines[lastLineIndex].length;
            const unescapedReplace = unescapeString(safeReplace);
            const result = safeContent + unescapedReplace;

            console.log(`✅ STRING-REPLACE: Append completed for ${context}`, {
                originalLength: safeContent.length,
                appendedLength: unescapedReplace.length,
                resultLength: result.length,
                changePosition: { line: lastLineIndex, ch: lastLineLength }
            });

            return {
                result: result,
                changePosition: { line: lastLineIndex, ch: lastLineLength }
            };
        } else if (safeSearch === '-') {
            console.log(`🔧 STRING-REPLACE: Prepend operation for ${context}`);
            // Prepend: change is at the beginning
            const unescapedReplace = unescapeString(safeReplace);
            const result = unescapedReplace + safeContent;

            console.log(`✅ STRING-REPLACE: Prepend completed for ${context}`, {
                originalLength: safeContent.length,
                prependedLength: unescapedReplace.length,
                resultLength: result.length,
                changePosition: { line: 0, ch: 0 }
            });

            return {
                result: result,
                changePosition: { line: 0, ch: 0 }
            };
        } else {
            console.log(`🔧 STRING-REPLACE: Regular search/replace operation for ${context}`);

            // Regular search/replace: find the position of the change
            const searchIndex = safeContent.indexOf(safeSearch);

            console.log(`🔍 STRING-REPLACE: Search analysis for ${context}`, {
                searchFound: searchIndex >= 0,
                searchIndex: searchIndex,
                searchInContent: searchIndex >= 0 ? 'FOUND' : 'NOT_FOUND',
                contentAroundSearch: searchIndex >= 0 ? {
                    before: safeContent.substring(Math.max(0, searchIndex - 50), searchIndex),
                    match: safeContent.substring(searchIndex, searchIndex + safeSearch.length),
                    after: safeContent.substring(searchIndex + safeSearch.length, Math.min(safeContent.length, searchIndex + safeSearch.length + 50))
                } : 'N/A'
            });

            let changePosition: { line: number, ch: number } | undefined;

            if (searchIndex >= 0) {
                // Calculate line and column position
                const beforeChange = safeContent.substring(0, searchIndex);
                const lines = beforeChange.split('\n');
                changePosition = {
                    line: lines.length - 1,
                    ch: lines[lines.length - 1].length
                };

                console.log(`📍 STRING-REPLACE: Change position calculated for ${context}`, {
                    searchIndex,
                    beforeChangeLength: beforeChange.length,
                    lineCount: lines.length,
                    changePosition
                });
            } else {
                console.warn(`⚠️ STRING-REPLACE: Search string not found in content for ${context}`);
            }

            const unescapedReplace = unescapeString(safeReplace);
            const result = safeContent.replace(safeSearch, unescapedReplace);

            console.log(`✅ STRING-REPLACE: Regular replacement completed for ${context}`, {
                originalLength: safeContent.length,
                searchLength: safeSearch.length,
                replaceLength: unescapedReplace.length,
                resultLength: result.length,
                replacementMade: result !== safeContent,
                changePosition,
                resultPreview: result.substring(0, 200) + (result.length > 200 ? '...' : ''),
                // Show content around the change
                changeArea: searchIndex >= 0 ? {
                    before: result.substring(Math.max(0, searchIndex - 50), searchIndex),
                    replacement: result.substring(searchIndex, searchIndex + unescapedReplace.length),
                    after: result.substring(searchIndex + unescapedReplace.length, Math.min(result.length, searchIndex + unescapedReplace.length + 50))
                } : 'N/A'
            });

            return { result, changePosition };
        }
    } catch (err) {
        console.error(`❌ STRING-REPLACE: Replacement failed for ${context}:`, {
            error: err.message,
            stack: err.stack,
            contentType: typeof safeContent,
            searchType: typeof safeSearch,
            replaceType: typeof safeReplace,
            contentLength: safeContent.length,
            searchLength: safeSearch.length,
            replaceLength: safeReplace.length
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

                // EXHAUSTIVE FILE TYPE ANALYSIS - Log everything JupyterLab returns
                console.log(`🔍 FILE-TYPE: EXHAUSTIVE analysis for ${filePath}`, {
                    // Raw object inspection
                    objectType: typeof result,
                    objectConstructor: result?.constructor?.name,

                    // All possible properties
                    allKeys: result ? Object.keys(result) : [],
                    allOwnPropertyNames: result ? Object.getOwnPropertyNames(result) : [],
                    propertyDescriptors: result ? Object.getOwnPropertyDescriptors(result) : {},

                    // File extension vs detected type analysis
                    fileExtension: filePath.split('.').pop(),
                    expectedMimetype: filePath.endsWith('.py') ? 'text/x-python' : 'unknown',
                    actualMimetype: result?.mimetype,
                    mimetypeMismatch: filePath.endsWith('.py') && result?.mimetype !== 'text/x-python',

                    // Standard properties we know about
                    standardProperties: {
                        name: result?.name,
                        path: result?.path,
                        type: result?.type,
                        format: result?.format,
                        mimetype: result?.mimetype,
                        size: result?.size,
                        writable: result?.writable,
                        last_modified: result?.last_modified,
                        created: result?.created,
                        hash: result?.hash,
                        hash_algorithm: result?.hash_algorithm
                    },

                    // Check for any custom or extension properties
                    customProperties: (() => {
                        if (!result) return {};
                        const standard = ['name', 'path', 'type', 'format', 'mimetype', 'content', 'size', 'writable', 'last_modified', 'created', 'hash', 'hash_algorithm'];
                        const all = Object.keys(result);
                        const custom = all.filter(key => !standard.includes(key));
                        const customObj = {};
                        custom.forEach(key => customObj[key] = result[key]);
                        return customObj;
                    })(),

                    // Content analysis
                    contentAnalysis: {
                        type: typeof result?.content,
                        isString: typeof result?.content === 'string',
                        isObject: typeof result?.content === 'object' && result?.content !== null,
                        isArray: Array.isArray(result?.content),
                        isNull: result?.content === null,
                        stringLength: typeof result?.content === 'string' ? result.content.length : null,
                        objectKeys: (typeof result?.content === 'object' && result?.content !== null) ? Object.keys(result.content) : null,
                        looksLikeNotebook: (typeof result?.content === 'object' && result?.content !== null) &&
                            (result.content.cells || result.content.metadata),
                        looksLikePythonCode: typeof result?.content === 'string' &&
                            (result.content.includes('def ') || result.content.includes('import ') || result.content.includes('class ')),
                        contentSample: typeof result?.content === 'string' ? result.content.substring(0, 200) + '...' : 'N/A',
                        contentStructure: (typeof result?.content === 'object' && result?.content !== null) ? {
                            hasCells: !!result.content.cells,
                            cellsType: result.content.cells ? (Array.isArray(result.content.cells) ? 'array' : typeof result.content.cells) : 'none',
                            cellsLength: Array.isArray(result.content.cells) ? result.content.cells.length : 'N/A',
                            hasMetadata: !!result.content.metadata,
                            metadataKeys: result.content.metadata ? Object.keys(result.content.metadata) : [],
                            hasJupytextInMetadata: !!(result.content.metadata?.jupytext),
                            hasKernelspec: !!(result.content.metadata?.kernelspec),
                            nbformat: result.content.nbformat,
                            nbformatMinor: result.content.nbformat_minor
                        } : null
                    }
                });

                // Log the complete raw object for manual inspection
                console.log(`📋 FILE-TYPE: Complete raw object for ${filePath}:`, result);

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
                    "name": "text to be removed. text should be long enough to ensure unique match. Pass '+' string to append to file, '-' to add at the beginning"
                },
                "replace": {
                    "type": "string",
                    "name": "text to insert instead of the removed text"
                }
            }
        },
        "func": async (args: any, streaming: boolean = false, call_id: string = undefined): Promise<string> => {
            function scrollToChangeOnce(mergeView: MergeView, position: { line: number, ch: number }): void {
                try {
                    if (!mergeView || !position) {
                        return;
                    }

                    // Calculate the document position from line/column
                    const docA = mergeView.a.state.doc;
                    const docB = mergeView.b.state.doc;

                    // Ensure line number is within bounds
                    const lineA = Math.min(position.line, docA.lines - 1);
                    const lineB = Math.min(position.line, docB.lines - 1);

                    // Get the line start position
                    const posA = docA.line(lineA + 1).from + Math.min(position.ch, docA.line(lineA + 1).length);
                    const posB = docB.line(lineB + 1).from + Math.min(position.ch, docB.line(lineB + 1).length);

                    // Scroll both editors so the edit line appears as the second line from top
                    mergeView.a.dispatch({
                        effects: EditorView.scrollIntoView(posA, { y: 'start', yMargin: 30 })
                    });

                    mergeView.b.dispatch({
                        effects: EditorView.scrollIntoView(posB, { y: 'start', yMargin: 30 })
                    });

                    console.log(`📍 Scrolled to change at line ${position.line}, column ${position.ch} (positioned as second line from top)`);
                } catch (err) {
                    console.warn('Could not scroll to change position:', err.message);
                }
            }

            function smartFollowScroll(mergeView: MergeView, position: { line: number, ch: number }): void {
                try {
                    if (!mergeView || !position) {
                        return;
                    }

                    // Get viewport and document info for the modified editor (B)
                    const editorB = mergeView.b;
                    const doc = editorB.state.doc;
                    const viewport = editorB.viewport;

                    // Calculate which line we're editing
                    const editLine = position.line;

                    // Find the last fully visible line in the viewport
                    const lastVisiblePos = viewport.to;
                    const lastVisibleLine = doc.lineAt(lastVisiblePos).number - 1; // Convert to 0-based


                    // Check if edit line is below the visible viewport
                    if (editLine > lastVisibleLine) {
                        // Edit is below screen - scroll so edit line becomes the last visible line
                        const lineA = Math.min(position.line, mergeView.a.state.doc.lines - 1);
                        const lineB = Math.min(position.line, doc.lines - 1);

                        const posA = mergeView.a.state.doc.line(lineA + 1).from + Math.min(position.ch, mergeView.a.state.doc.line(lineA + 1).length);
                        const posB = doc.line(lineB + 1).from + Math.min(position.ch, doc.line(lineB + 1).length);

                        // Scroll so the edit line appears as the last visible line
                        mergeView.a.dispatch({
                            effects: EditorView.scrollIntoView(posA, { y: 'end', yMargin: 20 })
                        });

                        mergeView.b.dispatch({
                            effects: EditorView.scrollIntoView(posB, { y: 'end', yMargin: 20 })
                        });

                    }
                } catch (err) {
                    console.warn('Could not perform smart follow scroll:', err.message);
                }
            }

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


                    // Create a transaction to replace the entire document content
                    mergeView.b.dispatch({
                        changes: {
                            from: 0,
                            to: currentState.doc.length,
                            insert: safeContent
                        }
                    });

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

                // Handle streaming content state management
                let originalFileContent: string;
                let currentDisplayContent: string;
                let isFirstOperation = false;

                if (streamingContent.has(call_id + '_original')) {
                    // Use cached original content for ALL operations
                    originalFileContent = streamingContent.get(call_id + '_original');
                    currentDisplayContent = streamingContent.get(call_id) || originalFileContent;
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

                // Clean separation: Streaming vs Non-Streaming operations
                let diffResult: string;
                let changePosition: { line: number, ch: number } | undefined;

                if (streaming) {
                    // STREAMING: Visual updates only - apply replacement for diff view
                    try {
                        if (search === '+') {
                            // Append: original + new content
                            const lines = originalFileContent.split('\n');
                            const lastLineIndex = lines.length - 1;
                            const lastLineLength = lines[lastLineIndex].length;
                            diffResult = originalFileContent + unescapeString(replace);
                            changePosition = { line: lastLineIndex, ch: lastLineLength };
                        } else if (search === '-') {
                            // Prepend: new content + original
                            diffResult = unescapeString(replace) + originalFileContent;
                            changePosition = { line: 0, ch: 0 };
                        } else {
                            // Regular search/replace: apply to original content
                            const replaceResult = safeStringReplace(originalFileContent, search, replace, filePath);
                            diffResult = replaceResult.result;
                            changePosition = replaceResult.changePosition;
                        }

                        // Cache the result for the final non-streaming call
                        streamingContent.set(call_id, diffResult);

                    } catch (err) {
                        console.error(`Streaming operation failed for ${filePath}:`, {
                            error: err.message,
                            stack: err.stack
                        });
                        return JSON.stringify({
                            "status": "fail",
                            "message": `Streaming operation failed for ${filePath}: ${err.message}`,
                            "stack": err.stack
                        });
                    }
                } else {
                    // NON-STREAMING: Persistence only - use cached final result
                    diffResult = streamingContent.get(call_id);
                    if (!diffResult) {
                        console.error(`No cached content found for call_id: ${call_id}`);
                        return JSON.stringify({
                            "status": "fail",
                            "message": `No cached content found for ${filePath}. Streaming may have failed.`,
                            "stack": "Missing cached content"
                        });
                    }
                }

                if (mergeViews[call_id] != undefined) {
                    // Subsequent streaming updates - update content and smart follow scroll
                    updateDocB(mergeViews[call_id], diffResult);

                    // Apply smart follow scrolling for consecutive chunks
                    if (changePosition && streaming) {
                        // Use requestAnimationFrame to ensure content update is rendered first
                        requestAnimationFrame(() => {
                            smartFollowScroll(mergeViews[call_id], changePosition);
                        });
                    }
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

                    // Apply syntax highlighting and scroll to change position on first creation
                    requestAnimationFrame(() => {
                        applySyntaxHighlighting(mergeView);

                        // Scroll to change position only on first chunk (MergeView creation)
                        if (changePosition) {
                            // Use a slight delay to ensure the view is fully rendered
                            setTimeout(() => {
                                scrollToChangeOnce(mergeView, changePosition);
                            }, 100);
                        }
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

                    // Modern approach: Use Document Context's save method for proper state synchronization
                    let savedSuccessfully = false;

                    try {
                        // Method 1: Find document context through open widgets (most reliable)
                        const widgets = app.shell.widgets('main');
                        let targetContext = null;

                        for (const widget of widgets) {
                            const context = (widget as any).context;
                            if (context && context.path === filePath) {
                                targetContext = context;
                                console.log(`🎯 Found document context via open widget for ${filePath}`);
                                break;
                            }
                        }

                        // Method 2: Try to find context through service manager (alternative approach)
                        if (!targetContext) {
                            // Look for widgets that might have the same path
                            for (const widget of widgets) {
                                if (widget.title && widget.title.label && widget.title.label.includes(filePath.split('/').pop() || '')) {
                                    const context = (widget as any).context;
                                    if (context && context.path === filePath) {
                                        targetContext = context;
                                        console.log(`🎯 Found document context via widget title matching for ${filePath}`);
                                        break;
                                    }
                                }
                            }
                        }

                        if (targetContext) {
                            // Update the model content with enhanced synchronization
                            if (targetContext.model && typeof targetContext.model.fromString === 'function') {
                                console.log(`📝 Updating model content via context for ${filePath}`);

                                // Log model state before update
                                const originalContent = targetContext.model.toString();
                                console.log(`📊 Model state before update:`, {
                                    isDirty: targetContext.model.dirty,
                                    contentLength: originalContent.length,
                                    modelType: typeof targetContext.model,
                                    isReady: targetContext.isReady
                                });
                                console.log(`🔍 Original content preview: ${originalContent.substring(0, 100)}...`);

                                // Update the model content
                                targetContext.model.fromString(diffResult);

                                // Ensure model is marked as dirty (some models don't auto-mark)
                                if (targetContext.model.dirty !== undefined) {
                                    targetContext.model.dirty = true;
                                }

                                // Verify content actually changed
                                const updatedContent = targetContext.model.toString();
                                const contentChanged = originalContent !== updatedContent;
                                console.log(`📊 Model state after update:`, {
                                    isDirty: targetContext.model.dirty,
                                    contentLength: updatedContent.length,
                                    newContentLength: diffResult.length,
                                    contentActuallyChanged: contentChanged
                                });
                                console.log(`🔍 Updated content preview: ${updatedContent.substring(0, 100)}...`);

                                if (!contentChanged) {
                                    console.warn(`⚠️ Model content did not change after fromString() call!`);
                                }

                                // Wait a tick for model updates to propagate
                                await new Promise(resolve => setTimeout(resolve, 10));

                                // Save with enhanced error handling
                                try {
                                    console.log(`💾 Attempting context save for ${filePath}...`);
                                    await targetContext.save();

                                    // Verify save completed by checking model state
                                    console.log(`📊 Model state after save:`, {
                                        isDirty: targetContext.model.dirty,
                                        isReady: targetContext.isReady,
                                        path: targetContext.path,
                                        contentLength: targetContext.model.toString().length
                                    });

                                    console.log(`✅ File saved successfully via document context: ${filePath}`);
                                    savedSuccessfully = true;
                                } catch (saveError) {
                                    console.error(`❌ Context save failed for ${filePath}:`, {
                                        error: saveError.message,
                                        stack: saveError.stack,
                                        contextPath: targetContext.path,
                                        modelDirty: targetContext.model.dirty
                                    });
                                    throw saveError;
                                }
                            } else {
                                console.warn(`Context found but model.fromString not available for ${filePath}`, {
                                    hasModel: !!targetContext.model,
                                    modelType: typeof targetContext.model,
                                    hasFromString: targetContext.model && typeof targetContext.model.fromString === 'function'
                                });
                            }
                        } else {
                            console.log(`📄 No document context found for ${filePath}, using fallback method`);
                        }
                    } catch (err) {
                        console.error(`Error using document context save for ${filePath}:`, err);
                    }

                    // Fallback: Direct save if context method failed
                    if (!savedSuccessfully) {
                        console.log(`🔄 Using fallback direct save method for ${filePath}`);
                        await contents.save(filePath, {
                            type: 'file',
                            format: 'text',
                            content: diffResult
                        });
                        console.log(`💾 File saved successfully via fallback method: ${filePath}`);

                        // Try to update any open contexts after direct save
                        try {
                            const widgets = app.shell.widgets('main');
                            for (const widget of widgets) {
                                const context = (widget as any).context;
                                if (context && context.path === filePath) {
                                    // Trigger a revert to sync the context with the saved file
                                    if (typeof context.revert === 'function') {
                                        await context.revert();
                                        console.log(`🔄 Reverted context to sync with saved file: ${filePath}`);
                                    }
                                }
                            }
                        } catch (err) {
                            console.warn(`Could not sync contexts after fallback save: ${err.message}`);
                        }
                    }

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
