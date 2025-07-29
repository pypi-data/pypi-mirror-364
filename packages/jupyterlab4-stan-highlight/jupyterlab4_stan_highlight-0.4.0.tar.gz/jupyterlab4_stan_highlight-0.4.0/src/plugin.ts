import { stanLanguage } from './stan-lang';

// @ts-ignore
import { INotebookTracker } from '@jupyterlab/notebook';
// @ts-ignore  
import { CodeCell } from '@jupyterlab/cells';
// @ts-ignore
import { IEditorLanguageRegistry } from '@jupyterlab/codemirror';

/**
 * Register Stan file type and language
 */
function registerStanFileType(app: any): void {
  // Register file type
  app.docRegistry.addFileType({
    name: 'stan',
    displayName: 'Stan',
    extensions: ['stan'],
    mimeTypes: ['text/x-stan'],
  });

  console.log('Stan file type registered');
}

/**
 * Check if a cell starts with %%stan magic command
 */
function isStanCell(cell: any): boolean {
  if (!cell || !(cell instanceof CodeCell)) return false;

  const source = cell.model.sharedModel.getSource();
  const firstLine = source.split('\n')[0].trim();
  return firstLine.startsWith('%%stan');
}

/**
 * Apply Stan highlighting to a cell
 */
function applyStanHighlighting(cell: any): void {
  if (!isStanCell(cell)) return;

  try {
    console.log('Applying Stan highlighting to cell');

    // Set the MIME type
    cell.model.mimeType = 'text/x-stan';

    const editor = cell.editor;
    if (editor) {
      // Method 1: Try to use JupyterLab's language switching
      try {
        if (editor.model && editor.model.mimeType !== 'text/x-stan') {
          editor.model.mimeType = 'text/x-stan';
          console.log('Set MIME type to text/x-stan');
        }
      } catch (mimeError) {
        console.warn('Failed to set MIME type:', mimeError);
      }

      // Method 2: Try CodeMirror 6 reconfiguration (safer approach)
      if (editor.editor && editor.editor.state) {
        try {
          const editorView = editor.editor;

          // Check if we can access the state configuration
          if (editorView.state && editorView.state.facet) {
            // This is a safer way to work with CodeMirror 6
            console.log('CodeMirror 6 editor detected, attempting language change');

            // Try to force a refresh instead of reconfiguration
            if (editor.refresh) {
              editor.refresh();
              console.log('Editor refreshed');
            }

            // Alternative: dispatch a simple update
            if (editorView.dispatch) {
              editorView.dispatch({
                changes: { from: 0, to: 0, insert: '' }
              });
            }
          }
        } catch (configError) {
          console.warn('CodeMirror configuration failed:', configError);
        }
      }

      // Method 3: Force editor to re-evaluate content
      setTimeout(() => {
        try {
          if (editor.focus && editor.blur) {
            editor.focus();
            editor.blur();
          }
        } catch (focusError) {
          console.warn('Focus/blur failed:', focusError);
        }
      }, 100);
    }
  } catch (error) {
    console.warn('Failed to apply Stan highlighting:', error);
  }
}/**
 * Process all cells in a notebook
 */
function processNotebook(notebook: any): void {
  if (!notebook) return;

  notebook.content.widgets.forEach((cell: any) => {
    if (cell instanceof CodeCell) {
      applyStanHighlighting(cell);
    }
  });
}

/**
 * JupyterLab extension definition
 */
