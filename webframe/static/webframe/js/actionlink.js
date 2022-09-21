// Date: 2022-09-09 12:26
// File: actionlink.js
// Version: v3.0
// Description:
//    Rewrite the actionlink module with VanillaJS
// Usage:
//    Webframe.actionlink(document.querySelectorAll('a[action]'), <opts>)

Webframe.actionlink=function(elems, options=null)=>{
   let opts=Object.assign({href:null,action:null,target:null,preventDefault:true}, options);
   Webframe.nodeList(elems).forEach( lnk=>{
      if(opts.href)lnk.setAttribute('href', opts.href);
      if(opts.action)lnk.setAttribute('action', opts.action);
      if(opts.target)lnk.setAttribute('target', opts.target);
      if(opts.preventDefault)lnk.setAttribute('preventDefault', opts.preventDefault);

      lnk.addEventListener(evt=>{
         if(evt.target.attributes['preventDefault']==='true')evt.preventDefault();
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
