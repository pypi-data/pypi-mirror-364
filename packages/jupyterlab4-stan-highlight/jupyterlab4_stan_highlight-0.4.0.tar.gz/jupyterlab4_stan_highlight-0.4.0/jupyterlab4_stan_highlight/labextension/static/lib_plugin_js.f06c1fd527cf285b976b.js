"use strict";
(self["webpackChunkjupyterlab_stan_highlight"] = self["webpackChunkjupyterlab_stan_highlight"] || []).push([["lib_plugin_js"],{

/***/ "./lib/plugin.js":
/*!***********************!*\
  !*** ./lib/plugin.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _stan_lang__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./stan-lang */ "./lib/stan-lang.js");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/cells */ "webpack/sharing/consume/default/@jupyterlab/cells");
/* harmony import */ var _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_cells__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/codemirror */ "webpack/sharing/consume/default/@jupyterlab/codemirror");
/* harmony import */ var _jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_3__);

// @ts-ignore

// @ts-ignore  

// @ts-ignore

/**
 * Register Stan file type and language
 */
function registerStanFileType(app) {
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
function isStanCell(cell) {
    if (!cell || !(cell instanceof _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_2__.CodeCell))
        return false;
    const source = cell.model.sharedModel.getSource();
    const firstLine = source.split('\n')[0].trim();
    return firstLine.startsWith('%%stan');
}
/**
 * Apply Stan highlighting to a cell
 */
function applyStanHighlighting(cell) {
    if (!isStanCell(cell))
        return;
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
            }
            catch (mimeError) {
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
                }
                catch (configError) {
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
                }
                catch (focusError) {
                    console.warn('Focus/blur failed:', focusError);
                }
            }, 100);
        }
    }
    catch (error) {
        console.warn('Failed to apply Stan highlighting:', error);
    }
} /**
 * Process all cells in a notebook
 */
function processNotebook(notebook) {
    if (!notebook)
        return;
    notebook.content.widgets.forEach((cell) => {
        if (cell instanceof _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_2__.CodeCell) {
            applyStanHighlighting(cell);
        }
    });
}
/**
 * JupyterLab extension definition
 */
