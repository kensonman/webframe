// Date: 2022-09-09 12:26
// File: actionlink.js
// Version: v3.0
// Description:
//    Rewrite the actionlink module with VanillaJS
// Usage:
//    wf_actionlink(document.querySelectorAll('a[action]'), <opts>)

const wf_actionlink=(elems, options={href:null,action:null,target:null})=>{
   let opts=Object.assign({href:null,action:null,target:null}, opts);
   elems.forEach( lnk=>{
      if(opts.href)lnk.attributes.href=opts.href;
      if(opts.action)lnk.attributes.action=opts.action;
      if(opts.target)lnk.attributes.target=opts.target;

      lnk.addEventListener(evt=>{
         evt.preventDefault();
         console.debug(`action link clicked:`);
         console.debug(evt.target);
         let action=evt.target.attributes.action;
         let target=evt.target.attributes.target;
         let href=evt.target.attr.href;
         if(action==='link' || action==='href')
            window.open(href, target);
         else if(action==='script')
            eval(href);
         else
            alert('Unknow action');
      });
   });
}
