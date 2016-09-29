jQuery.validator.addMethod('dateformat', function(val, element, params){
	if(typeof(params)=='undefined')
		params='YYYY-MM-DD';
	return this.optional(element) || moment(val, params, true).isValid();
}, 'Please enter the value in valid date-format');
