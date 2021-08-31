<template>
<a v-if="childs.length < 1" :class="props.class" :href="props.href?props.href:'#'" :target="props.target?props.target:'_self'"><i v-if="icon" :class="'fas '+icon"></i> {{ label }}</a>
<div v-else>
</div>
</template>

<script>
module.exports={
   data: function(){ return {}; }
   ,props: ['id', 'name', 'label', 'icon', 'image', 'childs', 'props']
   ,name: 'navitem'
};
</script>
