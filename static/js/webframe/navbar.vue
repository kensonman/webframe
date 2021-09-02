<template>
<div v-if="loading"><span class="name debug">@{{name}}</span> Loading: {{url}}... <i class="fas fa-spinner fa-pulse"></i></div>
<nav class="navbar navbar-expand-lg navbar-light bg-light webframe-navbar" v-else>
   <a class="navbar-brand" :href="data.props.href?data.props.href:'/'" :id="id+'-brand'" @click.prevent="onclick">
      <i v-if="data.icon" :class="'fas '+data.icon"></i>
      <label :for="id">{{data.label}}</label>
      <img v-if="data.image" :src="data.image"/>
   </a>

   <button class="navbar-toggler" type="button" data-toggle="collapse" :data-target="'#'+id" :aria-controls="id" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
   </button>
   <div class="collapse navbar-collapse" :id="id">
      <ul :class="'navbar-nav mr-auto'+(items.props.class?items.props.class:'')" v-for="items in data.childs" :key="items.id" :id="items.id">
         <li v-for="item in items.childs" :key="item.id" :class="'nav-item'"><navitem :menuitem="item"></navitem></li>
      </ul>
   </div>
</nav>
</template>

<script>
if(typeof(httpVueLoader)==='undefined')throw new Error('Please load httpVueLoader first');

function uuidv4() {
   return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
   });
}
module.exports={
   props: ['href', 'title']
   ,name: 'navbar'
   ,data: function(){ return {
         url: this.href
         ,name: this.title
         ,loading:true
         ,id: uuidv4()
         ,data:null
      }; 
   }
   ,mounted: function(){
      let vm=this;
      console.log('Loading the navbar-items from '+vm.url+'...');
      axios.get(vm.url).then(rep=>{
         console.debug(rep);
         if(rep.status==200){
            vm.data=rep.data;
            vm.name=vm.data.name;
            vm.id=vm.data.id;
            vm.loading=false; 
            console.debug('loaded navbar');
         }else{
            console.debug('Loading '+rep.status+' error');
         }
      });
   }
   ,methods: {
      getItems: function(){ return this.items; }
      ,onclick: function(evt){
         console.debug('onclick@navbar');
         console.debug(this.data.onclick);
         eval(this.data.onclick);
      }
      ,mousein: function(evt){ if(this.data.mousein && this.data.mousein.length>0) eval(this.data.mousein); }
      ,mouseout: function(evt){ if(this.data.mouseout && this.data.mouseout.length>0) eval(this.data.mouseout); }
   }
   ,components:{
      'navitem': httpVueLoader(STATIC_ROOT+'js/webframe/navitem.vue')
   }
};
</script>

<style>
.webframe-helper{ position:relative; padding:0px; margin:0px; }
</style>
