/*
**Date** 2017-03-22 18:08
**File** jquery.dropdown.js
**Version** v2.1
**Desc** The jquery plugin for dropdown widget.
**License** BSD 

#Usage
   $('selector').wfdropdown(Options);

# Options
**item** The jquery selector to find the item. Once the item was clicked, the onclick action will be fired; Default is "a.item";

**onclick** The function to handle the item clicking; Default is jQuery.fn.wfdropdown.onclick;

**value** The jQuery selector to find the input. Default is "input:first";

# Basic Example
   <div class="dropdown" target="[name=field-name]" label="button">
      <input type="hidden" name="field-name" value="default-value"/>
      <button class="btn btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">-- Please Select --</button>
      <ul class="dropdown-menu">
            <li><a class="dropdown-item" val="1">Opt1</a></li>
            <li><a class="dropdown-item" val="two">Opt2</a></li>
            <li><a class="dropdown-item" val="value will be here">Opt3</a></li>
            <li><a class="dropdown-item">Opt4</li><!-- def value is the "Opt4</a>" -->
      </ul>
    </div>
   <script type="text/javascript"><!--
   document.addEventListener('DOMContentLoaded', evt=>{
      wf_dropdown(document.querySelectorAll('.dropdown'));
   });
   //--></script>

# JavaScript Example
   <div class="dropdown" target="[name=field-name]" label="button">
      <input type="hidden" name="field-name" value="default-value"/>
      <button class="btn btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">-- Please Select --</button>
      <ul class="dropdown-menu"></ul>
    </div>
   <script type="text/javascript"><!--
   document.addEventListener('DOMContentLoaded', evt=>{
      wf_dropdown(document.querySelectorAll('.dropdown'), {data:function(){ return [
            {"value":"05574364-e97d-4b39-87e5-f3c6428a41e0", "label":"Opt1"}, 
            {"value":"aef1d4ca-5bda-42d1-8b52-64e2575e9d0e", "label":"Opt2"}, 
            {"value":"30dcac3c-dc5e-4bf5-a1a2-ea5bf3f46e57", "label":"Opt3"}, 
         ]
      );
   });
   //--></script>

# AJAX Example
   <div class="dropdown" target="[name=field-name]" label="button">
      <input type="hidden" name="field-name" value="default-value"/>
      <button class="btn btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">-- Please Select --</button>
      <ul class="dropdown-menu"></ul>
    </div>
   <script type="text/javascript"><!--
   document.addEventListener('DOMContentLoaded', evt=>{
      wf_dropdown(document.querySelectorAll('.dropdown'), {data: async function(elem){
         let data=await axios.get('{%static "webframe/js/dropdown-data-sample.json"%}');
         //Do massage on data
         return data;
      }});
   });
   //--></script>

   <!-- {%static "webframe/js/dropdown-data-sample.json"%}  -->
   [
      {"value":"05574364-e97d-4b39-87e5-f3c6428a41e0", "label":"Opt1"}, 
      {"value":"aef1d4ca-5bda-42d1-8b52-64e2575e9d0e", "label":"Opt2"}, 
      {"value":"30dcac3c-dc5e-4bf5-a1a2-ea5bf3f46e57", "label":"Opt3"}, 
   ]
*/
const wf_dropdown_onclick=function(evt){
   evt.preventDefault();
   let self=wf_getParent(evt.target, '.dropdown');
   let val=evt.target.attributes.val===undefined?evt.target.innerText:evt.target.attributes.val;
   let lbl=evt.target.attributes.label===undefined?evt.target.innerText:evt.target.attributes.label;
   let input=self.attributes.target===undefined?'input':self.attributes.target;
   let label=self.attributes.label===undefined?'button':self.attributes.label;
   self.querySelector(input).value=val;
   self.querySelector(label).innerText=lbl;
   self.dispatchEvent(new Event('change'));
};

const wf_dropdown_additem=function(elem, value, label=null, prepend=false){
   if(label==null)label=value;
   let dropmenu=elem.querySelector('.dropdown-menu');
   let ditem=document.createElement('li');
   let a=document.createElement('a');
   ditem.appendChild(a);
   a.classList.add('dropdown-item');
   a.attributes['val']=value;
   a.innerText=label;
   if(prepend)
      dropmenu.prepend(ditem);
   else
      dropmenu.appendChild(ditem);
   a.addEventListener('click', wf_dropdown_onclick);
};

const wf_dropdown=function( elems, options={} ){
   if(elems===undefined)throw 'No element(s) found';
   let opts=Object.assign({required:false}, options);
   elems=wf_nodeList(elems);
   elems.forEach(e=>{
      let data=opts.data;
      if(data===undefined && typeof(e.attributes.ajax)!='undefined')
         data=(e)=>axios.get(e.attributes.ajax.value);
      if(!opts.required)wf_dropdown_additem(e, '', e.querySelector('button').innerText, true);
      if(data===undefined){
         e.querySelectorAll('li').forEach(li=>{ li.querySelector('a').addEventListener('click', wf_dropdown_onclick) });
      }else{
         while(typeof(data)=='function')data=data(e);
         let dropmenu=e.querySelector('.dropdown-menu');
         if(typeof(data)==='object' && typeof(data.then)==='function') //if Promise
            data
               .then(rep=>{ rep.data.forEach(item=>{ wf_dropdown_additem(e, item.value, item.label) }); })
               .catch(err=>{ console.error(err) });
         else
            data.forEach(item=>{ wf_dropdown_additem(e, item.value, item.label) });
      }
   });
};
