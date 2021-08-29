// Date:       2021-08-27 08:47+0100
// Author:     Kenson Man <kenson.idv.hk@gmail.com>
// File:       /static/js/menuitem.vue
// Desc:       Provide the component for MenuItem

<template>
   <h1>Hello, {{name}}</h1>
</template>

<script>
export default {
   name: 'MenuItem',
   data: function(){
      return {"name": "Kenson"};
   }
}
</script>

<style>
   h1{ font-size:20px; }
</style>
