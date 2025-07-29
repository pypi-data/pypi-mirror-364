"use strict";
(self["webpackChunkjupyterlab_nbqueue"] = self["webpackChunkjupyterlab_nbqueue"] || []).push([["lib_index_js"],{

/***/ "./lib/common/types.js":
/*!*****************************!*\
  !*** ./lib/common/types.js ***!
  \*****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   isJobSubmissionSuccess: () => (/* binding */ isJobSubmissionSuccess),
/* harmony export */   validateJobSubmissionRequest: () => (/* binding */ validateJobSubmissionRequest),
/* harmony export */   validateNotebookFile: () => (/* binding */ validateNotebookFile)
/* harmony export */ });
/**
 * Job submission interfaces for API validation
 */
/**
 * Validation utilities for API requests
 */
/** Validates that a NotebookFile has the required fields */
function validateNotebookFile(file) {
    return file &&
        typeof file.name === 'string' &&
        typeof file.path === 'string' &&
        file.name.endsWith('.ipynb');
}
/** Validates that a JobSubmissionRequest has all required fields */
function validateJobSubmissionRequest(request) {
    if (!request)
        return false;
    const requiredFields = ['notebook_file', 'output_path', 'cpu', 'ram'];
    for (const field of requiredFields) {
        if (!request[field])
            return false;
    }
    // Validate notebook_file structure
    if (!validateNotebookFile(request.notebook_file))
        return false;
    // Validate CPU is a valid number
    const cpu = parseFloat(String(request.cpu));
    if (isNaN(cpu) || cpu <= 0)
        return false;
    // Validate RAM format (number optionally followed by unit)
    const ramPattern = /^\d+(\.\d+)?(Gi|G|Mi|M)?$/;
    if (!ramPattern.test(String(request.ram).trim()))
        return false;
    return true;
}
/** Type guard to check if response is a successful job submission */
function isJobSubmissionSuccess(response) {
    return response &&
        typeof response.success === 'boolean' &&
        typeof response.job_id === 'string' &&
        typeof response.kubectl_output === 'string';
}


/***/ }),

/***/ "./lib/components/NBQueueComponent.js":
/*!********************************************!*\
  !*** ./lib/components/NBQueueComponent.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material_Autocomplete__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @mui/material/Autocomplete */ "./node_modules/@mui/material/Autocomplete/Autocomplete.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../handler */ "./lib/handler.js");
/* harmony import */ var _common_types__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../common/types */ "./lib/common/types.js");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__);
/**
 * NBQueue Job Submission Component
 *
 * React component that provides a dialog interface for submitting notebooks
 * to the execution queue with configurable parameters (CPU, RAM, container image, etc.).
 */






/**
 * Main component for job submission dialog
 *
 * Renders a Material-UI dialog with form fields for configuring
 * notebook execution parameters and submitting to the queue.
 */
