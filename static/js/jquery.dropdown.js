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
   <div class="dropdown">
      <input type="hidden" name="field-name" value="default-value"/>
      <button type="button" data-toggle="dropdown" class="btn btn-success">-- Please Select --</button>
      <ul class="dropdown-menu">
            <li><a class="dropdown-item" val="1" name="Opt1">Opt1</a></li>
            <li><a class="dropdown-item" val="two" name="Opt2</a>"></li>
            <li><a class="dropdown-item" val="value will be here" name="Opt3">Opt3</a</a>></li>
            <li><a class="dropdown-item" val="Opt4"></li><!-- def value is the "Opt4</a>" -->
      </ul>
    </div>
   <script type="text/javascript"><!--
   $(document).ready(function(){
      $('div.dropdown').wfdropdown({
            'items':'a.dropdown-item',
            'onclick':jQuery.wfdropdown.onclick,
            'value': 'input:first',
      });
   });
   //--></script>

{%url 'newsletters'%}?filter= AJAX Example
   <div class="dropdown">
      <input type="hidden" name="field-name" value="default-value"/>
      <button type="button" data-toggle="dropdown">Label</button>
      <ul class="dropdown-menu">
      </ul>
    </div>
   <script type="text/javascript"><!--
   $(document).ready(function(){
      $('div.dropdown').wfdropdown({
         'items':'a.item',
         'onclick':jQuery.wfdropdown.onclick,
         'value': 'input:first',
         'element': 'li',
         'ajax':   {url: 'server.php, method: 'GET', }, //Refer to [jQuery.ajax(opts)](http://api.jquery.com/jquery.ajax/#jQuery-ajax-settings]
         'name': 'name',
         'id':   'id',
         'success': function(){ }, //The function will be override ajax-options.success
      });
   });
   //--></script>

   <!-- server.php -->
   [
      {"id":"05574364-e97d-4b39-87e5-f3c6428a41e0", "name":"Opt1"}, 
      {"id":"aef1d4ca-5bda-42d1-8b52-64e2575e9d0e", "name":"Opt2"}, 
      {"id":"30dcac3c-dc5e-4bf5-a1a2-ea5bf3f46e57", "name":"Opt3"}, 
   ]

   <!-- server.php -->
   {
      "result": [
         {"id":"05574364-e97d-4b39-87e5-f3c6428a41e0", "name":"Opt1"}, 
         {"id":"aef1d4ca-5bda-42d1-8b52-64e2575e9d0e", "name":"Opt2"}, 
         {"id":"30dcac3c-dc5e-4bf5-a1a2-ea5bf3f46e57", "name":"Opt3"}, 
      ],
   }

*/

;(function($) {
   $.extend($, {wfdropdown:{
      onclick: function( evt ){
         var element=$(this).parents('.wfdropdown:first');
         var value=null;
         var lastVal=$(element).find('input:first').val();
         var symbol=$(element).attr('wfsymbol')==''?'':'<i class="symbol-dropdown fas '+$(element).attr('wfsymbol')+'"></i>';
         if(typeof($(this).attr('val'))=='undefined')
            value=$(this).text();
         else
            value=$(this).attr('val');
         $(element)
            .find('button:first').empty().text($(this).text()).append(symbol).end()
            .find('input:first').val(value)
               .trigger('change', {'from': lastVal, 'to':value})
            .end()
            .trigger('change', {'from': lastVal, 'to':value})
         ;
     },
     success: function( data ){
        var result=('result' in data)?data.result:data;
        var menu=$(this).find('.dropdown-menu');
        $(menu).find('.dropdown-item').remove();
        for(var i=0; i<result.length; i++){
           var entry=result[i];
           var item=$('<'+$(this).attr('wfelement')+'/>')
              .addClass('dropdown-item')
              .appendTo(menu)
              .attr('name', $(entry).attr($(this).attr('wfname')))
              .attr('val', $(entry).attr($(this).attr('wfid')))
           ;
           $.wfdropdown.populate(item);
        }
        if(!$(this).find('input').hasClass('required')){
           var item=$('<'+$(this).attr('wfelement')+'/>')
              .addClass('dropdown-item')
              .prependTo(menu)
              .attr('name', $(this).attr('wfPlsSelect'))
              .attr('val', '')
           ;
           $.wfdropdown.populate(item);
        }
        var selected=$(this).find('input:first').val();
        var label=$(this).find('.dropdown-item[val="'+selected+'"]:first').text();
        $(this).find('button:first').text(label).append($('<span></span>').text()).append('<i class="symbol-dropdown fas '+$(this).attr('wfsymbol')+'"></i>');
        $(this).trigger('ready');
     },
     populate: function( item ){
        var name=$(item).attr('name');
        if(typeof(name)=='undefined')name=$(item).text();
        var val=$(item).attr('val');
        $(item).empty().append($('<a></a>').text(name).attr({'href':'#','val':val}).addClass('dropdown-item').on('click', $.wfdropdown.onclick));
     },
   }});
   
   // jQuery plugin definition
   $.fn.wfdropdown = function(params) {
     // merge default and user parameters
     params = $.extend({
      'items':'a.dropdown-item',
      'value':'input:first',
      'symbol': 'fa-caret-down',
      'onclick':jQuery.wfdropdown.onclick,
      'success':jQuery.wfdropdown.success,
      'element':'li',
      'name':'name',
      'id':'id',
      'ajax':null
     }, params);
     if($(this).length<1){
        console.log('No element found for dropdown.');
        return this;
     }

     $(this).addClass('wfdropdown');
     //If ajax
     if(params.ajax!=null){
       params.ajax.success=params.success; //Overwrite the success function
       params.ajax.context=this;
       $(this).attr({'wfelement':params.element, 'wfname':params.name, 'wfid':params.id, 'wfPlsSelect':$(this).text(), 'wfsymbol':params.symbol});
       $(this).on('ready', function(){
         $(this).find('a.dropdown-item').off('click').on('click', params.onclick); //Remove the default handler when populate, use the custom onclick instead.
       });
       $.ajax(params.ajax);
     }

     var selected=$(this).find('input:first').val();
     var label=$(this).find('.dropdown-item[val="'+selected+'"]:first').text();
     var symbol=params.symbol==''?'':'<i class="symbol-dropdown fas '+params.symbol+'"></i>';
     if(label.length<1) label=$(this).find('buttton:first').text();
     $(this)
       .attr('wfsymbol', params.symbol)
       .find(params.items).each(function(){ $.wfdropdown.populate( this ); }).end()
       .find('button:first').text(label).append(symbol)
     ;
     if(params.ajax==null)$(this).trigger('ready');
     return this;
   };
})(jQuery);
