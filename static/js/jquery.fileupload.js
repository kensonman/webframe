/*
**Date** 2017-05-23 22:52
**File** jquery.fileupload.js
**Version** v1.0
**Desc** The jquery plugin for file-upload widget.
**License** BSD 

#Usage
    $('selector').wf_fileupload(Options);

# Options
*/

;(function($) {
   // jQuery plugin definition
   $.fn.wf_fileupload = function(params) {
      // merge default and user parameters
      params = $.extend({}, params);

      $(this).each(function(){
            $(this).change(function( evt ){
               var val=$(this).val();
               $(this).parents('.input-group:first').find('.form-control')
                  .val(val)
                  .text(val)
               ;
            });
      });
      
      // allow jQuery chaining
      return this;
   };
})(jQuery);

$(document).ready(function(){ $('input[type=file]').wf_fileupload(); });
