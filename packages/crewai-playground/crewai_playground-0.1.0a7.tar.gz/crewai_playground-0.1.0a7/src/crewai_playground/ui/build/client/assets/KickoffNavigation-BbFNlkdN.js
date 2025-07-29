import{q as i,x as l,l as o}from"./chunk-GNGMS2XR-KLeu_BA0.js";import{a as c,B as f,c as h}from"./sun-CQoWRrLL.js";/**
 * @license lucide-react v0.483.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const d=[["path",{d:"M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2",key:"169zse"}]],k=c("Activity",d);/**
 * @license lucide-react v0.483.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const r=[["path",{d:"M3 3v16a2 2 0 0 0 2 2h16",key:"c24i48"}],["path",{d:"M18 17V9",key:"2bz60n"}],["path",{d:"M13 17V5",key:"1frdt8"}],["path",{d:"M8 17v-3",key:"17ska0"}]],m=c("ChartColumn",r);/**
 * @license lucide-react v0.483.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const p=[["polygon",{points:"6 3 20 12 6 21 6 3",key:"1oa8hb"}]],u=c("Play",p);function g({crewId:s}){const e=i(),t=l().pathname,n=[{name:"Execution",path:s?`/kickoff?crewId=${s}`:"/kickoff",icon:o.jsx(u,{className:"h-4 w-4"}),isActive:t==="/kickoff"},{name:"Traces",path:`/kickoff/traces?crewId=${s}`,icon:o.jsx(k,{className:"h-4 w-4"}),isActive:t.includes("/kickoff/traces")},{name:"Evaluations",path:`/kickoff/evals?crewId=${s}`,icon:o.jsx(m,{className:"h-4 w-4"}),isActive:t.includes("/kickoff/evals")}];return o.jsx("div",{className:"border rounded-lg p-1 flex mb-4 bg-muted/30",children:n.map(a=>o.jsxs(f,{variant:a.isActive?"default":"ghost",size:"sm",className:h("flex-1 flex items-center justify-center gap-2",a.isActive?"shadow-sm":"hover:bg-muted/50"),onClick:()=>e(a.path),disabled:!s&&a.name!=="Execution",children:[a.icon,a.name]},a.name))})}export{m as C,g as K,u as P};