const NBQueueComponent = (props) => {
    // Dialog state management
    const [open, setOpen] = react__WEBPACK_IMPORTED_MODULE_1___default().useState(true);
    const [file] = react__WEBPACK_IMPORTED_MODULE_1___default().useState(props.file);
    const [renderingFolder] = react__WEBPACK_IMPORTED_MODULE_1___default().useState(props.renderingFolder);
    const [fullWidth] = react__WEBPACK_IMPORTED_MODULE_1___default().useState(true);
    const [maxWidth] = react__WEBPACK_IMPORTED_MODULE_1___default().useState('md');
    const [selectedOutputPath, setSelectedOutputPath] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(null);
    // State for accessible directories
    const [accessibleDirectories, setAccessibleDirectories] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)([]);
    const [showAdvanced, setShowAdvanced] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(false);
    // New state variables for container image and conda environment
    const [containerImage, setContainerImage] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)('');
    const [condaEnv, setCondaEnv] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)('');
    const [condaEnvError, setCondaEnvError] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(false);
    (0,react__WEBPACK_IMPORTED_MODULE_1__.useEffect)(() => {
        // Fetch accessible directories from the handler
        const fetchDirectories = async () => {
            try {
                const response = await (0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('accessible-directories', {
                    method: 'POST',
                    body: JSON.stringify({ root_path: renderingFolder }),
                });
                // Map response to extract paths as strings
                const directoryPaths = response.accessible_directories.map(dir => dir.path);
                setAccessibleDirectories(directoryPaths);
            }
            catch (error) {
                console.error('Error fetching accessible directories:', error);
            }
        };
        fetchDirectories();
    }, [renderingFolder]);
    /** Closes the dialog */
    const handleClose = () => {
        setOpen(false);
    };
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement((react__WEBPACK_IMPORTED_MODULE_1___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Dialog, { open: open, onClose: handleClose, fullWidth: fullWidth, maxWidth: maxWidth, PaperProps: {
                component: 'form',
                onSubmit: async (event) => {
                    event.preventDefault();
                    const formData = new FormData(event.currentTarget);
                    const formJson = Object.fromEntries(formData.entries());
                    // Validación: si container-image tiene valor, conda-environment es obligatorio
                    if (containerImage && !condaEnv) {
                        setCondaEnvError(true);
                        return;
                    }
                    // Build payload for API request
                    const payload = {
                        notebook_file: file,
                        image: containerImage || formJson['container-image'],
                        conda_env: condaEnv || formJson['conda-environment'],
                        output_path: selectedOutputPath !== null && selectedOutputPath !== void 0 ? selectedOutputPath : '',
                        cpu: formJson['cpu-number'],
                        ram: formJson['ram-number']
                    };
                    // Validate payload before sending
                    if (!(0,_common_types__WEBPACK_IMPORTED_MODULE_4__.validateJobSubmissionRequest)(payload)) {
                        console.error('Invalid job submission payload:', payload);
                        return;
                    }
                    // Submit job with progress notifications
                    _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.Notification.promise((0,_handler__WEBPACK_IMPORTED_MODULE_3__.requestAPI)('submit', {
                        method: 'POST',
                        body: JSON.stringify(payload),
                    }), {
                        pending: {
                            message: 'Sending info to gRPC server',
                        },
                        success: {
                            message: (result) => {
                                const response = result;
                                if ((0,_common_types__WEBPACK_IMPORTED_MODULE_4__.isJobSubmissionSuccess)(response)) {
                                    return response.success ?
                                        (response.kubectl_output || 'Job submitted successfully') :
                                        (response.error_message || 'Job submission failed');
                                }
                                return 'Job submitted successfully';
                            },
                            options: { autoClose: 3000 },
                        },
                        error: {
                            message: (reason) => `Error sending info. Reason: ${typeof reason === 'object' && reason.error ? reason.error : reason}`,
                            options: { autoClose: 3000 },
                        },
                    });
                    handleClose();
                }
            } },
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.DialogTitle, null, "Parameters"),
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.DialogContent, null,
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.DialogContentText, null, "Please fill the form with your parameters."),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.TextField, { required: true, id: "cpu-number", name: "cpu-number", defaultValue: "1", label: "CPU", type: "number", variant: "standard", margin: "dense", fullWidth: true, autoFocus: true, inputProps: { min: 1, max: 32, step: 1 } }),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.TextField, { required: true, id: "ram-number", name: "ram-number", defaultValue: "1", label: "RAM", type: "number", variant: "standard", margin: "dense", fullWidth: true, inputProps: { min: 1, max: 32, step: 1 } }),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material_Autocomplete__WEBPACK_IMPORTED_MODULE_5__["default"], { id: "output-path", options: accessibleDirectories, value: selectedOutputPath, onChange: (_, newValue) => setSelectedOutputPath(newValue), renderInput: (params) => (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.TextField, { ...params, label: "Output Path", variant: "standard", margin: "dense", fullWidth: true, required: true })) }),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Button, { onClick: () => setShowAdvanced((prev) => !prev), color: "primary", style: { marginTop: 16, marginBottom: 8 } }, showAdvanced ? 'Hide Advanced Options' : 'Show Advanced Options'),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Collapse, { in: showAdvanced },
                    react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", null,
                        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.TextField, { id: "container-image", name: "container-image", label: "Container Image", variant: "standard", margin: "dense", fullWidth: true, style: { marginTop: 8 }, value: containerImage, onChange: e => {
                                setContainerImage(e.target.value);
                                setCondaEnvError(false);
                            } }),
                        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.TextField, { id: "conda-environment", name: "conda-environment", label: "Conda environment", variant: "standard", margin: "dense", fullWidth: true, style: { marginTop: 8 }, value: condaEnv, onChange: e => {
                                setCondaEnv(e.target.value);
                                setCondaEnvError(false);
                            }, error: condaEnvError, helperText: condaEnvError ? 'Conda environment is required if container image is set.' : '' })))),
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.DialogActions, null,
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Button, { onClick: handleClose }, "Cancel"),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Button, { type: "submit" }, "Send")))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (NBQueueComponent);


/***/ }),

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);
/**
 * API Handler for NBQueue Extension
 *
 * Provides utility functions for making HTTP requests to the NBQueue backend API.
 * Handles authentication, error processing, and response formatting.
 */


/**
 * Makes authenticated requests to the NBQueue API extension
 *
 * @param endPoint - API REST endpoint for the extension (default: '')
 * @param init - Initial values for the request (headers, method, body, etc.)
 * @returns Promise resolving to the parsed response body
 * @throws {ServerConnection.NetworkError} When network request fails
 * @throws {ServerConnection.ResponseError} When server returns error response
 */
