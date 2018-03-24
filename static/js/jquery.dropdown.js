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
        <button type="button" data-toggle="dropdown">Label</button>
        <ul class="dropdown-menu">
                <li><a href="#" class="item" val="1">Opt1</a></li>
                <li><a href="#" class="item" val="two">Opt2</a></li>
                <li><a href="#" class="item" val="value will be here">Opt3</a></li>
                <li><a href="#" class="item">Opt4</a></li><!-- def value is the "Opt4" -->
        </ul>
     </div>
    <script type="text/javascript"><!--
    $(document).ready(function(){
        $('div.dropdown').wfdropdown({
                'items':'a.item',
                'onclick':jQuery.wfdropdown.onclick,
                'value': 'input:first',
        });
    });
    //--></script>

# AJAX Example
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
             'ajax':    {url: 'server.php, method: 'GET', }, //Refer to [jQuery.ajax(opts)](http://api.jquery.com/jquery.ajax/#jQuery-ajax-settings]
             'name': 'nameFld',
             'id':   'idFld',
             'success': function(){ /* The function will be override ajax-options.success */ },
        });
    });
    //--></script>

    <!-- server.php -->
    [
      {"idFld":"05574364-e97d-4b39-87e5-f3c6428a41e0", "nameFld":"Opt1"}, 
      {"idFld":"aef1d4ca-5bda-42d1-8b52-64e2575e9d0e", "nameFld":"Opt2"}, 
      {"idFld":"30dcac3c-dc5e-4bf5-a1a2-ea5bf3f46e57", "nameFld":"Opt3"}, 
    ]

*/

;(function($) {
   $.extend($, {wfdropdown:{
      onclick: function( evt ){
         var element=$(this).parents('.wfdropdown:first');
         var value=null;
         if(typeof($(this).attr('val'))=='undefined')
            value=$(this).text();
         else
            value=$(this).attr('val');
         $(element)
            .find($(element).attr('value')).val(value).end()
            .find('.wfdropdown_lbl').text($(this).text()).end()
            .trigger('change')
         ;
      },
      success: function( data ){
      },
   }});
   
   // jQuery plugin definition
   $.fn.wfdropdown = function(params) {
      // merge default and user parameters
      params = $.extend({'items':'a.item','value':'input:first','onclick':jQuery.wfdropdown.onclick,'success':jQuery.wfdropdown.success,'element':'li','name':'nameFld','id':'idFld','ajax':null}, params);
      var text=$(this).find(params['value']).val();
      var val=$(this).find('a[val="'+text+'"]').html();
      if(val){
         $(this).find(params['value']).val(text);
         text=val;
      }else{
         text=$(this).find('button:first').html();
      }
      
      $(this)
         .find('button').empty().append('<span class="wfdropdown_lbl">'+text+'</span><span class="caret"></span>').end()
         .addClass('wfdropdown')
         .attr({'value':params.value})
         .find(params.items).click(params.onclick)
      ;

      if(params.ajax!=null){
      }
      
      // allow jQuery chaining
      return this;
   };
})(jQuery);
