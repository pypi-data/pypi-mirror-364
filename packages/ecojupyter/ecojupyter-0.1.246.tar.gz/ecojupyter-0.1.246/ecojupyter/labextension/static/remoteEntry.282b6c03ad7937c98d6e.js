var _JUPYTERLAB;
/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "webpack/container/entry/ecojupyter":
/*!***********************!*\
  !*** container entry ***!
  \***********************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

var moduleMap = {
	"./index": () => {
		return Promise.all([__webpack_require__.e("vendors-node_modules_prop-types_index_js"), __webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_development_esm_js"), __webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_extends_js-node_modules_emotion_serialize_dist-051195"), __webpack_require__.e("vendors-node_modules_mui_material_Box_Box_js-node_modules_mui_material_Button_Button_js-node_-c551e4"), __webpack_require__.e("vendors-node_modules_mui_icons-material_esm_AddCircleOutlineRounded_js-node_modules_mui_icons-b8db0d"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_react-dom"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-2f734f"), __webpack_require__.e("lib_index_js")]).then(() => (() => ((__webpack_require__(/*! ./lib/index.js */ "./lib/index.js")))));
	},
	"./extension": () => {
		return Promise.all([__webpack_require__.e("vendors-node_modules_prop-types_index_js"), __webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_development_esm_js"), __webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_extends_js-node_modules_emotion_serialize_dist-051195"), __webpack_require__.e("vendors-node_modules_mui_material_Box_Box_js-node_modules_mui_material_Button_Button_js-node_-c551e4"), __webpack_require__.e("vendors-node_modules_mui_icons-material_esm_AddCircleOutlineRounded_js-node_modules_mui_icons-b8db0d"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_react-dom"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-2f734f"), __webpack_require__.e("lib_index_js")]).then(() => (() => ((__webpack_require__(/*! ./lib/index.js */ "./lib/index.js")))));
	},
	"./style": () => {
		return __webpack_require__.e("style_index_js").then(() => (() => ((__webpack_require__(/*! ./style/index.js */ "./style/index.js")))));
	}
};
var get = (module, getScope) => {
	__webpack_require__.R = getScope;
	getScope = (
		__webpack_require__.o(moduleMap, module)
			? moduleMap[module]()
			: Promise.resolve().then(() => {
				throw new Error('Module "' + module + '" does not exist in container.');
			})
	);
	__webpack_require__.R = undefined;
	return getScope;
};
var init = (shareScope, initScope) => {
	if (!__webpack_require__.S) return;
	var name = "default"
	var oldScope = __webpack_require__.S[name];
	if(oldScope && oldScope !== shareScope) throw new Error("Container initialization failed as it has already been initialized with a different share scope");
	__webpack_require__.S[name] = shareScope;
	return __webpack_require__.I(name, initScope);
};

