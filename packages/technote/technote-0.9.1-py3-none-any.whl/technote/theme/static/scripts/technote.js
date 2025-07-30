/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	// The require scope
/******/ 	var __webpack_require__ = {};
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be isolated against other entry modules.
(() => {
var __webpack_exports__ = {};
/*!*****************************************!*\
  !*** ./src/assets/styles/technote.scss ***!
  \*****************************************/
__webpack_require__.r(__webpack_exports__);
// extracted by mini-css-extract-plugin

})();

// This entry need to be wrapped in an IIFE because it need to be isolated against other entry modules.
(() => {
/*!****************************************!*\
  !*** ./src/assets/scripts/technote.js ***!
  \****************************************/
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "documentReady": () => (/* binding */ documentReady)
/* harmony export */ });
/*
 * Support a configurable colour theme.
 *
 * This script is based on pydata-sphinx-theme:
 * https://github.com/pydata/pydata-sphinx-theme
 */

var prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

/**
 * Set the the body theme to the one specified by the user's browser/system
 * settings.
 *
 * @param {event} e
 */
function handleAutoTheme(e) {
  document.documentElement.dataset.theme = prefersDark.matches
    ? 'dark'
    : 'light';
}

/**
 * Set the theme using the specified mode.
 *
 * @param {str} mode - The theme mode to set. One of ["auto", "dark", "light"]
 */
function setTheme(mode) {
  if (mode !== 'light' && mode !== 'dark' && mode !== 'auto') {
    console.error(`Got invalid theme mode: ${mode}. Resetting to auto.`);
    mode = 'auto';
  }

  var colorScheme = prefersDark.matches ? 'dark' : 'light';
  document.documentElement.dataset.mode = mode;
  var theme = mode == 'auto' ? colorScheme : mode;

  // save mode and theme
  localStorage.setItem('mode', mode);
  localStorage.setItem('theme', theme);
  console.log(`[Technote]: Changed to ${mode} mode using the ${theme} theme.`);

  // add a listener if set on auto
  prefersDark.onchange = mode == 'auto' ? handleAutoTheme : '';
}

/**
 * add the theme listener on the btns of the navbar
 */
function addThemeModeListener() {
  // the theme was set a first time using the initial mini-script
  // running setMode will ensure the use of the dark mode if auto is selected
  setTheme(document.documentElement.dataset.mode);

  // Attach event handlers for toggling themes colors
  // document.querySelectorAll(".theme-switch-button").forEach((el) => {
  //   el.addEventListener("click", cycleMode);
  // });
}

/**
 * Execute a method if DOM has finished loading
 *
 * @param {function} callback the method to execute
 */
function documentReady(callback) {
  if (document.readyState != 'loading') callback();
  else document.addEventListener('DOMContentLoaded', callback);
}

/**
 * Add handlers.
 */
documentReady(addThemeModeListener);

/**
 * Add listener for contents outline navigation button.
 */
function toggleContentsOutline() {
  document
    .querySelector('#technote-contents-toggle')
    .classList.toggle('technote-contents-toggle--active');
  document
    .querySelector('.technote-outline-container')
    .classList.toggle('technote-outline-container--visible');

  const showLabel =
    '<svg class="technote-svg-icon"><use href="#svg-octicon-three-bars-16"></svg> Contents';
  const hideLabel =
    '<svg class="technote-svg-icon"><use href="#svg-octicon-filled-x-16"></svg> Hide contents';

  document.querySelector(
    '#technote-contents-toggle.technote-contents-toggle--active'
  )
    ? (document.querySelector('#technote-contents-toggle').innerHTML =
        hideLabel)
    : (document.querySelector('#technote-contents-toggle').innerHTML =
        showLabel);
}

documentReady(function () {
  document
    .querySelector('#technote-contents-toggle')
    .addEventListener('click', toggleContentsOutline);

  document.querySelectorAll('.technote-outline-container a').forEach((el) => {
    el.addEventListener('click', toggleContentsOutline);
  });
  console.log(
    '[Technote]: Added listener for contents outline navigation button.'
  );
});

})();

/******/ })()
;
//# sourceMappingURL=technote.js.map