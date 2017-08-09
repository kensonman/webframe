//FileName: jqueryvalidation.date.js
//Author:   Kenson Man <kenson@kenson.idv.hk>
//
//Description: The file provide the date validation rules for (jqueryvalidation)[https://jqueryvalidation.org]
//
//Required: 
//    - (monent.js)[http://momentjs.com]
//
//Methods:
//     dateformat:  Used to required the input must be fit with specific date-format[http://momentjs.com/docs/#/displaying/].
//            e.g: dateformat="YYYY-MM-DD"
//            e.g: dateformat="DD/MM/YYYY"
//
//     mindate:     Used to request a date that greater than or equals to the specific date[http://momentjs.com/docs/#/displaying/].
//                  The parameter should be specified by JSON format.
//            e.g: mindate="{&quote;dateformat&quote;:&quote;YYYY-MM-DD&quote;, &quote;value&quote;:&quote;2017-08-09&quote;}" 
//
//     maxdate:     Used to request a date that less than or equals to the specific date[http://momentjs.com/docs/#/displaying/].
//                  The parameter should be specified by JSON format.
//            e.g: maxdate="{&quote;dateformat&quote;:&quote;YYYY-MM-DD&quote;, &quote;value&quote;:&quote;2017-08-09&quote;}" 

jQuery.validator.addMethod('dateformat', function(val, element, params){
	if(typeof(params)=='undefined')
		params='YYYY-MM-DD';
	return this.optional(element) || moment(val, params, true).isValid();
}, 'Please enter the value in valid date-format');


jQuery.validator.addMethod('mindate', function(val, element, params){
   val=val.trim();
   if(this.optional(element) && val=="")return true;
	if(typeof(params)=='undefined')
		params='{}';
   try{
      params=JSON.parse(params);
      params=jQuery.extend({}, JSON.parse(params), {"dateformat":"YYYY-MM-DD", "value":monent().format("YYYY-MM-DD")});
      params.value=monent(params.value, params.dateformat, true);
      val=moment(val, params.dateformat, true);
      return val.isSame(params.value) || params.value.isBefore(val);
   }catch(err){
      return false;
   }
}, 'Please enter the value in valid date-format');

jQuery.validator.addMethod('maxdate', function(val, element, params){
   val=val.trim();
   if(this.optional(element) && val=="")return true;
	if(typeof(params)=='undefined')
		params='{}';
   try{
      params=JSON.parse(params);
      params=jQuery.extend({}, JSON.parse(params), {"dateformat":"YYYY-MM-DD", "value":monent().format("YYYY-MM-DD")});
      params.value=monent(params.value, params.dateformat, true);
      val=moment(val, params.dateformat, true);
      return val.isSame(params.value) || params.value.isAfter(val);
   }catch(err){
      return false;
   }
}, 'Please enter the value in valid date-format');
