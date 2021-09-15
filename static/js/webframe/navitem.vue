<template>
<span v-if="data.childs.length>0" class="webframe-navitem" :id="data.id">
   <a class="nav-link dropdown-toggle" href="#" :id="data.id" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
      <i v-if="data.icon" :class="'fas '+data.icon"></i> 
      <span v-if="data.label">{{ data.label|trans }}</span>
      <img v-if="data.image" :src="data.image"/>
   </a>
   <div class="dropdown-menu" :arial-labelledby="data.id">
      <span class="webframe-navitem" v-for="item in data.childs" :key="item.id">
         <div v-if="item.label=='-'" class="dropdown-divider"></div>
         <navitem v-else :menuitem="item"></navitem>
      </span>
   </div>
</span>
<span v-else class="webframe-navitem" :id="data.id">
   <a :class="data.props.class?data.props.class:'nav-link'" :href="data.props.href?data.props.href:'#'" :target="data.props.target?data.props.target:'_self'" @click.prevent="onclick" @mouseenter="mousein" @mouseleave="mouseout">
      <i v-if="data.icon" :class="'fas '+data.icon"></i> 
      <span v-if="data.label">{{ data.label|trans }}</span>
      <img v-if="data.image" :src="data.image"/>
   </a>
</span>
</template>

<script>
module.exports={
   data: function(){ return {
         'data': this.menuitem
      }; 
   }
   ,props: ['menuitem']
   ,name: 'navitem'
   ,methods:{
      onclick: function(evt){
         if(typeof(this.data.onclick)==='undefined' || this.data.onclick==null || this.data.onclick.length<1)
            this.$parent.onclick(evt);//raise the event for navbar
         else{
            console.debug('data.onclick@navitem@'+this.data.id);
            eval(this.data.onclick);
         }
      }
      ,mousein:  function(evt){ if(this.data.mousein && this.data.mousein.length>0) eval(this.data.mousein); else this.$parent.mousein(evt); }
      ,mouseout: function(evt){ if(this.data.mouseout && this.data.mouseout.length>0) eval(this.data.mouseout); else this.$parent.mouseout(evt); }
   }
   ,filters: {
      trans: function(value){
         if(!value)return '';
         let user=JSON.parse(window.localStorage.getItem('USER'));
         let val=value;
         val=val.replace(/{\s*username\s*}/g, user.username);
         val=val.replace(/{\s*first_name\s*}/g, user.first_name);
         val=val.replace(/{\s*last_name\s*}/g, user.last_name);
         val=val.replace(/{\s*email\s*}/g, user.email);
         return val
      }
   }
};
</script>

<style>
.webframe-navitem{ position:relative; margin:0px; padding:0px; }
</style>
