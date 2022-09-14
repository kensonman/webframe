const Webframe=function(){
   let self=this;
   return self;
}

/**
 * Get the first matched DOMElement, which matched with the selector, according to the baseElement.
 * @param baseElement The base element to starting the search. If null or undefined, starting from the document itself.
 * @param selector    The selector to specified the parent DOMElement. 
 *                    The syntax and usage can be refer to [Locating DOM elements using selectors]
 *                    (https://developer.mozilla.org/en-US/docs/Web/API/Document_object_model/Locating_DOM_elements_using_selectors).
 *                    Default is '*'.
 * @param callback    The callback for Promise usaging.
 * @return            Returns a Node when found the specified parent. Or null when no matched result found.
 */
Webframe.getFirstMatchedParent=function( baseElement, selector='*', callback=null){
   if(baseElement===undefined || baseElement==null)baseElement=document;

   let parent=baseElement;
   while(parent.parentElement!=null){
      parent=parent.parentElement;
      if(parent.matches(selector))break;
   }
   if(callback!=null && typeof(callback)==='function')
      new Promise((res,rej)=>{res(parent)}).then(callback);
   return parent;
}

/**
 * Make sure the element is the NodeList instead of Node. It is normally used for convert the querySelector(...) to querySelectorAll(...).
 * @param elems      The specified result.
 * @return           Returns a NodeList that you can use the forEach(...) features in Node.
 */
Webframe.getNodeList=function( elems ){
   if(!(elems instanceof Node || elems instanceof NodeList))throw 'Required a Node or NodeList';
   if(elems instanceof Node){
      const tmpattr='__Webframe_getNodeList_tmpattr__';
      elems.setAttribute(tmpattr, true)
      let result=document.querySelectorAll(`[${tmpattr}]`);
      elems.removeAttribute(tmpattr);
      elems=result;
   }
   return elems;
}

/**
 * 
 */
Webframe.fileupload=function( elems, options ){
   if(!(elems instanceof Node || elems instanceof NodeList))throw 'Required a Node or NodeList';
   let opts=Object.assign({'webframe-fileupload-container':'.input-group', 'webframe-fileupload-label':'label', 'webframe-fileupload-value':'input'}, options);
   Webframe.getNodeList(elems).forEach(e=>{
      e.setAttribute('webframe-fileupload-container', opts['webframe-fileupload-container']);
      e.setAttribute('webframe-fileupload-label', opts['webframe-fileupload-label']);
      e.setAttribute('webframe-fileupload-value', opts['webframe-fileupload-value']);
      e.addEventListener('change', evt=>{
         let val=evt.target.value;
         let container=Webframe.getFirstMatchedParent(evt.target.attributes['webframe-fileupload-container']);
         if(container!=null){
            container.querySelector(evt.target.attributes['webframe-fileupload-label']).innerText=val;
            container.querySelector(evt.target.attributes['webframe-fileupload-value']).value=val;
         }
      });
   });
};

Webframe.actionlink=function(elems, options){
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
};
