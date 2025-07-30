import{j as xt,u as bt,r as A,s as wt,k as kt,o as Ct,l as V,m as $,w as d,n as r,p as n,q as At,t as _,v as Pt,x as v,y as St,z as g,A as Ft,C as Ut,D as x,E as w,G as Bt,H as Rt,J as Tt,K as L,N as Et,_ as j,O as Ot,P as Vt,Q as $t,R as W,T as Mt,X as It,Y as Dt,Z as Nt,$ as zt,a0 as Lt,a1 as jt,a2 as Wt}from"./index-BXU9C3Zy.js";import{loader as Zt,VueMonacoEditor as qt}from"@guolao/vue-monaco-editor";import*as Gt from"monaco-editor";import Jt from"monaco-editor/esm/vs/editor/editor.worker?worker";import Kt from"monaco-editor/esm/vs/language/json/json.worker?worker";import Ht from"monaco-editor/esm/vs/language/css/css.worker?worker";import Qt from"monaco-editor/esm/vs/language/html/html.worker?worker";import Xt from"monaco-editor/esm/vs/language/typescript/ts.worker?worker";import{newPyodideWorker as Yt}from"./frontend/tools/pyodide-worker-api.ts";import{version as te}from"pyodide";self.MonacoEnvironment={getWorker(t,e){return e==="json"?new Kt:e==="css"||e==="scss"||e==="less"?new Ht:e==="html"||e==="handlebars"||e==="razor"?new Qt:e==="typescript"||e==="javascript"?new Xt:new Jt}};function ee(){Zt.config({monaco:Gt})}const Q="3.7.7",oe=Q,C=typeof Buffer=="function",Z=typeof TextDecoder=="function"?new TextDecoder:void 0,q=typeof TextEncoder=="function"?new TextEncoder:void 0,ne="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",P=Array.prototype.slice.call(ne),U=(t=>{let e={};return t.forEach((l,p)=>e[l]=p),e})(P),ae=/^(?:[A-Za-z\d+\/]{4})*?(?:[A-Za-z\d+\/]{2}(?:==)?|[A-Za-z\d+\/]{3}=?)?$/,u=String.fromCharCode.bind(String),G=typeof Uint8Array.from=="function"?Uint8Array.from.bind(Uint8Array):t=>new Uint8Array(Array.prototype.slice.call(t,0)),X=t=>t.replace(/=/g,"").replace(/[+\/]/g,e=>e=="+"?"-":"_"),Y=t=>t.replace(/[^A-Za-z0-9\+\/]/g,""),tt=t=>{let e,l,p,c,f="";const i=t.length%3;for(let b=0;b<t.length;){if((l=t.charCodeAt(b++))>255||(p=t.charCodeAt(b++))>255||(c=t.charCodeAt(b++))>255)throw new TypeError("invalid character found");e=l<<16|p<<8|c,f+=P[e>>18&63]+P[e>>12&63]+P[e>>6&63]+P[e&63]}return i?f.slice(0,i-3)+"===".substring(i):f},D=typeof btoa=="function"?t=>btoa(t):C?t=>Buffer.from(t,"binary").toString("base64"):tt,M=C?t=>Buffer.from(t).toString("base64"):t=>{let l=[];for(let p=0,c=t.length;p<c;p+=4096)l.push(u.apply(null,t.subarray(p,p+4096)));return D(l.join(""))},B=(t,e=!1)=>e?X(M(t)):M(t),re=t=>{if(t.length<2){var e=t.charCodeAt(0);return e<128?t:e<2048?u(192|e>>>6)+u(128|e&63):u(224|e>>>12&15)+u(128|e>>>6&63)+u(128|e&63)}else{var e=65536+(t.charCodeAt(0)-55296)*1024+(t.charCodeAt(1)-56320);return u(240|e>>>18&7)+u(128|e>>>12&63)+u(128|e>>>6&63)+u(128|e&63)}},ie=/[\uD800-\uDBFF][\uDC00-\uDFFFF]|[^\x00-\x7F]/g,et=t=>t.replace(ie,re),J=C?t=>Buffer.from(t,"utf8").toString("base64"):q?t=>M(q.encode(t)):t=>D(et(t)),k=(t,e=!1)=>e?X(J(t)):J(t),K=t=>k(t,!0),se=/[\xC0-\xDF][\x80-\xBF]|[\xE0-\xEF][\x80-\xBF]{2}|[\xF0-\xF7][\x80-\xBF]{3}/g,le=t=>{switch(t.length){case 4:var e=(7&t.charCodeAt(0))<<18|(63&t.charCodeAt(1))<<12|(63&t.charCodeAt(2))<<6|63&t.charCodeAt(3),l=e-65536;return u((l>>>10)+55296)+u((l&1023)+56320);case 3:return u((15&t.charCodeAt(0))<<12|(63&t.charCodeAt(1))<<6|63&t.charCodeAt(2));default:return u((31&t.charCodeAt(0))<<6|63&t.charCodeAt(1))}},ot=t=>t.replace(se,le),nt=t=>{if(t=t.replace(/\s+/g,""),!ae.test(t))throw new TypeError("malformed base64.");t+="==".slice(2-(t.length&3));let e,l="",p,c;for(let f=0;f<t.length;)e=U[t.charAt(f++)]<<18|U[t.charAt(f++)]<<12|(p=U[t.charAt(f++)])<<6|(c=U[t.charAt(f++)]),l+=p===64?u(e>>16&255):c===64?u(e>>16&255,e>>8&255):u(e>>16&255,e>>8&255,e&255);return l},N=typeof atob=="function"?t=>atob(Y(t)):C?t=>Buffer.from(t,"base64").toString("binary"):nt,at=C?t=>G(Buffer.from(t,"base64")):t=>G(N(t).split("").map(e=>e.charCodeAt(0))),rt=t=>at(it(t)),de=C?t=>Buffer.from(t,"base64").toString("utf8"):Z?t=>Z.decode(at(t)):t=>ot(N(t)),it=t=>Y(t.replace(/[-_]/g,e=>e=="-"?"+":"/")),I=t=>de(it(t)),ue=t=>{if(typeof t!="string")return!1;const e=t.replace(/\s+/g,"").replace(/={0,2}$/,"");return!/[^\s0-9a-zA-Z\+/]/.test(e)||!/[^\s0-9a-zA-Z\-_]/.test(e)},st=t=>({value:t,enumerable:!1,writable:!0,configurable:!0}),lt=function(){const t=(e,l)=>Object.defineProperty(String.prototype,e,st(l));t("fromBase64",function(){return I(this)}),t("toBase64",function(e){return k(this,e)}),t("toBase64URI",function(){return k(this,!0)}),t("toBase64URL",function(){return k(this,!0)}),t("toUint8Array",function(){return rt(this)})},dt=function(){const t=(e,l)=>Object.defineProperty(Uint8Array.prototype,e,st(l));t("toBase64",function(e){return B(this,e)}),t("toBase64URI",function(){return B(this,!0)}),t("toBase64URL",function(){return B(this,!0)})},pe=()=>{lt(),dt()},fe={version:Q,VERSION:oe,atob:N,atobPolyfill:nt,btoa:D,btoaPolyfill:tt,fromBase64:I,toBase64:k,encode:k,encodeURI:K,encodeURL:K,utob:et,btou:ot,decode:I,isValid:ue,fromUint8Array:B,toUint8Array:rt,extendString:lt,extendUint8Array:dt,extendBuiltins:pe},ce=`import micropip

# Prioritize the OCP.wasm package repository for finding the ported dependencies.
micropip.set_index_urls(["https://yeicor.github.io/OCP.wasm", "https://pypi.org/simple"])

# For build123d < 0.10.0, we need to install the mock the py-lib3mf package (before the main install).
await micropip.install("lib3mf")
micropip.add_mock_package("py-lib3mf", "2.4.1", modules={"py_lib3mf": 'from lib3mf import *'})

# Install the yacv_server package, which is the main server for the OCP.wasm playground; and also preinstalls build123d.
await micropip.install("yacv_server", pre=True)

# Preimport the yacv_server package to ensure it is available in the global scope, and mock the ocp_vscode package.
from yacv_server import *
micropip.add_mock_package("ocp-vscode", "2.8.9", modules={"ocp_vscode": 'from yacv_server import *'})
show_object = show

# Preinstall a font to avoid issues with no font being available.
def install_font_to_ocp(font_url, font_name=None):
    # noinspection PyUnresolvedReferences
    from pyodide.http import pyfetch
    from OCP.Font import Font_FontMgr, Font_SystemFont, Font_FA_Regular
    from OCP.TCollection import TCollection_AsciiString
    import os, asyncio

    font_name = font_name if font_name is not None else font_url.split("/")[-1]

    # Choose a "system-like" font directory
    font_path = os.path.join("/tmp", font_name)
    os.makedirs(os.path.dirname(font_path), exist_ok=True)

    # Download the font using pyfetch
    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(pyfetch(font_url))
    font_data = loop.run_until_complete(response.bytes())

    # Save it to the system-like folder
    with open(font_path, "wb") as f:
        f.write(font_data)

    mgr = Font_FontMgr.GetInstance_s()
    font_t = Font_SystemFont(TCollection_AsciiString(font_path))
    font_t.SetFontPath(Font_FA_Regular, TCollection_AsciiString(font_path))
    assert mgr.RegisterFont(font_t, False)
    #print(f"✅ Font installed at: {font_path}")
    return font_path


# Make sure there is at least one font installed, so that the tests can run
install_font_to_ocp("https://raw.githubusercontent.com/xbmc/xbmc/d3a7f95f3f017b8e861d5d95cc4b33eef4286ce2/media/Fonts/arial.ttf")
`,me={style:{display:"inline-flex","margin-right":"16px"}},ye={style:{"margin-right":"-8px"}},he={style:{"margin-left":"-8px"}},_e={class:"playground-container"},ve={class:"playground-console"},H="yacv_server://model/",ge=xt({__name:"PlaygroundDialogContent",props:{initialCode:{}},emits:["close","updateModel"],setup(t,{emit:e}){bt(a=>({e61290de:m.value}));const l=t,p=e;ee();const c=A(l.initialCode),f=A("");function i(a){f.value+=a;let o=1e4;f.value.length>o&&(f.value=f.value.slice(-o)),console.log(a),jt(()=>{const s=document.querySelector(".playground-console");s&&(s.scrollTop=s.scrollHeight)})}const b={automaticLayout:!0,formatOnType:!0,formatOnPaste:!0},ut=window.matchMedia("(prefers-color-scheme: dark)").matches?"vs-dark":"vs",pt=wt(),ft=a=>pt.value=a,m=A(.9);let y=null;const h=A(!0);async function z(){h.value=!0,m.value==0&&(m.value=.9),y===null?(i(`Creating new Pyodide worker...
`),y=Yt({indexURL:`https://cdn.jsdelivr.net/pyodide/v${te}/full/`,packages:["micropip","sqlite3"]})):i(`Reusing existing Pyodide instance...
`),i(`Preloading packages...
`),await y.asyncRun(ce,i,i),h.value=!1,i(`Pyodide worker initialized.
`)}async function R(){if(y===null){i(`Pyodide worker is not initialized. Please wait...
`);return}if(h.value){i(`Pyodide is already running. Please wait...
`);return}i(`Running code...
`);try{h.value=!0,await y.asyncRun(c.value,i,a=>{if(a.startsWith(H)){const o=a.slice(H.length);ct(o)}else i(a)})}catch(a){i(`Error running initial code: ${a}
`)}finally{h.value=!1}}function ct(a){i(`Model data detected... ${a.length}B
`);let o=0,s=0;for(;o<a.length&&(a[o]==="{"?s++:a[o]==="}"&&s--,s!==0);o++);if(s!==0)throw`Error: Invalid model data received: ${a}
`;const T=a.slice(0,o+1);let E=JSON.parse(T);const F=new Dt(E.name,"",E.hash,E.is_remove);if(i(`Model metadata: ${JSON.stringify(F)}
`),!F.isRemove){const O=fe.toUint8Array(a.slice(o+1));console.assert(O.slice(0,4).toString()=="103,108,84,70","Invalid GLTF binary data received: "+O.slice(0,4).toString());const gt=new Blob([O],{type:"model/gltf-binary"});F.url=URL.createObjectURL(gt)}let vt=new Nt([F],()=>{});p("updateModel",vt)}function mt(){y&&(y.terminate(),y=null),f.value="",z()}function yt(){const a=window.location,o=new URLSearchParams(a.hash.slice(1));o.set("pg_code",zt(Lt(c.value,{level:9})));const s=`${a.origin}${a.pathname}${a.search}#${o.toString()}`;if(i(`Share link ready: ${s}
`),navigator.clipboard)navigator.clipboard.writeText(s).then(()=>i(`Link copied to clipboard!
`)).catch(T=>i(`Failed to copy link: ${T}
`));else{i(`Clipboard API not available. Please copy the link manually.
`);return}}function ht(){throw new Error("Not implemented yet!")}function _t(){throw new Error("Not implemented yet!")}(async()=>{const a=await kt();m.value=a.pg_opacity_loading,await z(),l.initialCode!=""&&await R(),m.value=a.pg_opacity_loaded})();const S=A(null);return Ct(()=>{S.value&&(console.log(S.value),S.value.addEventListener("keydown",a=>{a instanceof KeyboardEvent&&(a.key==="Enter"&&a.ctrlKey?(a.preventDefault(),R()):a.key==="Escape"&&p("close"))}))}),(a,o)=>($(),V(n(It),{class:"popup-card",style:W(m.value==0?"position: absolute; top: calc(-50vh + 24px); width: calc(100vw - 64px);":"")},{default:d(()=>[r(n(At),{class:"popup"},{default:d(()=>[r(n(Pt),{style:{flex:"0 1 auto"}},{default:d(()=>o[8]||(o[8]=[v("Playground",-1)])),_:1,__:[8]}),r(n(St)),_("span",me,[r(n(g),{path:n(Ft),type:"mdi",style:{height:"32px"}},null,8,["path"]),r(n(Ut),{modelValue:m.value,"onUpdate:modelValue":o[0]||(o[0]=s=>m.value=s),max:1,min:0,step:.1,style:{width:"100px",height:"32px"}},null,8,["modelValue"]),r(n(x),{activator:"parent",location:"bottom"},{default:d(()=>o[9]||(o[9]=[v("Opacity of the editor (0 = hidden, 1 = fully visible)",-1)])),_:1,__:[9]})]),_("span",ye,[r(n(w),{icon:"",disabled:"",onClick:o[1]||(o[1]=s=>ht())},{default:d(()=>[r(n(g),{path:n(Bt),type:"mdi"},null,8,["path"])]),_:1}),r(n(x),{activator:"parent",location:"bottom"},{default:d(()=>o[10]||(o[10]=[v("Save current state to a snapshot for fast startup (WIP)",-1)])),_:1,__:[10]})]),_("span",he,[r(n(w),{icon:"",disabled:"",onClick:o[2]||(o[2]=s=>_t())},{default:d(()=>[r(n(g),{path:n(Rt),type:"mdi"},null,8,["path"])]),_:1}),r(n(x),{activator:"parent",location:"bottom"},{default:d(()=>o[11]||(o[11]=[v("Load snapshot for fast startup (WIP)",-1)])),_:1,__:[11]})]),r(n(w),{icon:"",onClick:o[3]||(o[3]=s=>mt())},{default:d(()=>[r(n(g),{path:n(Tt),type:"mdi"},null,8,["path"]),r(n(x),{activator:"parent",location:"bottom"},{default:d(()=>o[12]||(o[12]=[v("Reset Pyodide worker (this forgets all previous state and will take a little while) ",-1)])),_:1,__:[12]})]),_:1}),r(n(w),{icon:"",onClick:o[4]||(o[4]=s=>R()),disabled:h.value},{default:d(()=>[r(n(g),{path:n(Et),type:"mdi"},null,8,["path"]),h.value?($(),V(j,{key:0,style:{position:"absolute",top:"-16%",left:"-16%"}})):L("",!0),r(n(x),{activator:"parent",location:"bottom"},{default:d(()=>o[13]||(o[13]=[v("Run code",-1)])),_:1,__:[13]})]),_:1},8,["disabled"]),r(n(w),{icon:"",onClick:o[5]||(o[5]=s=>yt())},{default:d(()=>[r(n(g),{path:n(Ot),type:"mdi"},null,8,["path"]),r(n(x),{activator:"parent",location:"bottom"},{default:d(()=>o[14]||(o[14]=[v("Share link that auto-runs the code",-1)])),_:1,__:[14]})]),_:1}),r(n(w),{icon:"",onClick:o[6]||(o[6]=s=>p("close"))},{default:d(()=>[r(n(g),{path:n(Vt),type:"mdi"},null,8,["path"]),r(n(x),{activator:"parent",location:"bottom"},{default:d(()=>o[15]||(o[15]=[v("Close (Pyodide remains loaded)",-1)])),_:1,__:[15]})]),_:1})]),_:1}),r(n($t),{class:"popup-card-text",style:W(m.value==0?"display: none":"")},{default:d(()=>[_("div",_e,[_("div",{class:"playground-editor",ref_key:"editorRef",ref:S},[r(n(qt),{value:c.value,"onUpdate:value":o[7]||(o[7]=s=>c.value=s),theme:n(ut),options:b,language:"python",onMount:ft},null,8,["value","theme"])],512),_("div",ve,[o[16]||(o[16]=_("h3",null,"Console Output",-1)),_("pre",null,Mt(f.value),1),h.value?($(),V(j,{key:0})):L("",!0)])])]),_:1},8,["style"])]),_:1},8,["style"]))}}),Ue=Wt(ge,[["__scopeId","data-v-50d46d8c"]]);export{Ue as default};
//# sourceMappingURL=PlaygroundDialogContent-DwAqTo4r.js.map
