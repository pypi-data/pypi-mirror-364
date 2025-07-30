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
                    // Handle both string and array formats
                    if (typeof cell.source === 'string') {
                        return cell.source;
                    } else if (Array.isArray(cell.source)) {
                        return cell.source.join('');
                    }
                }
                return '';
            })
            .join('\n');
    }

    // If it's not a recognizable notebook structure, stringify it
    return JSON.stringify(notebookContent, null, 2);
}

// Enhanced validation and safety functions
function validateFileContent(fileContent: any, filePath: string): string {
    console.log(`Validating file content for ${filePath}:`, {
        hasContent: !!fileContent,
        contentType: typeof fileContent?.content,
        contentLength: fileContent?.content?.length,
        fileType: fileContent?.type,
        format: fileContent?.format,
        mimetype: fileContent?.mimetype,
        writable: fileContent?.writable
    });

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

    console.log(`Content analysis for ${filePath}:`, {
        mimetype,
        fileType,
        format,
        contentType: typeof fileContent.content
    });

    // PRIORITY 1: Handle text files based on mimetype (most reliable indicator)
    // This must come BEFORE checking fileType to handle Jupytext files correctly
    if (mimetype.startsWith('text/') || mimetype === 'application/x-python-code') {
        console.log(`Processing text file ${filePath} with mimetype: ${mimetype}`);

        if (typeof fileContent.content === 'string') {
            console.log(`Text file ${filePath} has string content, returning as-is`);
            return fileContent.content;
        } else if (typeof fileContent.content === 'object' && format === 'json') {
            // This is a Jupytext file - extract source from notebook cells
            console.log(`Extracting source from Jupytext file ${filePath} (type=${fileType}, format=${format})`);
            try {
                return extractSourceFromNotebook(fileContent.content);
            } catch (err) {
                throw new Error(`Failed to extract source from Jupytext file ${filePath}: ${err.message}`);
            }
        } else {
            throw new Error(`Text file ${filePath} has unexpected content type: ${typeof fileContent.content}`);
        }
    }

    // PRIORITY 2: Handle actual notebook files (only if mimetype is not text-based)
    if ((fileType === 'notebook' || mimetype === 'application/x-ipynb+json') && !mimetype.startsWith('text/')) {
        console.log(`Processing actual notebook file ${filePath} (not Jupytext)`);
        if (fileContent.content === null) {
            return '';
        }
        try {
            return JSON.stringify(fileContent.content, null, 2);
        } catch (err) {
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
            const startTime = Date.now();
            console.log(`Reading file ${filePath}, attempt ${attempt}/${maxRetries}`);

            const result = await contents.get(filePath);
            const duration = Date.now() - startTime;

            console.log(`File read attempt ${attempt} took ${duration}ms`, {
                hasResult: !!result,
                resultType: typeof result,
                hasContent: !!result?.content,
                contentType: typeof result?.content,
                fileType: result?.type,
                format: result?.format
            });

            if (!result) {
                throw new Error(`File read returned null/undefined on attempt ${attempt}`);
            }

            // Don't validate content type here - let validateFileContent handle it
            // This allows us to properly handle different content formats (string, object, etc.)
            return result;
        } catch (err) {
            console.error(`File read attempt ${attempt} failed:`, {
                error: err.message,
                stack: err.stack,
                filePath
            });

            if (attempt === maxRetries) {
                throw new Error(`Failed to read file ${filePath} after ${maxRetries} attempts: ${err.message}`);
            }

            // Progressive delay between retries
            const delay = 100 * attempt;
            console.log(`Retrying in ${delay}ms...`);
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

    console.log(`Performing string replacement for ${context}:`, {
        contentLength: safeContent.length,
        searchLength: safeSearch.length,
        replaceLength: safeReplace.length,
        searchType: safeSearch
    });

    try {
        if (safeSearch === '+') {
            return safeContent + unescapeString(safeReplace);
        } else if (safeSearch === '-') {
            return unescapeString(safeReplace) + safeContent;
        } else {
            return safeContent.replace(unescapeString(safeSearch), unescapeString(safeReplace));
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

                            // Force a refresh of the editor view
                            setTimeout(() => {
                                try {
                                    // Dispatch a dummy transaction to force a refresh
                                    editorView.dispatch({});
                                } catch (err) {
                                    console.error(`Error refreshing editor ${index}:`, err);
                                }
                            }, 100);
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

                // Read the file content with retry logic
                let fileContent;
                try {
                    fileContent = await readFileWithRetry(contents, filePath);
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
                let originalContent: string;
                try {
                    originalContent = validateFileContent(fileContent, filePath);
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

                // Apply the diff with safe string operations
                let diffResult: string;
                try {
                    diffResult = safeStringReplace(originalContent, search, replace, filePath);
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
                        mergeView = createMergeViewSafely(originalContent, diffResult, languageExtensions, filePath);
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

                    setTimeout(function () {
                        applySyntaxHighlighting(mergeView);
                    }, 500);

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
                    console.log(app.commands.listCommands());

                    //app.commands.execute('docmanager:close', { path: filePath });


                    if (mergeViews[call_id]) {
                        // Find the widget by ID and close it
                        const widget = mergeWidgets[call_id];
                        //const widget = app.shell.widgets('main').find(w => w.id === call_id);
                        if (widget) {
                            setTimeout(() => {
                                widget.close();
                                setTimeout(() => {
                                    app.commands.execute('docmanager:open', { path: filePath });
                                    setTimeout(() => {
                                        app.commands.execute('docmanager:reload')
                                    }, 100)
                                }, 100)
                            }, 1000);
                        }
                    }

                    await contents.save(filePath, {
                        type: 'file',
                        format: 'text',
                        content: diffResult
                    });

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