const extension: any = {
  id: 'jupyterlab-stan-highlight',
  autoStart: true,
  requires: [INotebookTracker],
  optional: [IEditorLanguageRegistry],
  activate: function (
    app: any,
    tracker: any,
    languageRegistry?: any
  ): void {
    console.log('JupyterLab extension jupyterlab-stan-highlight is activated!');
    console.log('Available language registry:', !!languageRegistry);
    console.log('Language registry type:', typeof languageRegistry);
    console.log('Stan language definition:', stanLanguage);
    console.log('App object:', app);

    // Register Stan file type
    registerStanFileType(app);

    // Register Stan language with enhanced error handling
    console.log('Attempting to register Stan language...');

    if (languageRegistry) {
      try {
        // Try the standard approach
        const registration = {
          name: 'stan',
          mime: 'text/x-stan',
          extensions: ['stan'],
          load: async () => {
            console.log('Loading Stan language definition for registration');
            return stanLanguage;
          }
        };

        languageRegistry.addLanguage(registration);
        console.log('Stan language registered successfully with IEditorLanguageRegistry');

        // Try alternative MIME types as well
        try {
          languageRegistry.addLanguage({
            name: 'stan-text',
            mime: 'text/stan',
            extensions: ['stan'],
            load: async () => stanLanguage
          });
          console.log('Alternative Stan MIME type registered');
        } catch (altError) {
          console.warn('Alternative MIME registration failed:', altError);
        }

      } catch (registrationError) {
        console.error('Failed to register Stan language:', registrationError);
      }
    } else {
      console.warn('Language registry not available - this may be normal in some JupyterLab configurations');

      // Fallback: try to access global language registry
      try {
        const globalRegistry = (window as any).jupyterlab?.languageRegistry;
        if (globalRegistry) {
          globalRegistry.addLanguage({
            name: 'stan',
            mime: 'text/x-stan',
            extensions: ['stan'],
            load: async () => stanLanguage
          });
          console.log('Stan language registered via global registry');
        }
      } catch (globalError) {
        console.warn('Global registry fallback failed:', globalError);
      }
    }    // Function to check and apply highlighting to all cells
    const checkAllCells = (notebook: any) => {
      if (!notebook) return;

      console.log('Checking all cells for Stan magic');
      notebook.content.widgets.forEach((cell: any, index: number) => {
        if (cell instanceof CodeCell) {
          const source = cell.model.sharedModel.getSource();
          const firstLine = source.split('\n')[0].trim();
          if (firstLine.startsWith('%%stan')) {
            console.log(`Found Stan cell at index ${index}`);
            applyStanHighlighting(cell);
          }
        }
      });
    };

    // Monitor cell content changes
    const setupCellMonitoring = (notebook: any) => {
      if (!notebook) return;

      // Monitor each cell for content changes
      notebook.content.widgets.forEach((cell: any) => {
        if (cell instanceof CodeCell) {
          // Listen to model changes
          cell.model.contentChanged.connect(() => {
            setTimeout(() => applyStanHighlighting(cell), 100);
          });
        }
      });

      // Monitor when new cells are added
      notebook.content.model.cells.changed.connect(() => {
        setTimeout(() => checkAllCells(notebook), 100);
      });
    };

    // Process notebooks when they change
    tracker.currentChanged.connect((tracker: any, notebook: any) => {
      if (notebook) {
        notebook.revealed.then(() => {
          console.log('Notebook changed, setting up monitoring');
          checkAllCells(notebook);
          setupCellMonitoring(notebook);
        });
      }
    });

    // Process active cell when it changes
    tracker.activeCellChanged.connect((tracker: any, activeCell: any) => {
      if (activeCell instanceof CodeCell) {
        console.log('Active cell changed, checking for Stan magic');
        applyStanHighlighting(activeCell);
      }
    });

    // Process new notebooks
    tracker.widgetAdded.connect((tracker: any, notebook: any) => {
      notebook.revealed.then(() => {
        console.log('New notebook added, setting up monitoring');
        checkAllCells(notebook);
        setupCellMonitoring(notebook);
      });
    });

    // Process current notebook if it already exists
    if (tracker.currentWidget) {
      console.log('Processing existing notebook');
      checkAllCells(tracker.currentWidget);
      setupCellMonitoring(tracker.currentWidget);
    }
  }
};

export default [extension];
