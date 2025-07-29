"use strict";
(self["webpackChunknbtest_lab_extension"] = self["webpackChunknbtest_lab_extension"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/rendermime */ "webpack/sharing/consume/default/@jupyterlab/rendermime");
/* harmony import */ var _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/cells */ "webpack/sharing/consume/default/@jupyterlab/cells");
/* harmony import */ var _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_cells__WEBPACK_IMPORTED_MODULE_5__);






// Signal for updating the status display of the ENV variable
class ToggleSignal {
    constructor() {
        this._stateChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_3__.Signal(this);
    }
    get stateChanged() {
        return this._stateChanged;
    }
    emitState(value) {
        this._stateChanged.emit(value);
    }
}
const toggleSignal = new ToggleSignal();
let status = 0; // Track status locally for the ENV variable
// Define constants for the metadata key and assertion prefix
const METADATA_KEY = 'nbtest_hidden_asserts';
const ASSERT_PREFIX = 'nbtest.assert_';
/**
 * The main extension plugin.
 */
const plugin = {
    id: 'nbtest_lab_extension:plugin',
    autoStart: true,
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ICommandPalette, _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.INotebookTracker, _jupyterlab_rendermime__WEBPACK_IMPORTED_MODULE_2__.IRenderMimeRegistry],
    activate: (app, palette, tracker) => {
        const { commands } = app;
        const toggleEnvCommand = 'nbtest:toggle-asserts-env';
        const toggleVisibilityCommand = 'nbtest:toggle-visibility';
        // COMMAND 1: Toggle NBTEST_RUN_ASSERTS environment variable
        commands.addCommand(toggleEnvCommand, {
            label: 'Toggle NBTEST_RUN_ASSERTS Env Var',
            execute: async () => {
                const currentNotebook = tracker.currentWidget;
                if (!currentNotebook) {
                    return;
                }
                const session = currentNotebook.sessionContext.session;
                if (!session || !session.kernel) {
                    return;
                }
                const code = `
import os
os.environ["NBTEST_RUN_ASSERTS"] = "1" if os.environ.get("NBTEST_RUN_ASSERTS", "0") != "1" else "0"
print(os.environ["NBTEST_RUN_ASSERTS"])
        `;
                const future = session.kernel.requestExecute({ code });
                future.onIOPub = msg => {
                    if (msg.header.msg_type === 'stream') {
                        const newStatusValue = msg.content.text.trim();
                        status = newStatusValue === '1' ? 1 : 0;
                        toggleSignal.emitState(status === 1 ? 'ON' : 'OFF');
                    }
                };
                await future.done;
            }
        });
        // COMMAND 2: Completely hide or show nbtest.assert_* lines
        commands.addCommand(toggleVisibilityCommand, {
            label: 'Hide/Show NBTest Assertions',
            execute: () => {
                const panel = tracker.currentWidget;
                if (!panel) {
                    return;
                }
                const notebookModel = panel.content.model;
                if (!notebookModel) {
                    return;
                }
                const cells = notebookModel.cells;
                let shouldHide = true;
                // Check if any cell has hidden assertions in its metadata
                for (let i = 0; i < cells.length; i++) {
                    const cell = cells.get(i);
                    if (cell.type !== 'code') {
                        continue;
                    }
                    if (cell.getMetadata(METADATA_KEY) !== undefined) {
                        shouldHide = false;
                        break;
                    }
                }
                // Apply the determined action
                for (let i = 0; i < cells.length; i++) {
                    const cellModel = cells.get(i);
                    if (cellModel.type !== 'code') {
                        continue;
                    }
                    if (shouldHide) {
                        const sourceLines = cellModel.sharedModel.getSource().split('\n');
                        const visibleLines = [];
                        const hiddenLines = [];
                        sourceLines.forEach((line) => {
                            if (line.trim().startsWith(ASSERT_PREFIX)) {
                                hiddenLines.push(line);
                            }
                            else {
                                visibleLines.push(line);
                            }
                        });
                        if (hiddenLines.length > 0) {
                            cellModel.sharedModel.setSource(visibleLines.join('\n'));
                            cellModel.setMetadata(METADATA_KEY, hiddenLines);
                        }
                    }
                    else {
                        const hiddenLines = cellModel.getMetadata(METADATA_KEY);
                        if (hiddenLines) {
                            const visibleLines = cellModel.sharedModel.getSource();
                            const separator = visibleLines.trim().length > 0 ? '\n' : '';
                            cellModel.sharedModel.setSource(visibleLines + separator + hiddenLines.join('\n'));
                            cellModel.deleteMetadata(METADATA_KEY);
                        }
                    }
                }
            }
        });
        // Add commands to the palette
        palette.addItem({ command: toggleEnvCommand, category: 'NBTest' });
        palette.addItem({ command: toggleVisibilityCommand, category: 'NBTest' });
        // Add buttons and functionality to any new notebook
        tracker.widgetAdded.connect((sender, panel) => {
            const envButton = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
                label: 'Toggle Assertions',
                tooltip: 'Toggle NBTEST_RUN_ASSERTS Environment Variable',
                onClick: () => commands.execute(toggleEnvCommand)
            });
            const statusDisplay = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_4__.Widget();
            statusDisplay.node.textContent = 'NBTest Status: OFF';
            statusDisplay.node.style.marginLeft = '4px';
            statusDisplay.node.style.marginRight = '8px';
            toggleSignal.stateChanged.connect((_, newStatus) => {
                statusDisplay.node.textContent = `NBTest Status: ${newStatus}`;
            });
            const visibilityButton = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
                label: 'Hide/Show Assertions',
                tooltip: 'Completely hide or show nbtest assertions',
                onClick: () => commands.execute(toggleVisibilityCommand)
            });
            panel.toolbar.addItem('toggleAssertsEnv', envButton);
            panel.toolbar.addItem('assertsStatus', statusDisplay);
            panel.toolbar.addItem('toggleVisibility', visibilityButton);
            const highlightAssertCells = () => {
                panel.content.widgets.forEach(cell => {
                    const model = cell.model;
                    const node = cell.node;
                    let hasAssertions = false;
                    if (model instanceof _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_5__.CodeCellModel) {
                        const source = model.sharedModel.getSource();
                        const hasVisibleAssertions = /nbtest\.assert_\w+/.test(source);
                        const hasHiddenAssertions = model.getMetadata(METADATA_KEY) !== undefined;
                        hasAssertions = hasVisibleAssertions || hasHiddenAssertions;
                    }
                    if (hasAssertions) {
                        node.style.borderLeft = '4px solid #f39c12';
                        node.style.backgroundColor = 'rgba(243, 156, 18, 0.07)';
                    }
                    else {
                        node.style.borderLeft = '';
                        node.style.backgroundColor = '';
                    }
                });
            };
            // Run highlighting once the panel is ready.
            panel.revealed.then(() => {
                highlightAssertCells();
            });
            // Re-run highlighting efficiently on any content change.
            if (panel.content.model) {
                panel.content.model.contentChanged.connect(() => {
                    highlightAssertCells();
                });
            }
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.8506b79d5f15833e9a74.js.map