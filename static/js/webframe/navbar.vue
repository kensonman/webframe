<template>
<nav class="navbar navbar-expand-lg navbar-light bg-light webframe-navbar" v-bind:title="name">
   <div v-if="loading"><span class="name debug">@{{name}}</span> Loading: {{url}}...</div>
   <navitem v-if="!loading" v-for="item in items" :id="item.id" :key="item.id" :name="item.name" :label="item.label" :icon="item.icon" :image="item.image" :childs="item.childs" :props="item.props"></navitem>
</nav>
</template>

<script>
if(typeof(httpVueLoader)==='undefined')throw new Error('Please load httpVueLoader first');
module.exports={
   props: ['href', 'title']
   ,name: 'navbar'
   ,data: function(){ return {
         url: this.href
         ,name: typeof(this.title)==='undefined'?'NoNamedNavBar':this.title
         ,loading:true
         ,items:[]
      }; 
   }
   ,mounted: function(){
      let vm=this;
      console.log('Loading the navbar-items from '+vm.url+'...');
      axios.get(vm.url).then(rep=>{
         console.log(rep);
         if(rep.status==200 && rep.data.length>0){
            vm.items=rep.data[0].childs; 
            vm.loading=false; 
         }
      });
   }
   ,methods: {
      getItems: function(){ return this.items; }
   }
   ,components:{
      'navitem': httpVueLoader(STATIC_ROOT+'js/webframe/navitem.vue')
   }
};
</script>
