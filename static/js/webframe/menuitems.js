// Date:       2021-08-31 13:50
// Author:     Kenson Man <kenson.idv.hk@gmail.com>
// File:       /static/js/navitems.js
// Desc:       Provide the component for MenuItem
import Vue from 'https://cdn.jsdelivr.net/npm/vue@2.6.14/dist/vue.esm.browser.js';

const navbar={
   props: ['href', 'title']
   ,data: function(){ return {
         url:this.href
         ,name:this.title
         ,loading:true
         ,items:[]
      }; 
   }
   ,template: `
<nav class="navbar navbar-expand-lg navbar-light bg-light webframe-navbar" :title="name">
   <span v-if="loading">Loading: {{url}}:{{name}}...</span>
</nav>`
   ,mounted:function(){
      let vm=this;
      console.log('Loading the navbar-items from '+this.url+'...');
      axios.get(this.url).then(rep=>vm.items=rep.data).then(()=>{ console.log('loaded'); console.log(vm.items); });
   }
};

const navitem={
   data: function(){ return {title:'navitem'}; }
   ,template: '<span class="webframe-navitem">MI</span>'
};

export {navbar, navitem};
