import{l as e,q as n,x as h}from"./chunk-GNGMS2XR-KLeu_BA0.js";import{a as s,B as l,f as i,M as d}from"./sun-CQoWRrLL.js";import{u as x}from"./store-BDLt0vbv.js";/**
 * @license lucide-react v0.483.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const p=[["path",{d:"M12 6V2H8",key:"1155em"}],["path",{d:"m8 18-4 4V8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2Z",key:"w2lp3e"}],["path",{d:"M2 12h2",key:"1t8f8n"}],["path",{d:"M9 11v2",key:"1ueba0"}],["path",{d:"M15 11v2",key:"i11awn"}],["path",{d:"M20 12h2",key:"1q8mjw"}]],y=s("BotMessageSquare",p);/**
 * @license lucide-react v0.483.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const m=[["rect",{width:"7",height:"9",x:"3",y:"3",rx:"1",key:"10lvy0"}],["rect",{width:"7",height:"5",x:"14",y:"3",rx:"1",key:"16une8"}],["rect",{width:"7",height:"9",x:"14",y:"12",rx:"1",key:"1hutg5"}],["rect",{width:"7",height:"5",x:"3",y:"16",rx:"1",key:"ldoo1y"}]],f=s("LayoutDashboard",m);/**
 * @license lucide-react v0.483.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const k=[["rect",{x:"16",y:"16",width:"6",height:"6",rx:"1",key:"4q2zg0"}],["rect",{x:"2",y:"16",width:"6",height:"6",rx:"1",key:"8cvhb9"}],["rect",{x:"9",y:"2",width:"6",height:"6",rx:"1",key:"1egb70"}],["path",{d:"M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3",key:"1jsf9p"}],["path",{d:"M12 12V8",key:"2874zd"}]],g=s("Network",k);/**
 * @license lucide-react v0.483.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const u=[["path",{d:"M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z",key:"cbrjhi"}]],b=s("Wrench",u);/**
 * @license lucide-react v0.483.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const N=[["path",{d:"M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z",key:"1xq2db"}]],w=s("Zap",N);function j(){const o=n(),t=h(),c=[{icon:f,label:"Dashboard",path:"/"},{icon:y,label:"Chat",path:"/chat"},{icon:w,label:"Crews",path:"/kickoff"},{icon:b,label:"Tools",path:"/tools"},{icon:g,label:"Flows",path:"/flow"}];return e.jsxs("aside",{className:"w-64 flex-shrink-0 border-r bg-background p-4 flex flex-col",children:[e.jsx("div",{className:"flex items-center mb-8",children:e.jsx("h2",{className:"text-2xl font-bold",children:"CrewAI Playground"})}),e.jsx("nav",{className:"flex flex-col space-y-2",children:c.map((a,r)=>e.jsxs(l,{variant:t.pathname===a.path?"secondary":"ghost",className:"justify-start",onClick:()=>o(a.path),children:[e.jsx(a.icon,{className:"mr-2 h-5 w-5"}),a.label]},r))})]})}function q({children:o,rightSidebar:t}){const{isDarkMode:c,toggleDarkMode:a}=x();return e.jsxs("div",{className:"flex h-screen bg-background text-foreground",children:[e.jsx(j,{}),e.jsxs("div",{className:"flex flex-col flex-1",children:[e.jsx("header",{className:"py-4 px-8 border-b bg-background",children:e.jsx("div",{className:"flex items-center justify-end",children:e.jsx(l,{variant:"ghost",size:"icon",onClick:a,className:"h-8 w-8",children:c?e.jsx(i,{className:"h-4 w-4"}):e.jsx(d,{className:"h-4 w-4"})})})}),e.jsxs("main",{className:"flex-grow p-8 overflow-auto flex gap-8",children:[e.jsx("div",{className:"flex-1",children:o}),t&&e.jsx("div",{className:"w-96 border-l bg-background p-4",children:t})]})]})]})}export{y as B,q as L,g as N,b as W,w as Z};