async function requestAPI(endPoint = '', init = {}) {
    // Build request URL using Jupyter server settings
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'jupyterlab-nbqueue', // API namespace for this extension
    endPoint);
    let response;
    try {
        // Make authenticated request through Jupyter server connection
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    // Parse response body as text first, then try JSON parsing
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log('Not a JSON response body.', response);
        }
    }
    // Check for HTTP error status codes
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ButtonExtension: () => (/* binding */ ButtonExtension),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/filebrowser */ "webpack/sharing/consume/default/@jupyterlab/filebrowser");
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _widgets_NBQueueWidget__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./widgets/NBQueueWidget */ "./lib/widgets/NBQueueWidget.js");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./utils */ "./lib/utils.js");
/* harmony import */ var lodash__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! lodash */ "webpack/sharing/consume/default/lodash/lodash");
/* harmony import */ var lodash__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(lodash__WEBPACK_IMPORTED_MODULE_7__);
/**
 * JupyterLab NBQueue Extension
 *
 * This extension provides functionality to queue notebook executions
 * in Kubernetes environments through a sidebar interface and context menu.
 */







// import { NBQueueSideBarWidget } from './widgets/NBQueueSideBarWidget';



/** Plugin identifier for settings and registration */
const PLUGIN_ID = 'jupyterlab-nbqueue:plugin';
/**
 * Activates the NBQueue extension
 * @param app - The JupyterLab application instance
 * @param factory - File browser factory for file operations
 * @param palette - Command palette for registering commands
 * @param mainMenu - Main menu for adding menu items
 * @param settings - Settings registry for configuration
 */
const activate = async (app, factory, palette, mainMenu, settings) => {
    console.log('JupyterLab extension jupyterlab-nbqueue is activated!');
    // Initialize user service and log user information for debugging
    const user = app.serviceManager.user;
    user.ready.then(() => {
        console.debug("Identity:", user.identity);
        console.debug("Permissions:", user.permissions);
    });
    // Load rendering folder configuration from settings
    let renderingFolder = '';
    await Promise.all([settings.load(PLUGIN_ID)])
        .then(([setting]) => {
        renderingFolder = (0,_utils__WEBPACK_IMPORTED_MODULE_8__.loadSetting)(setting);
    }).catch((reason) => {
        console.error(`Something went wrong when getting the current rendering folder.\n${reason}`);
    });
    // Validate rendering folder configuration
    if (lodash__WEBPACK_IMPORTED_MODULE_7___default().isEqual(renderingFolder, "")) {
        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Notification.warning('Rendering Folder is not configured');
        return;
    }
    // Create and configure the sidebar widget for job management
    // const sideBarContent = new NBQueueSideBarWidget(renderingFolder);
    // const sideBarWidget = new MainAreaWidget<NBQueueSideBarWidget>({
    //   content: sideBarContent
    // });
    // // Configure sidebar widget appearance and add to shell
    // sideBarWidget.toolbar.hide();
    // sideBarWidget.title.icon = runIcon;
    // sideBarWidget.title.caption = 'NBQueue job list';
    // app.shell.add(sideBarWidget, 'right', { rank: 501 });
    // Register command for sending notebooks to queue via context menu
    app.commands.addCommand('jupyterlab-nbqueue:open', {
        label: 'NBQueue: Send to queue',
        caption: "Send selected notebook to execution queue",
        icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_2__.runIcon,
        execute: async () => {
            var _a;
            // Reload settings to ensure we have the latest configuration
            await Promise.all([settings.load(PLUGIN_ID)])
                .then(([setting]) => {
                renderingFolder = (0,_utils__WEBPACK_IMPORTED_MODULE_8__.loadSetting)(setting);
            }).catch((reason) => {
                console.error(`Something went wrong when getting the current rendering folder.\n${reason}`);
            });
            // Validate configuration before proceeding
            if (lodash__WEBPACK_IMPORTED_MODULE_7___default().isEqual(renderingFolder, "")) {
                _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Notification.warning('Rendering Folder is not configured');
                return;
            }
            // Get the currently selected file from file browser
            const file = (_a = factory.tracker.currentWidget) === null || _a === void 0 ? void 0 : _a.selectedItems().next().value;
            if (file) {
                // Create and display the job submission widget
                const widget = new _widgets_NBQueueWidget__WEBPACK_IMPORTED_MODULE_9__.NBQueueWidget(file, renderingFolder);
                widget.title.label = "NBQueue metadata";
                _lumino_widgets__WEBPACK_IMPORTED_MODULE_3__.Widget.attach(widget, document.body);
            }
        }
    });
    // Add context menu item for notebook files
    app.contextMenu.addItem({
        command: 'jupyterlab-nbqueue:open',
        selector: ".jp-DirListing-item[data-file-type=\"notebook\"]",
        rank: 0
    });
    // Add toolbar button extension to notebook panels
    app.docRegistry.addWidgetExtension('Notebook', new ButtonExtension(settings));
};
/**
 * Main plugin configuration object
 */
