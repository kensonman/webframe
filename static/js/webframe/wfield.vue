<template>
<div class="field form-group" :id="id">
   <label :for="`fld-${id}`" v-if="type!='hidden'" :id="`lbl-${id}`">{{label}} <i class="fas fa-shield-alt" v-if="required"></i></label>
   <div v-if="type=='color' || type=='colour'">
      <input type="color" :name="name" :class="'form-control control'" :id="`fld-${id}`" :placeholder="label" :required="required?'required':false" v-model="value"/>
   </div>
   <div v-else-if="type=='checkbox'">
      <div class="input-group" v-for="opt in options" :key="opt">
         <span class="input-group-text input-group-prepend"><input type="checkbox" :id="`fld-${id}-${opt['key']}`" :name="name" :required="required?'required':false" :value="opt['key']"/></span>
         <label class="form-control" :for="`fld-${id}-${opt['key']}`" v-html="opt['value']"></label>
      </div>
   </div>
   <div v-else-if="type=='date'">
      <input type="date" class="form-control control datetimepicker-input" :id="`fld-${id}`" :name="name" :required="required?'required':false" v-model="value" data-toggle="datetimepicker" :data-target="`#fld-${id}`" :placeholder="label"/>
   </div>
   <div v-else-if="type=='datetime'">
      <input type="datetime-local" class="form-control control datetimepicker-input" :id="`fld-${id}`" :name="name" :required="required?'required':false" v-model="value" data-toggle="datetimepicker" :data-target="`#fld-${id}`" :placeholder="label"/>
   </div>
   <div v-else-if="type=='email'">
      <input type="email" :name="name" :class="'form-control control'" :id="`fld-${id}`" :placeholder="label" :required="required?'required':false" v-model="value"/>
   </div>
   <div v-else-if="type=='file'">
      <input type="file" :name="name" :class="'form-control control'" :id="`fld-${id}`" :placeholder="label" :required="required?'required':false" v-model="value" :accept="(accept)?accept:'*'"/>
   </div>
   <div v-else-if="type=='float'">
      <input type="number" :name="name" :class="'form-control control'" :id="`fld-${id}`" :placeholder="label" :required="required?'required':false" v-model="value" :step="(step)?step:'any'"/>
   </div>
   <div v-else-if="type=='hidden'">
      <input type="hidden" :name="name" :class="'form-control control'" :id="`fld-${id}`" :placeholder="label" :required="required?'required':false" v-model="value"/>
   </div>
   <div v-else-if="type=='number' || type=='int'">
      <input type="number" :name="name" :class="'form-control control'" :id="`fld-${id}`" :placeholder="label" :required="required?'required':false" v-model="value"/>
   </div>
   <div v-else-if="type=='password'">
      <input type="password" :name="name" :class="'form-control control'" :id="`fld-${id}`" :placeholder="label" :required="required?'required':false" v-model="value"/>
   </div>
   <div v-else-if="type=='radio'">
      <div class="input-group" v-for="opt in options" :key="opt">
         <span class="input-group-text input-group-prepend"><input type="radio" :id="`fld-${id}-${opt['key']}`" :name="name" :required="required?'required':false" :value="opt['key']" v-model="value"/></span>
         <label class="form-control" :for="`fld-${id}-${opt['key']}`" v-html="opt['value']"></label>
      </div>
   </div>
   <div v-else-if="type=='range'">
      <input type="range" :name="name" :class="'form-control control'" :id="`fld-${id}`" :placeholder="label" :required="required?'required':false" v-model="value" :min="(min)?min:0" :max="(max)?max:100"/>
   </div>
   <div v-else-if="type=='tel'">
      <input type="tel" :name="name" :class="'form-control control'" :id="`fld-${id}`" :placeholder="label" :required="required?'required':false" v-model="value"/>
   </div>
   <div v-else-if="type=='text'">
      <input type="text" :name="name" :class="'form-control control'" :id="`fld-${id}`" :placeholder="label" :required="required?'required':false" v-model="value"/>
   </div>
   <div v-else-if="type=='textarea'">
      <textarea :name="name" :class="'form-control control'" :id="`fld-${id}`" :placeholder="label" :required="required?'required':false" v-model="value"></textarea>
   </div>
   <div v-else-if="type=='time'">
      <input type="time" class="form-control control datetimepicker-input" :id="`fld-${id}`" :name="name" :required="required?'required':false" v-model="value" data-toggle="datetimepicker" :data-target="`#fld-${id}`" :placeholder="label"/>
   </div>
   <div v-else-if="type=='url'">
      <input type="url" :name="name" :class="'form-control control'" :id="`fld-${id}`" :placeholder="label" :required="required?'required':false" v-model="value"/>
   </div>
   <div v-else>
      Unknown/Unsupported field-type: {{type}}
   </div>
   <div class="helptext" c-if="helptext" :id="`des-${id}`">{{ helptext }}</div>
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
   ,props: {
      'type': {'type': String}
      , 'name': {'type': String}
      , 'label': {'type': String}
      , 'helptext': {'type': String}
      , 'options': {'type': String}
      , 'required': {'type': Boolean}
      , 'value': {'type': String}
      , 'step': {'type': Number}
      , 'format': {'type': String}
      , 'min': {'type': Number, 'default': 0}
      , 'max': {'type': Number, 'default':100}
      , 'accept': {'type': String, 'default': '*'}
      , 'readonly': {'type': Boolean, 'default':false}
      , 'readonlyWhenAutoPopulated': {'type': Boolean, 'default':true}
      , 'disabled': {'type': Boolean, 'default':false}
      , 'autopopulate': {'type': Boolean, 'default':true}
   }
   ,data: function(){
      return {'id':uuidv4(), 'isReadOnly':this.readonly, 'isDisabled':this.disabled}
   }
   ,mounted: function(evt){
      let vm=this;
      let ctrl=$(`#fld-${vm.id}`);
      console.debug(ctrl);
      if(vm.type=='date'){
         fmt=vm.format?vm.format:'YYYY-MM-DD';
         $(`#fld-${vm.id}`).datetimepicker({'format':fmt});
      }else if(vm.type=='time'){
         fmt=vm.format?vm.format:'HH:mm';
         $(`#fld-${vm.id}`).datetimepicker({'format':fmt});
      }else if(vm.type=='datetime'){
         fmt=vm.format?vm.format:'YYYY-MM-DD HH:mm';
         $(`#fld-${vm.id}`).datetimepicker({'format':fmt});
      }

      //Populate from queryParam
      if(vm.autopopulate){
         let val=getQueryParam(vm.name);
         if(typeof(val)!='undefined'){
            vm.value=val;
            if(vm.readonlyWhenAutoPopulated) vm.isReadOnly=true; 
         }
      }

      //Populate readonly and disabled
      if(vm.isReadOnly)$(ctrl).prop('readonly', 'readonly');
      if(vm.isDisabled)$(ctrl).prop('disabled', 'disabled');
   }
   ,watches: {
       isReadOnly: function(newVal, oldVal){ $(`#fld-${this.id}`).prop('readonly', newVal); }
      ,isDisabled: function(newVal, oldVal){ $(`#fld-${this.id}`).prop('disabled', newVal); }
   }
};
</script>

<style>
.helptext{ color:#777; }
</style>
