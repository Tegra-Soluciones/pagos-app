var v=Object.defineProperty,x=Object.defineProperties;var C=Object.getOwnPropertyDescriptors;var s=Object.getOwnPropertySymbols;var d=Object.prototype.hasOwnProperty,h=Object.prototype.propertyIsEnumerable;var u=(e,r,t)=>r in e?v(e,r,{enumerable:!0,configurable:!0,writable:!0,value:t}):e[r]=t,a=(e,r)=>{for(var t in r||(r={}))d.call(r,t)&&u(e,t,r[t]);if(s)for(var t of s(r))h.call(r,t)&&u(e,t,r[t]);return e},l=(e,r)=>x(e,C(r));var w=(e,r)=>{var t={};for(var o in e)d.call(e,o)&&r.indexOf(o)<0&&(t[o]=e[o]);if(e!=null&&s)for(var o of s(e))r.indexOf(o)<0&&h.call(e,o)&&(t[o]=e[o]);return t};import{l as g}from"./main.js";/**
 * @license lucide-vue-next v0.373.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var i={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor","stroke-width":2,"stroke-linecap":"round","stroke-linejoin":"round"};/**
 * @license lucide-vue-next v0.373.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const $=e=>e.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase();/**
 * @license lucide-vue-next v0.373.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const B=(e,r)=>(L,{attrs:b,slots:c})=>{var n=L,{size:t,strokeWidth:o=2,absoluteStrokeWidth:k,color:m,class:A}=n,p=w(n,["size","strokeWidth","absoluteStrokeWidth","color","class"]);return g("svg",a(l(a(l(a({},i),{width:t||i.width,height:t||i.height,stroke:m||i.stroke,"stroke-width":k?Number(o)*24/Number(t):o}),b),{class:["lucide",`lucide-${$(e)}`]}),p),[...r.map(f=>g(...f)),...c.default?[c.default()]:[]])};export{B as c};