const plugin = {
    id: 'jupyterlab-nbqueue:plugin',
    description: 'A JupyterLab extension for queuing notebook executions in Kubernetes.',
    autoStart: true,
    requires: [_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_0__.IFileBrowserFactory, _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ICommandPalette, _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_1__.IMainMenu, _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6__.ISettingRegistry],
    activate
};
/**
 * Document registry extension that adds a toolbar button to notebook panels
 * for quick access to NBQueue functionality
 */
class ButtonExtension {
    constructor(settings) {
        this.settings = settings;
    }
    /**
     * Creates a new toolbar button for the notebook panel
     * @param panel - The notebook panel to extend
     * @param context - The document context
     * @returns Disposable for cleanup
     */
    createNew(panel, context) {
        /**
         * Handler for sending the current notebook to queue
         */
        const sendToQueue = async () => {
            let renderingFolder = '';
            // Load current settings
            await Promise.all([this.settings.load(PLUGIN_ID)])
                .then(([setting]) => {
                renderingFolder = (0,_utils__WEBPACK_IMPORTED_MODULE_8__.loadSetting)(setting);
                console.log(renderingFolder);
            }).catch((reason) => {
                console.error(`Something went wrong when getting the current rendering folder.\n${reason}`);
            });
            // Validate configuration
            if (lodash__WEBPACK_IMPORTED_MODULE_7___default().isEqual(renderingFolder, "")) {
                _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.Notification.warning('Rendering Folder is not configured');
                return;
            }
            // Create and show the job submission widget
            const widget = new _widgets_NBQueueWidget__WEBPACK_IMPORTED_MODULE_9__.NBQueueWidget(context.contentsModel, renderingFolder);
            widget.title.label = "NBQueue metadata";
            _lumino_widgets__WEBPACK_IMPORTED_MODULE_3__.Widget.attach(widget, document.body);
        };
        // Create the toolbar button
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_5__.ToolbarButton({
            className: 'nbqueue-submit',
            label: 'NBQueue: Send to queue',
            onClick: sendToQueue,
            tooltip: 'Send notebook to execution queue',
        });
        // Insert button into toolbar
        panel.toolbar.insertItem(10, 'clearOutputs', button);
        // Return disposable for cleanup
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_4__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/utils.js":
/*!**********************!*\
  !*** ./lib/utils.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   loadSetting: () => (/* binding */ loadSetting)
/* harmony export */ });
/**
 * Utility Functions for NBQueue Extension
 *
 * Provides helper functions for loading and processing extension settings.
 */
/**
 * Loads the rendering folder setting from the extension configuration
 *
 * @param setting - The loaded settings instance for this extension
 * @returns The configured rendering folder path as a string
 */
function loadSetting(setting) {
    // Extract rendering folder from composite settings
    let renderingFolder = setting.get('renderingFolder').composite;
    console.log(`Rendering Folder Loading Settings = ${renderingFolder}`);
    return renderingFolder;
}


/***/ }),

/***/ "./lib/widgets/NBQueueWidget.js":
/*!**************************************!*\
  !*** ./lib/widgets/NBQueueWidget.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   NBQueueWidget: () => (/* binding */ NBQueueWidget)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components_NBQueueComponent__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../components/NBQueueComponent */ "./lib/components/NBQueueComponent.js");
/**
 * NBQueue Widget
 *
 * A ReactWidget wrapper for the NBQueueComponent that provides
 * a styled container for the job submission dialog.
 */



/**
 * Widget class for NBQueue job submission
 *
 * Wraps the NBQueueComponent in a JupyterLab ReactWidget
 * with appropriate styling and dimensions.
 */
class NBQueueWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    /**
     * Constructor for NBQueueWidget
     * @param file - File object containing notebook information
     * @param renderingFolder - Output folder path for job results
     */
    constructor(file, renderingFolder) {
        super();
        this.file = file;
        this.renderingFolder = renderingFolder;
    }
    /**
     * Renders the widget content
     * @returns JSX element with styled container and NBQueueComponent
     */
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { style: {
                width: '400px',
                minWidth: '400px',
                display: 'flex',
                flexDirection: 'column',
                background: 'var(--jp-layout-color1)'
            } },
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_components_NBQueueComponent__WEBPACK_IMPORTED_MODULE_2__["default"], { file: this.file, renderingFolder: this.renderingFolder })));
    }
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.6dc06a1c2b0193c50e6e.js.map