/*
 * Date:   2022-09-12 15:01
 * Author: Kenson Man <kenson.idv.hk@gmail.com>
 * Version: v2.0
 * File:    webframe/static/webframe/js/fileupload.js
 * Desc:    Create the file-upload component(s)
 *
 * Usage:
 *    wf_fileupload(document.querySelectorAll('...'));
*/

const wf_fileupload=function(elems){
   elems=wf_nodeList(elems);
   elems.forEach(e=>{
      e.addEventListener('change', evt=>{
         let val=evt.target.value;
         let container=wf_getParent('.input-group');
         if(container!=null){
            container=container.querySelector('.form-control');
            container.value=val;
            container.innerText=val;
         }
      });
   });
};

document.addEventListener('DOMContentLoaded', evt=>{
   wf_fileupload(document.querySelectorAll('input[type=file]'));
});