const extension = {
    id: 'jupyterlab-stan-highlight',
    autoStart: true,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.INotebookTracker],
    optional: [_jupyterlab_codemirror__WEBPACK_IMPORTED_MODULE_3__.IEditorLanguageRegistry],
    activate: function (app, tracker, languageRegistry) {
        var _a;
        console.log('JupyterLab extension jupyterlab-stan-highlight is activated!');
        console.log('Available language registry:', !!languageRegistry);
        console.log('Language registry type:', typeof languageRegistry);
        console.log('Stan language definition:', _stan_lang__WEBPACK_IMPORTED_MODULE_0__.stanLanguage);
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
                        return _stan_lang__WEBPACK_IMPORTED_MODULE_0__.stanLanguage;
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
                        load: async () => _stan_lang__WEBPACK_IMPORTED_MODULE_0__.stanLanguage
                    });
                    console.log('Alternative Stan MIME type registered');
                }
                catch (altError) {
                    console.warn('Alternative MIME registration failed:', altError);
                }
            }
            catch (registrationError) {
                console.error('Failed to register Stan language:', registrationError);
            }
        }
        else {
            console.warn('Language registry not available - this may be normal in some JupyterLab configurations');
            // Fallback: try to access global language registry
            try {
                const globalRegistry = (_a = window.jupyterlab) === null || _a === void 0 ? void 0 : _a.languageRegistry;
                if (globalRegistry) {
                    globalRegistry.addLanguage({
                        name: 'stan',
                        mime: 'text/x-stan',
                        extensions: ['stan'],
                        load: async () => _stan_lang__WEBPACK_IMPORTED_MODULE_0__.stanLanguage
                    });
                    console.log('Stan language registered via global registry');
                }
            }
            catch (globalError) {
                console.warn('Global registry fallback failed:', globalError);
            }
        } // Function to check and apply highlighting to all cells
        const checkAllCells = (notebook) => {
            if (!notebook)
                return;
            console.log('Checking all cells for Stan magic');
            notebook.content.widgets.forEach((cell, index) => {
                if (cell instanceof _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_2__.CodeCell) {
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
        const setupCellMonitoring = (notebook) => {
            if (!notebook)
                return;
            // Monitor each cell for content changes
            notebook.content.widgets.forEach((cell) => {
                if (cell instanceof _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_2__.CodeCell) {
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
        tracker.currentChanged.connect((tracker, notebook) => {
            if (notebook) {
                notebook.revealed.then(() => {
                    console.log('Notebook changed, setting up monitoring');
                    checkAllCells(notebook);
                    setupCellMonitoring(notebook);
                });
            }
        });
        // Process active cell when it changes
        tracker.activeCellChanged.connect((tracker, activeCell) => {
            if (activeCell instanceof _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_2__.CodeCell) {
                console.log('Active cell changed, checking for Stan magic');
                applyStanHighlighting(activeCell);
            }
        });
        // Process new notebooks
        tracker.widgetAdded.connect((tracker, notebook) => {
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
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ([extension]);


/***/ }),

/***/ "./lib/stan-lang.js":
/*!**************************!*\
  !*** ./lib/stan-lang.js ***!
  \**************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   stanLang: () => (/* binding */ stanLang),
/* harmony export */   stanLanguage: () => (/* binding */ stanLanguage)
/* harmony export */ });
/* harmony import */ var _codemirror_language__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @codemirror/language */ "webpack/sharing/consume/default/@codemirror/language");
/* harmony import */ var _codemirror_language__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_codemirror_language__WEBPACK_IMPORTED_MODULE_0__);
// @ts-ignore

// Stan language definition for CodeMirror 6
const stan = {
    name: 'stan',
    startState() {
        return {
            tokenize: tokenBase,
            context: null,
            indent: 0,
            startOfLine: true
        };
    },
    token(stream, state) {
        if (stream.sol()) {
            state.startOfLine = true;
            state.indent = stream.indentation();
        }
        if (stream.eatSpace())
            return null;
        state.startOfLine = false;
        return state.tokenize(stream, state);
    },
    indent(state, textAfter) {
        const { context } = state;
        if (!context)
            return 0;
        return context.indent + (textAfter.charAt(0) === '}' ? 0 : 2);
    },
    languageData: {
        commentTokens: { line: '//', block: { open: '/*', close: '*/' } },
        closeBrackets: { brackets: ['(', '[', '{', '"'] },
        indentOnInput: /^\s*\}$/
    }
};
// Define tokenize functions outside the object to avoid 'this' issues
function tokenBase(stream, state) {
    // Comments
    if (stream.match('//')) {
        stream.skipToEnd();
        return 'comment';
    }
    if (stream.match('/*')) {
        state.tokenize = tokenComment;
        return 'comment';
    }
    if (stream.match('#')) {
        // Check for include directive
        if (stream.match(/\s*include\b/)) {
            state.tokenize = tokenInclude;
            return 'meta';
        }
        stream.skipToEnd();
        return 'comment';
    }
    // Numbers
    if (stream.match(/^(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?i?/)) {
        return 'number';
    }
    // Strings
    if (stream.match('"')) {
        state.tokenize = tokenString;
        return 'string';
    }
    // Block keywords
    if (stream.match(/\b(functions|data|transformed\s+data|parameters|transformed\s+parameters|model|generated\s+quantities)\b/)) {
        return 'keyword';
    }
    // Types
    if (stream.match(/\b(int|real|complex|vector|array|simplex|unit_vector|ordered|positive_ordered|row_vector|matrix|corr_matrix|cov_matrix|cholesky_factor_cov|cholesky_factor_corr|void)\b/)) {
        return 'type';
    }
    // Control flow
    if (stream.match(/\b(for|in|while|if|else|return)\b/)) {
        return 'keyword';
    }
    // Distribution sampling
    if (stream.match('~')) {
        return 'operator';
    }
    // Distributions
    if (stream.match(/\b(bernoulli|bernoulli_logit|beta|beta_binomial|binomial|binomial_logit|categorical|categorical_logit|cauchy|chi_square|dirichlet|discrete_range|double_exponential|exp_mod_normal|exponential|frechet|gamma|gaussian_dlm_obs|gumbel|hypergeometric|inv_chi_square|inv_gamma|inv_wishart|lkj_corr|lkj_corr_cholesky|logistic|lognormal|multi_gp|multi_gp_cholesky|multi_normal|multi_normal_cholesky|multi_normal_prec|multi_student_t|multinomial|multinomial_logit|neg_binomial|neg_binomial_2|neg_binomial_2_log|normal|normal_id_glm|ordered_logistic|ordered_probit|pareto|pareto_type_2|poisson|poisson_log|rayleigh|scaled_inv_chi_square|skew_double_exponential|skew_normal|std_normal|student_t|uniform|von_mises|weibull|wiener|wishart)\b/)) {
        return 'builtin';
    }
    // Built-in functions
    if (stream.match(/\b(print|reject|target)\b/)) {
        return 'builtin';
    }
    // Constraints
    if (stream.match(/\b(lower|upper|offset|multiplier)\b/)) {
        return 'keyword';
    }
    // Operators
    if (stream.match(/[+\-*/%^=<>!&|]+|<-/)) {
        return 'operator';
    }
    // Punctuation
    if (stream.match(/[{}()\[\];,]/)) {
        return 'bracket';
    }
    // Identifiers
    if (stream.match(/\b[A-Za-z][0-9A-Za-z_]*\b/)) {
        return 'variable';
    }
    // Illegal identifiers
    if (stream.match(/\b([a-zA-Z0-9_]*__|[0-9_][A-Za-z0-9_]+|_)\b/)) {
        return 'error';
    }
    stream.next();
    return null;
}
function tokenString(stream, state) {
    let escaped = false;
    let ch;
    while ((ch = stream.next()) != null) {
        if (ch === '"' && !escaped) {
            state.tokenize = tokenBase;
            break;
        }
        escaped = !escaped && ch === '\\';
    }
    return 'string';
}
function tokenComment(stream, state) {
    let maybeEnd = false;
    let ch;
    while ((ch = stream.next()) != null) {
        if (ch === '/' && maybeEnd) {
            state.tokenize = tokenBase;
            break;
        }
        maybeEnd = (ch === '*');
    }
    return 'comment';
}
function tokenInclude(stream, state) {
    stream.skipToEnd();
    state.tokenize = tokenBase;
    return 'meta';
}
const stanLanguage = _codemirror_language__WEBPACK_IMPORTED_MODULE_0__.StreamLanguage.define(stan);
function stanLang() {
    return stanLanguage;
}


/***/ })

}]);
//# sourceMappingURL=lib_plugin_js.f06c1fd527cf285b976b.js.map