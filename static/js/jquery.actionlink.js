// Date: 2016-03-30 13:34
// File: jquery.actionlink.js
// Version: v2.0
// The jquery plugin for slide-show widget
// All rights reserved
//

;(function($) {
	$.extend($, {actionlink:{
		handle: function( evt ){
			console.log('handle');
			var action=$(this).attr('action');
			var target=$(this).attr('target');
			var url=$(this).attr('href');
			if(action==='link' || action==='url')
				window.open(url, target);
			else if(action==='script')
				eval(url);
			else
				alert('Unknow action');
			return false;
		},
	}});
	
	// jQuery plugin definition
	$.fn.actionlink = function(params) {
		// merge default and user parameters
		params = $.extend({src:null,action:null,target:null}, params);
		
		$(this).click(jQuery.actionlink.handle);
		
		// allow jQuery chaining
		return this;
	};
})(jQuery);
