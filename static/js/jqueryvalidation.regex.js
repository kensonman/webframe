// File: jqueryvalidation.regex.js
// Date: 2016-09-29 17:56
// Author: Kenson Man
//
// The jquery-validation rule for [jQuery Validation Plugin](https://jqueryvalidation.org/).
//
jQuery.validator.addMethod('regex', function(val, element, params){
	if(typeof(params)=='undefined')
		params='^.*$';
	return this.optional(element) || new RegExp(params).test(val);
}, 'Please enter the value in valid format');
