<template>
<div class="field form-group" :id="id">
   <div v-if="type=='text'">
      <label :for="`txt-${id}`">{{label}} <i class="fas fa-shield-alt" v-if="required"></i></label>
      <input type="text" :name="name" :class="'form-control control'" :id="`txt-${id}`" :placeholder="label" :required="required?'required':false" v-model="value"/>
      <div class="helptext" c-if="helptext">{{ helptext }}</div>
   </div>
   <div v-else-if="type=='textarea'">
      <label :for="`txt-${id}`">{{label}} <i class="fas fa-shield-alt" v-if="required"></i></label>
      <textarea :name="name" :class="'form-control control'" :id="`txt-${id}`" :placeholder="label" :required="required?'required':false" v-model="value"></textarea>
      <div class="helptext" c-if="helptext">{{ helptext }}</div>
   </div>
   <div v-else-if="type=='number'">
      <label :for="`txt-${id}`">{{label}} <i class="fas fa-shield-alt" v-if="required"></i></label>
      <input type="number" :name="name" :class="'form-control control'" :id="`txt-${id}`" :placeholder="label" :required="required?'required':false" v-model="value"/>
      <div class="helptext" c-if="helptext">{{ helptext }}</div>
   </div>
</div>
</template>

<script>
if(typeof(httpVueLoader)==='undefined')throw new Error('Please load httpVueLoader first');
const dateFmt=pydatefmt('%Y-%m-%d %H:%M');
function uuidv4() {
   return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
   });
};
module.exports={
   name: 'categories'
   ,props: ['type', 'name', 'label', 'helptext', 'options', 'required', 'value']
   ,data: function(){
      return {'id':uuidv4()}
   }
};
</script>

<style>
.helptext{ color:#777; }
</style>