// This exports getters to disallow modifications
__webpack_require__.d(exports, {
	get: () => (get),
	init: () => (init)
});

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			id: moduleId,
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = __webpack_modules__;
/******/ 	
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = __webpack_module_cache__;
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
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
/******/ 	/* webpack/runtime/ensure chunk */
/******/ 	(() => {
/******/ 		__webpack_require__.f = {};
/******/ 		// This file contains only the entry chunk.
/******/ 		// The chunk loading function for additional chunks
/******/ 		__webpack_require__.e = (chunkId) => {
/******/ 			return Promise.all(Object.keys(__webpack_require__.f).reduce((promises, key) => {
/******/ 				__webpack_require__.f[key](chunkId, promises);
/******/ 				return promises;
/******/ 			}, []));
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/get javascript chunk filename */
/******/ 	(() => {
/******/ 		// This function allow to reference async chunks
/******/ 		__webpack_require__.u = (chunkId) => {
/******/ 			// return url for filenames based on template
/******/ 			return "" + chunkId + "." + {"vendors-node_modules_prop-types_index_js":"44474126766786d97e01","vendors-node_modules_emotion_cache_dist_emotion-cache_browser_development_esm_js":"3234098e280ca6a7ba89","vendors-node_modules_babel_runtime_helpers_esm_extends_js-node_modules_emotion_serialize_dist-051195":"7caa56513d73bb4569eb","vendors-node_modules_mui_material_Box_Box_js-node_modules_mui_material_Button_Button_js-node_-c551e4":"5b2c81527810c2a78935","vendors-node_modules_mui_icons-material_esm_AddCircleOutlineRounded_js-node_modules_mui_icons-b8db0d":"bb3ee2a9fded0404d798","lib_index_js":"676b10642a1e590decc2","style_index_js":"ca437ccd8977d894a7c9","vendors-node_modules_emotion_react_dist_emotion-react_browser_development_esm_js":"6dfdcf71625dd4773cd4","node_modules_emotion_use-insertion-effect-with-fallbacks_dist_emotion-use-insertion-effect-wi-3c9bb40":"6bfff6cbd48a0cedd7d7","vendors-node_modules_emotion_styled_dist_emotion-styled_browser_development_esm_js":"d1a990d1c6ebba7dc6ab","vendors-node_modules_mui_material_index_js":"c41610117e604d211b27","vendors-node_modules_visx_axis_esm_index_js":"a2769b52e91d1bdd3938","node_modules_visx_group_esm_Group_js-_a7da0":"e95bc8ccd4853b0298ca","node_modules_visx_event_esm_index_js":"93bc365bfa9feef681b7","vendors-node_modules_visx_scale_esm_index_js":"08d64f2d5a4985fb835e","node_modules_d3-array_src_bisector_js-node_modules_d3-array_src_max_js-node_modules_d3-array_-0a7de0":"cf2130cf6921c60e9ba5","vendors-node_modules_visx_shape_esm_index_js":"bbc127223e607e59a397","node_modules_visx_group_esm_Group_js-_a7da1":"7d088c979644ae960ea1","vendors-node_modules_visx_tooltip_esm_index_js":"74327389cad56784977a","node_modules_classnames_index_js":"21a6215cb843a29dc76e","node_modules_dayjs_dayjs_min_js":"67bf215857d5e3e32d55","node_modules_emotion_use-insertion-effect-with-fallbacks_dist_emotion-use-insertion-effect-wi-3c9bb41":"f45d2ef005c471e81665"}[chunkId] + ".js";
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/global */
/******/ 	(() => {
/******/ 		__webpack_require__.g = (function() {
/******/ 			if (typeof globalThis === 'object') return globalThis;
/******/ 			try {
/******/ 				return this || new Function('return this')();
/******/ 			} catch (e) {
/******/ 				if (typeof window === 'object') return window;
/******/ 			}
/******/ 		})();
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/load script */
/******/ 	(() => {
/******/ 		var inProgress = {};
/******/ 		var dataWebpackPrefix = "ecojupyter:";
/******/ 		// loadScript function to load a script via script tag
/******/ 		__webpack_require__.l = (url, done, key, chunkId) => {
/******/ 			if(inProgress[url]) { inProgress[url].push(done); return; }
/******/ 			var script, needAttach;
/******/ 			if(key !== undefined) {
/******/ 				var scripts = document.getElementsByTagName("script");
/******/ 				for(var i = 0; i < scripts.length; i++) {
/******/ 					var s = scripts[i];
/******/ 					if(s.getAttribute("src") == url || s.getAttribute("data-webpack") == dataWebpackPrefix + key) { script = s; break; }
/******/ 				}
/******/ 			}
/******/ 			if(!script) {
/******/ 				needAttach = true;
/******/ 				script = document.createElement('script');
/******/ 		
/******/ 				script.charset = 'utf-8';
/******/ 				script.timeout = 120;
/******/ 				if (__webpack_require__.nc) {
/******/ 					script.setAttribute("nonce", __webpack_require__.nc);
/******/ 				}
/******/ 				script.setAttribute("data-webpack", dataWebpackPrefix + key);
/******/ 		
/******/ 				script.src = url;
/******/ 			}
/******/ 			inProgress[url] = [done];
/******/ 			var onScriptComplete = (prev, event) => {
/******/ 				// avoid mem leaks in IE.
/******/ 				script.onerror = script.onload = null;
/******/ 				clearTimeout(timeout);
/******/ 				var doneFns = inProgress[url];
/******/ 				delete inProgress[url];
/******/ 				script.parentNode && script.parentNode.removeChild(script);
/******/ 				doneFns && doneFns.forEach((fn) => (fn(event)));
/******/ 				if(prev) return prev(event);
/******/ 			}
/******/ 			var timeout = setTimeout(onScriptComplete.bind(null, undefined, { type: 'timeout', target: script }), 120000);
/******/ 			script.onerror = onScriptComplete.bind(null, script.onerror);
/******/ 			script.onload = onScriptComplete.bind(null, script.onload);
/******/ 			needAttach && document.head.appendChild(script);
/******/ 		};
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
/******/ 	/* webpack/runtime/sharing */
/******/ 	(() => {
/******/ 		__webpack_require__.S = {};
/******/ 		var initPromises = {};
/******/ 		var initTokens = {};
/******/ 		__webpack_require__.I = (name, initScope) => {
/******/ 			if(!initScope) initScope = [];
/******/ 			// handling circular init calls
/******/ 			var initToken = initTokens[name];
/******/ 			if(!initToken) initToken = initTokens[name] = {};
/******/ 			if(initScope.indexOf(initToken) >= 0) return;
/******/ 			initScope.push(initToken);
/******/ 			// only runs once
/******/ 			if(initPromises[name]) return initPromises[name];
/******/ 			// creates a new share scope if needed
/******/ 			if(!__webpack_require__.o(__webpack_require__.S, name)) __webpack_require__.S[name] = {};
/******/ 			// runs all init snippets from all modules reachable
/******/ 			var scope = __webpack_require__.S[name];
/******/ 			var warn = (msg) => {
/******/ 				if (typeof console !== "undefined" && console.warn) console.warn(msg);
/******/ 			};
/******/ 			var uniqueName = "ecojupyter";
/******/ 			var register = (name, version, factory, eager) => {
/******/ 				var versions = scope[name] = scope[name] || {};
/******/ 				var activeVersion = versions[version];
/******/ 				if(!activeVersion || (!activeVersion.loaded && (!eager != !activeVersion.eager ? eager : uniqueName > activeVersion.from))) versions[version] = { get: factory, from: uniqueName, eager: !!eager };
/******/ 			};
/******/ 			var initExternal = (id) => {
/******/ 				var handleError = (err) => (warn("Initialization of sharing external failed: " + err));
/******/ 				try {
/******/ 					var module = __webpack_require__(id);
/******/ 					if(!module) return;
/******/ 					var initFn = (module) => (module && module.init && module.init(__webpack_require__.S[name], initScope))
/******/ 					if(module.then) return promises.push(module.then(initFn, handleError));
/******/ 					var initResult = initFn(module);
/******/ 					if(initResult && initResult.then) return promises.push(initResult['catch'](handleError));
/******/ 				} catch(err) { handleError(err); }
/******/ 			}
/******/ 			var promises = [];
/******/ 			switch(name) {
/******/ 				case "default": {
/******/ 					register("@emotion/react", "11.14.0", () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_development_esm_js"), __webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_extends_js-node_modules_emotion_serialize_dist-051195"), __webpack_require__.e("vendors-node_modules_emotion_react_dist_emotion-react_browser_development_esm_js"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("node_modules_emotion_use-insertion-effect-with-fallbacks_dist_emotion-use-insertion-effect-wi-3c9bb40")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@emotion/react/dist/emotion-react.browser.development.esm.js */ "./node_modules/@emotion/react/dist/emotion-react.browser.development.esm.js"))))));
/******/ 					register("@emotion/styled", "11.14.0", () => (Promise.all([__webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_extends_js-node_modules_emotion_serialize_dist-051195"), __webpack_require__.e("vendors-node_modules_emotion_styled_dist_emotion-styled_browser_development_esm_js"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@emotion/styled/dist/emotion-styled.browser.development.esm.js */ "./node_modules/@emotion/styled/dist/emotion-styled.browser.development.esm.js"))))));
/******/ 					register("@mui/material", "6.4.12", () => (Promise.all([__webpack_require__.e("vendors-node_modules_prop-types_index_js"), __webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_development_esm_js"), __webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_extends_js-node_modules_emotion_serialize_dist-051195"), __webpack_require__.e("vendors-node_modules_mui_material_index_js"), __webpack_require__.e("vendors-node_modules_mui_material_Box_Box_js-node_modules_mui_material_Button_Button_js-node_-c551e4"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_react-dom"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-2f734f")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@mui/material/index.js */ "./node_modules/@mui/material/index.js"))))));
/******/ 					register("@visx/axis", "3.12.0", () => (Promise.all([__webpack_require__.e("vendors-node_modules_prop-types_index_js"), __webpack_require__.e("vendors-node_modules_visx_axis_esm_index_js"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_visx_scale_visx_scale-webpack_sharing_consume_default_visx_sh-ab6f42"), __webpack_require__.e("node_modules_visx_group_esm_Group_js-_a7da0")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@visx/axis/esm/index.js */ "./node_modules/@visx/axis/esm/index.js"))))));
/******/ 					register("@visx/event", "3.12.0", () => (__webpack_require__.e("node_modules_visx_event_esm_index_js").then(() => (() => (__webpack_require__(/*! ./node_modules/@visx/event/esm/index.js */ "./node_modules/@visx/event/esm/index.js"))))));
/******/ 					register("@visx/scale", "3.12.0", () => (Promise.all([__webpack_require__.e("vendors-node_modules_visx_scale_esm_index_js"), __webpack_require__.e("node_modules_d3-array_src_bisector_js-node_modules_d3-array_src_max_js-node_modules_d3-array_-0a7de0")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@visx/scale/esm/index.js */ "./node_modules/@visx/scale/esm/index.js"))))));
/******/ 					register("@visx/shape", "3.12.0", () => (Promise.all([__webpack_require__.e("vendors-node_modules_prop-types_index_js"), __webpack_require__.e("vendors-node_modules_visx_shape_esm_index_js"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("node_modules_visx_group_esm_Group_js-_a7da1")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@visx/shape/esm/index.js */ "./node_modules/@visx/shape/esm/index.js"))))));
/******/ 					register("@visx/tooltip", "3.12.0", () => (Promise.all([__webpack_require__.e("vendors-node_modules_prop-types_index_js"), __webpack_require__.e("vendors-node_modules_visx_tooltip_esm_index_js"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_react-dom"), __webpack_require__.e("node_modules_classnames_index_js")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@visx/tooltip/esm/index.js */ "./node_modules/@visx/tooltip/esm/index.js"))))));
/******/ 					register("dayjs", "1.11.13", () => (__webpack_require__.e("node_modules_dayjs_dayjs_min_js").then(() => (() => (__webpack_require__(/*! ./node_modules/dayjs/dayjs.min.js */ "./node_modules/dayjs/dayjs.min.js"))))));
/******/ 					register("ecojupyter", "0.1.245", () => (Promise.all([__webpack_require__.e("vendors-node_modules_prop-types_index_js"), __webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_development_esm_js"), __webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_extends_js-node_modules_emotion_serialize_dist-051195"), __webpack_require__.e("vendors-node_modules_mui_material_Box_Box_js-node_modules_mui_material_Button_Button_js-node_-c551e4"), __webpack_require__.e("vendors-node_modules_mui_icons-material_esm_AddCircleOutlineRounded_js-node_modules_mui_icons-b8db0d"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_react-dom"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-2f734f"), __webpack_require__.e("lib_index_js")]).then(() => (() => (__webpack_require__(/*! ./lib/index.js */ "./lib/index.js"))))));
/******/ 				}
/******/ 				break;
/******/ 			}
/******/ 			if(!promises.length) return initPromises[name] = 1;
/******/ 			return initPromises[name] = Promise.all(promises).then(() => (initPromises[name] = 1));
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/publicPath */
/******/ 	(() => {
/******/ 		var scriptUrl;
/******/ 		if (__webpack_require__.g.importScripts) scriptUrl = __webpack_require__.g.location + "";
/******/ 		var document = __webpack_require__.g.document;
/******/ 		if (!scriptUrl && document) {
/******/ 			if (document.currentScript && document.currentScript.tagName.toUpperCase() === 'SCRIPT')
/******/ 				scriptUrl = document.currentScript.src;
/******/ 			if (!scriptUrl) {
/******/ 				var scripts = document.getElementsByTagName("script");
/******/ 				if(scripts.length) {
/******/ 					var i = scripts.length - 1;
/******/ 					while (i > -1 && (!scriptUrl || !/^http(s?):/.test(scriptUrl))) scriptUrl = scripts[i--].src;
/******/ 				}
/******/ 			}
/******/ 		}
/******/ 		// When supporting browsers where an automatic publicPath is not supported you must specify an output.publicPath manually via configuration
/******/ 		// or pass an empty string ("") and set the __webpack_public_path__ variable from your code to use your own logic.
/******/ 		if (!scriptUrl) throw new Error("Automatic publicPath is not supported in this browser");
/******/ 		scriptUrl = scriptUrl.replace(/^blob:/, "").replace(/#.*$/, "").replace(/\?.*$/, "").replace(/\/[^\/]+$/, "/");
/******/ 		__webpack_require__.p = scriptUrl;
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/consumes */
/******/ 	(() => {
/******/ 		var parseVersion = (str) => {
/******/ 			// see webpack/lib/util/semver.js for original code
/******/ 			var p=p=>{return p.split(".").map((p=>{return+p==p?+p:p}))},n=/^([^-+]+)?(?:-([^+]+))?(?:\+(.+))?$/.exec(str),r=n[1]?p(n[1]):[];return n[2]&&(r.length++,r.push.apply(r,p(n[2]))),n[3]&&(r.push([]),r.push.apply(r,p(n[3]))),r;
/******/ 		}
/******/ 		var versionLt = (a, b) => {
/******/ 			// see webpack/lib/util/semver.js for original code
/******/ 			a=parseVersion(a),b=parseVersion(b);for(var r=0;;){if(r>=a.length)return r<b.length&&"u"!=(typeof b[r])[0];var e=a[r],n=(typeof e)[0];if(r>=b.length)return"u"==n;var t=b[r],f=(typeof t)[0];if(n!=f)return"o"==n&&"n"==f||("s"==f||"u"==n);if("o"!=n&&"u"!=n&&e!=t)return e<t;r++}
/******/ 		}
/******/ 		var rangeToString = (range) => {
/******/ 			// see webpack/lib/util/semver.js for original code
/******/ 			var r=range[0],n="";if(1===range.length)return"*";if(r+.5){n+=0==r?">=":-1==r?"<":1==r?"^":2==r?"~":r>0?"=":"!=";for(var e=1,a=1;a<range.length;a++){e--,n+="u"==(typeof(t=range[a]))[0]?"-":(e>0?".":"")+(e=2,t)}return n}var g=[];for(a=1;a<range.length;a++){var t=range[a];g.push(0===t?"not("+o()+")":1===t?"("+o()+" || "+o()+")":2===t?g.pop()+" "+g.pop():rangeToString(t))}return o();function o(){return g.pop().replace(/^\((.+)\)$/,"$1")}
/******/ 		}
/******/ 		var satisfy = (range, version) => {
/******/ 			// see webpack/lib/util/semver.js for original code
/******/ 			if(0 in range){version=parseVersion(version);var e=range[0],r=e<0;r&&(e=-e-1);for(var n=0,i=1,a=!0;;i++,n++){var f,s,g=i<range.length?(typeof range[i])[0]:"";if(n>=version.length||"o"==(s=(typeof(f=version[n]))[0]))return!a||("u"==g?i>e&&!r:""==g!=r);if("u"==s){if(!a||"u"!=g)return!1}else if(a)if(g==s)if(i<=e){if(f!=range[i])return!1}else{if(r?f>range[i]:f<range[i])return!1;f!=range[i]&&(a=!1)}else if("s"!=g&&"n"!=g){if(r||i<=e)return!1;a=!1,i--}else{if(i<=e||s<g!=r)return!1;a=!1}else"s"!=g&&"n"!=g&&(a=!1,i--)}}var t=[],o=t.pop.bind(t);for(n=1;n<range.length;n++){var u=range[n];t.push(1==u?o()|o():2==u?o()&o():u?satisfy(u,version):!o())}return!!o();
/******/ 		}
/******/ 		var exists = (scope, key) => {
/******/ 			return scope && __webpack_require__.o(scope, key);
/******/ 		}
/******/ 		var get = (entry) => {
/******/ 			entry.loaded = 1;
/******/ 			return entry.get()
/******/ 		};
/******/ 		var eagerOnly = (versions) => {
/******/ 			return Object.keys(versions).reduce((filtered, version) => {
/******/ 					if (versions[version].eager) {
/******/ 						filtered[version] = versions[version];
/******/ 					}
/******/ 					return filtered;
/******/ 			}, {});
/******/ 		};
/******/ 		var findLatestVersion = (scope, key, eager) => {
/******/ 			var versions = eager ? eagerOnly(scope[key]) : scope[key];
/******/ 			var key = Object.keys(versions).reduce((a, b) => {
/******/ 				return !a || versionLt(a, b) ? b : a;
/******/ 			}, 0);
/******/ 			return key && versions[key];
/******/ 		};
/******/ 		var findSatisfyingVersion = (scope, key, requiredVersion, eager) => {
/******/ 			var versions = eager ? eagerOnly(scope[key]) : scope[key];
/******/ 			var key = Object.keys(versions).reduce((a, b) => {
/******/ 				if (!satisfy(requiredVersion, b)) return a;
/******/ 				return !a || versionLt(a, b) ? b : a;
/******/ 			}, 0);
/******/ 			return key && versions[key]
/******/ 		};
/******/ 		var findSingletonVersionKey = (scope, key, eager) => {
/******/ 			var versions = eager ? eagerOnly(scope[key]) : scope[key];
/******/ 			return Object.keys(versions).reduce((a, b) => {
/******/ 				return !a || (!versions[a].loaded && versionLt(a, b)) ? b : a;
/******/ 			}, 0);
/******/ 		};
/******/ 		var getInvalidSingletonVersionMessage = (scope, key, version, requiredVersion) => {
/******/ 			return "Unsatisfied version " + version + " from " + (version && scope[key][version].from) + " of shared singleton module " + key + " (required " + rangeToString(requiredVersion) + ")"
/******/ 		};
/******/ 		var getInvalidVersionMessage = (scope, scopeName, key, requiredVersion, eager) => {
/******/ 			var versions = scope[key];
/******/ 			return "No satisfying version (" + rangeToString(requiredVersion) + ")" + (eager ? " for eager consumption" : "") + " of shared module " + key + " found in shared scope " + scopeName + ".\n" +
/******/ 				"Available versions: " + Object.keys(versions).map((key) => {
/******/ 				return key + " from " + versions[key].from;
/******/ 			}).join(", ");
/******/ 		};
/******/ 		var fail = (msg) => {
/******/ 			throw new Error(msg);
/******/ 		}
/******/ 		var failAsNotExist = (scopeName, key) => {
/******/ 			return fail("Shared module " + key + " doesn't exist in shared scope " + scopeName);
/******/ 		}
/******/ 		var warn = /*#__PURE__*/ (msg) => {
/******/ 			if (typeof console !== "undefined" && console.warn) console.warn(msg);
/******/ 		};
/******/ 		var init = (fn) => (function(scopeName, key, eager, c, d) {
/******/ 			var promise = __webpack_require__.I(scopeName);
/******/ 			if (promise && promise.then && !eager) {
/******/ 				return promise.then(fn.bind(fn, scopeName, __webpack_require__.S[scopeName], key, false, c, d));
/******/ 			}
/******/ 			return fn(scopeName, __webpack_require__.S[scopeName], key, eager, c, d);
/******/ 		});
/******/ 		
/******/ 		var useFallback = (scopeName, key, fallback) => {
/******/ 			return fallback ? fallback() : failAsNotExist(scopeName, key);
/******/ 		}
/******/ 		var load = /*#__PURE__*/ init((scopeName, scope, key, eager, fallback) => {
/******/ 			if (!exists(scope, key)) return useFallback(scopeName, key, fallback);
/******/ 			return get(findLatestVersion(scope, key, eager));
/******/ 		});
/******/ 		var loadVersion = /*#__PURE__*/ init((scopeName, scope, key, eager, requiredVersion, fallback) => {
/******/ 			if (!exists(scope, key)) return useFallback(scopeName, key, fallback);
/******/ 			var satisfyingVersion = findSatisfyingVersion(scope, key, requiredVersion, eager);
/******/ 			if (satisfyingVersion) return get(satisfyingVersion);
/******/ 			warn(getInvalidVersionMessage(scope, scopeName, key, requiredVersion, eager))
/******/ 			return get(findLatestVersion(scope, key, eager));
/******/ 		});
/******/ 		var loadStrictVersion = /*#__PURE__*/ init((scopeName, scope, key, eager, requiredVersion, fallback) => {
/******/ 			if (!exists(scope, key)) return useFallback(scopeName, key, fallback);
/******/ 			var satisfyingVersion = findSatisfyingVersion(scope, key, requiredVersion, eager);
/******/ 			if (satisfyingVersion) return get(satisfyingVersion);
/******/ 			if (fallback) return fallback();
/******/ 			fail(getInvalidVersionMessage(scope, scopeName, key, requiredVersion, eager));
/******/ 		});
/******/ 		var loadSingleton = /*#__PURE__*/ init((scopeName, scope, key, eager, fallback) => {
/******/ 			if (!exists(scope, key)) return useFallback(scopeName, key, fallback);
/******/ 			var version = findSingletonVersionKey(scope, key, eager);
/******/ 			return get(scope[key][version]);
/******/ 		});
/******/ 		var loadSingletonVersion = /*#__PURE__*/ init((scopeName, scope, key, eager, requiredVersion, fallback) => {
/******/ 			if (!exists(scope, key)) return useFallback(scopeName, key, fallback);
/******/ 			var version = findSingletonVersionKey(scope, key, eager);
/******/ 			if (!satisfy(requiredVersion, version)) {
/******/ 				warn(getInvalidSingletonVersionMessage(scope, key, version, requiredVersion));
/******/ 			}
/******/ 			return get(scope[key][version]);
/******/ 		});
/******/ 		var loadStrictSingletonVersion = /*#__PURE__*/ init((scopeName, scope, key, eager, requiredVersion, fallback) => {
/******/ 			if (!exists(scope, key)) return useFallback(scopeName, key, fallback);
/******/ 			var version = findSingletonVersionKey(scope, key, eager);
/******/ 			if (!satisfy(requiredVersion, version)) {
/******/ 				fail(getInvalidSingletonVersionMessage(scope, key, version, requiredVersion));
/******/ 			}
/******/ 			return get(scope[key][version]);
/******/ 		});
/******/ 		var installedModules = {};
/******/ 		var moduleToHandlerMapping = {
/******/ 			"webpack/sharing/consume/default/react": () => (loadSingletonVersion("default", "react", false, [1,18,2,0])),
/******/ 			"webpack/sharing/consume/default/react-dom": () => (loadSingletonVersion("default", "react-dom", false, [1,18,2,0])),
/******/ 			"webpack/sharing/consume/default/@emotion/react/@emotion/react?98f9": () => (loadStrictVersion("default", "@emotion/react", false, [1,11,4,1], () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_react_dist_emotion-react_browser_development_esm_js"), __webpack_require__.e("node_modules_emotion_use-insertion-effect-with-fallbacks_dist_emotion-use-insertion-effect-wi-3c9bb41")]).then(() => (() => (__webpack_require__(/*! @emotion/react */ "./node_modules/@emotion/react/dist/emotion-react.browser.development.esm.js"))))))),
/******/ 			"webpack/sharing/consume/default/@emotion/styled/@emotion/styled": () => (loadStrictVersion("default", "@emotion/styled", false, [1,11,3,0], () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_styled_dist_emotion-styled_browser_development_esm_js"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react")]).then(() => (() => (__webpack_require__(/*! @emotion/styled */ "./node_modules/@emotion/styled/dist/emotion-styled.browser.development.esm.js"))))))),
/******/ 			"webpack/sharing/consume/default/@jupyterlab/application": () => (loadSingletonVersion("default", "@jupyterlab/application", false, [1,4,2,5])),
/******/ 			"webpack/sharing/consume/default/@jupyterlab/apputils": () => (loadSingletonVersion("default", "@jupyterlab/apputils", false, [1,4,3,5])),
/******/ 			"webpack/sharing/consume/default/@jupyterlab/notebook": () => (loadSingletonVersion("default", "@jupyterlab/notebook", false, [1,4,2,5])),
/******/ 			"webpack/sharing/consume/default/@mui/material/@mui/material": () => (loadStrictVersion("default", "@mui/material", false, [1,6,3,0], () => (__webpack_require__.e("vendors-node_modules_mui_material_index_js").then(() => (() => (__webpack_require__(/*! @mui/material */ "./node_modules/@mui/material/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/dayjs/dayjs": () => (loadStrictVersion("default", "dayjs", false, [1,1,11,13], () => (__webpack_require__.e("node_modules_dayjs_dayjs_min_js").then(() => (() => (__webpack_require__(/*! dayjs */ "./node_modules/dayjs/dayjs.min.js"))))))),
/******/ 			"webpack/sharing/consume/default/@visx/scale/@visx/scale?1592": () => (loadStrictVersion("default", "@visx/scale", false, [1,3,12,0], () => (__webpack_require__.e("vendors-node_modules_visx_scale_esm_index_js").then(() => (() => (__webpack_require__(/*! @visx/scale */ "./node_modules/@visx/scale/esm/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/@visx/shape/@visx/shape?7338": () => (loadStrictVersion("default", "@visx/shape", false, [1,3,12,0], () => (__webpack_require__.e("vendors-node_modules_visx_shape_esm_index_js").then(() => (() => (__webpack_require__(/*! @visx/shape */ "./node_modules/@visx/shape/esm/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/@visx/axis/@visx/axis": () => (loadStrictVersion("default", "@visx/axis", false, [1,3,12,0], () => (Promise.all([__webpack_require__.e("vendors-node_modules_visx_axis_esm_index_js"), __webpack_require__.e("webpack_sharing_consume_default_visx_scale_visx_scale-webpack_sharing_consume_default_visx_sh-ab6f42")]).then(() => (() => (__webpack_require__(/*! @visx/axis */ "./node_modules/@visx/axis/esm/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/@visx/tooltip/@visx/tooltip": () => (loadStrictVersion("default", "@visx/tooltip", false, [1,3,12,0], () => (__webpack_require__.e("vendors-node_modules_visx_tooltip_esm_index_js").then(() => (() => (__webpack_require__(/*! @visx/tooltip */ "./node_modules/@visx/tooltip/esm/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/@visx/event/@visx/event": () => (loadStrictVersion("default", "@visx/event", false, [1,3,12,0], () => (__webpack_require__.e("node_modules_visx_event_esm_index_js").then(() => (() => (__webpack_require__(/*! @visx/event */ "./node_modules/@visx/event/esm/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/@emotion/react/@emotion/react?6a66": () => (loadStrictVersion("default", "@emotion/react", false, [1,11,0,0,,"rc",0], () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_development_esm_js"), __webpack_require__.e("vendors-node_modules_emotion_react_dist_emotion-react_browser_development_esm_js")]).then(() => (() => (__webpack_require__(/*! @emotion/react */ "./node_modules/@emotion/react/dist/emotion-react.browser.development.esm.js"))))))),
/******/ 			"webpack/sharing/consume/default/@visx/scale/@visx/scale?604c": () => (loadStrictVersion("default", "@visx/scale", false, [4,3,12,0], () => (Promise.all([__webpack_require__.e("vendors-node_modules_visx_scale_esm_index_js"), __webpack_require__.e("node_modules_d3-array_src_bisector_js-node_modules_d3-array_src_max_js-node_modules_d3-array_-0a7de0")]).then(() => (() => (__webpack_require__(/*! @visx/scale */ "./node_modules/@visx/scale/esm/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/@visx/shape/@visx/shape?77e9": () => (loadStrictVersion("default", "@visx/shape", false, [4,3,12,0], () => (__webpack_require__.e("vendors-node_modules_visx_shape_esm_index_js").then(() => (() => (__webpack_require__(/*! @visx/shape */ "./node_modules/@visx/shape/esm/index.js")))))))
/******/ 		};
/******/ 		// no consumes in initial chunks
/******/ 		var chunkMapping = {
/******/ 			"webpack_sharing_consume_default_react": [
/******/ 				"webpack/sharing/consume/default/react"
/******/ 			],
/******/ 			"webpack_sharing_consume_default_react-dom": [
/******/ 				"webpack/sharing/consume/default/react-dom"
/******/ 			],
/******/ 			"webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-2f734f": [
/******/ 				"webpack/sharing/consume/default/@emotion/react/@emotion/react?98f9",
/******/ 				"webpack/sharing/consume/default/@emotion/styled/@emotion/styled"
/******/ 			],
/******/ 			"lib_index_js": [
/******/ 				"webpack/sharing/consume/default/@jupyterlab/application",
/******/ 				"webpack/sharing/consume/default/@jupyterlab/apputils",
/******/ 				"webpack/sharing/consume/default/@jupyterlab/notebook",
/******/ 				"webpack/sharing/consume/default/@mui/material/@mui/material",
/******/ 				"webpack/sharing/consume/default/dayjs/dayjs",
/******/ 				"webpack/sharing/consume/default/@visx/scale/@visx/scale?1592",
/******/ 				"webpack/sharing/consume/default/@visx/shape/@visx/shape?7338",
/******/ 				"webpack/sharing/consume/default/@visx/axis/@visx/axis",
/******/ 				"webpack/sharing/consume/default/@visx/tooltip/@visx/tooltip",
/******/ 				"webpack/sharing/consume/default/@visx/event/@visx/event"
/******/ 			],
/******/ 			"webpack_sharing_consume_default_emotion_react_emotion_react": [
/******/ 				"webpack/sharing/consume/default/@emotion/react/@emotion/react?6a66"
/******/ 			],
/******/ 			"webpack_sharing_consume_default_visx_scale_visx_scale-webpack_sharing_consume_default_visx_sh-ab6f42": [
/******/ 				"webpack/sharing/consume/default/@visx/scale/@visx/scale?604c",
/******/ 				"webpack/sharing/consume/default/@visx/shape/@visx/shape?77e9"
/******/ 			]
/******/ 		};
/******/ 		var startedInstallModules = {};
/******/ 		__webpack_require__.f.consumes = (chunkId, promises) => {
/******/ 			if(__webpack_require__.o(chunkMapping, chunkId)) {
/******/ 				chunkMapping[chunkId].forEach((id) => {
/******/ 					if(__webpack_require__.o(installedModules, id)) return promises.push(installedModules[id]);
/******/ 					if(!startedInstallModules[id]) {
/******/ 					var onFactory = (factory) => {
/******/ 						installedModules[id] = 0;
/******/ 						__webpack_require__.m[id] = (module) => {
/******/ 							delete __webpack_require__.c[id];
/******/ 							module.exports = factory();
/******/ 						}
/******/ 					};
/******/ 					startedInstallModules[id] = true;
/******/ 					var onError = (error) => {
/******/ 						delete installedModules[id];
/******/ 						__webpack_require__.m[id] = (module) => {
/******/ 							delete __webpack_require__.c[id];
/******/ 							throw error;
/******/ 						}
/******/ 					};
/******/ 					try {
/******/ 						var promise = moduleToHandlerMapping[id]();
/******/ 						if(promise.then) {
/******/ 							promises.push(installedModules[id] = promise.then(onFactory)['catch'](onError));
/******/ 						} else onFactory(promise);
/******/ 					} catch(e) { onError(e); }
/******/ 					}
/******/ 				});
/******/ 			}
/******/ 		}
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/jsonp chunk loading */
/******/ 	(() => {
/******/ 		// no baseURI
/******/ 		
/******/ 		// object to store loaded and loading chunks
/******/ 		// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 		// [resolve, reject, Promise] = chunk loading, 0 = chunk loaded
/******/ 		var installedChunks = {
/******/ 			"ecojupyter": 0
/******/ 		};
/******/ 		
/******/ 		__webpack_require__.f.j = (chunkId, promises) => {
/******/ 				// JSONP chunk loading for javascript
/******/ 				var installedChunkData = __webpack_require__.o(installedChunks, chunkId) ? installedChunks[chunkId] : undefined;
/******/ 				if(installedChunkData !== 0) { // 0 means "already installed".
/******/ 		
/******/ 					// a Promise means "currently loading".
/******/ 					if(installedChunkData) {
/******/ 						promises.push(installedChunkData[2]);
/******/ 					} else {
/******/ 						if(!/^webpack_sharing_consume_default_(emotion_react_emotion_react(|\-webpack_sharing_consume_default_e\-2f734f)|react(|\-dom)|visx_scale_visx_scale\-webpack_sharing_consume_default_visx_sh\-ab6f42)$/.test(chunkId)) {
/******/ 							// setup Promise in chunk cache
/******/ 							var promise = new Promise((resolve, reject) => (installedChunkData = installedChunks[chunkId] = [resolve, reject]));
/******/ 							promises.push(installedChunkData[2] = promise);
/******/ 		
/******/ 							// start chunk loading
/******/ 							var url = __webpack_require__.p + __webpack_require__.u(chunkId);
/******/ 							// create error before stack unwound to get useful stacktrace later
/******/ 							var error = new Error();
/******/ 							var loadingEnded = (event) => {
/******/ 								if(__webpack_require__.o(installedChunks, chunkId)) {
/******/ 									installedChunkData = installedChunks[chunkId];
/******/ 									if(installedChunkData !== 0) installedChunks[chunkId] = undefined;
/******/ 									if(installedChunkData) {
/******/ 										var errorType = event && (event.type === 'load' ? 'missing' : event.type);
/******/ 										var realSrc = event && event.target && event.target.src;
/******/ 										error.message = 'Loading chunk ' + chunkId + ' failed.\n(' + errorType + ': ' + realSrc + ')';
/******/ 										error.name = 'ChunkLoadError';
/******/ 										error.type = errorType;
/******/ 										error.request = realSrc;
/******/ 										installedChunkData[1](error);
/******/ 									}
/******/ 								}
/******/ 							};
/******/ 							__webpack_require__.l(url, loadingEnded, "chunk-" + chunkId, chunkId);
/******/ 						} else installedChunks[chunkId] = 0;
/******/ 					}
/******/ 				}
/******/ 		};
/******/ 		
/******/ 		// no prefetching
/******/ 		
/******/ 		// no preloaded
/******/ 		
/******/ 		// no HMR
/******/ 		
/******/ 		// no HMR manifest
/******/ 		
/******/ 		// no on chunks loaded
/******/ 		
/******/ 		// install a JSONP callback for chunk loading
/******/ 		var webpackJsonpCallback = (parentChunkLoadingFunction, data) => {
/******/ 			var [chunkIds, moreModules, runtime] = data;
/******/ 			// add "moreModules" to the modules object,
/******/ 			// then flag all "chunkIds" as loaded and fire callback
/******/ 			var moduleId, chunkId, i = 0;
/******/ 			if(chunkIds.some((id) => (installedChunks[id] !== 0))) {
/******/ 				for(moduleId in moreModules) {
/******/ 					if(__webpack_require__.o(moreModules, moduleId)) {
/******/ 						__webpack_require__.m[moduleId] = moreModules[moduleId];
/******/ 					}
/******/ 				}
/******/ 				if(runtime) var result = runtime(__webpack_require__);
/******/ 			}
/******/ 			if(parentChunkLoadingFunction) parentChunkLoadingFunction(data);
/******/ 			for(;i < chunkIds.length; i++) {
/******/ 				chunkId = chunkIds[i];
/******/ 				if(__webpack_require__.o(installedChunks, chunkId) && installedChunks[chunkId]) {
/******/ 					installedChunks[chunkId][0]();
/******/ 				}
/******/ 				installedChunks[chunkId] = 0;
/******/ 			}
/******/ 		
/******/ 		}
/******/ 		
/******/ 		var chunkLoadingGlobal = self["webpackChunkecojupyter"] = self["webpackChunkecojupyter"] || [];
/******/ 		chunkLoadingGlobal.forEach(webpackJsonpCallback.bind(null, 0));
/******/ 		chunkLoadingGlobal.push = webpackJsonpCallback.bind(null, chunkLoadingGlobal.push.bind(chunkLoadingGlobal));
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/nonce */
/******/ 	(() => {
/******/ 		__webpack_require__.nc = undefined;
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// module cache are used so entry inlining is disabled
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	var __webpack_exports__ = __webpack_require__("webpack/container/entry/ecojupyter");
/******/ 	(_JUPYTERLAB = typeof _JUPYTERLAB === "undefined" ? {} : _JUPYTERLAB).ecojupyter = __webpack_exports__;
/******/ 	
/******/ })()
;
//# sourceMappingURL=remoteEntry.282b6c03ad7937c98d6e.js.map