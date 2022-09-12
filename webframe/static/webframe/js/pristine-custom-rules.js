/**
 * File:       webframe/static/webframe/js/pristine-custom-rules.js
 * Author:     Kenson Man <kenson.idv.hk@gmail.com>
 * Required: 
 *    - (moment.js)[http://momentjs.com]
 * Method:
 *    - dateformat:  Used to required the input must be fit with specific date-format[http://momentjs.com/docs/#/displaying/]. 
 *                   The dateformat can be defined according to MomentJS format (default is YYYY-MM-DD);
 *                      e.g: data-pristine-dateformat="YYYY-MM-DD"
 *                      e.g: data-pristine-dateformat="DD/MM/YYYY"
 *    - mindate:     Used to required the input must be on or after the specified date.
 *                      e.g: data-pristine-mindate="2022-06-13"
 *                      e.g: data-pristine-mindate="13/06/2022,DD/MMYYYY"
 *    - maxdate:     Used to required the input must be on or before the specified date.
 *                      e.g: data-pristine-maxdate="2022-06-13"
 *                      e.g: data-pristine-maxdate="13/06/2022,DD/MMYYYY"
 */

Pristine.addValidator("dateformat", function(value, dateformat='YYYY-MM-DD') {
   if(dateformat===undefined) dateformat='YYYY-MM-DD';
   if(value)
      return moment(value, dateformat, true).isValid();
   return true;
}, 'Please enter the value in valid date-format: ${1}', 10, false);

Pristine.addValidator('mindate', function(value, criteria, dateformat='YYYY-MM-DD'){
   if(dateformat===undefined) dateformat='YYYY-MM-DD';
   if(value){
      criteria=moment(criteria, dateformat, true);
      value=moment(value, dateformat, true);
      return value.isSameOrAfter(criteria);
   }
   return true;
}, 'The minimum value is ${1}', 10, false);

Pristine.addValidator('maxdate', function(value, criteria, dateformat='YYYY-MM-DD'){
   if(dateformat===undefined) dateformat='YYYY-MM-DD';
   if(value){
      criteria=moment(criteria, dateformat, true);
      value=moment(value, dateformat, true);
      return value.isSameOrBefore(criteria);
   }
   return true;
}, 'The maximum value is ${1}', 10, false);

//The regex validator is deprecated. The Pristine provided the "pattern" instead.
//Just to keep it for backward compatibility.
Pristine.addValidator('regex', function(value, criteria='^.*$'){
   if(criteria===undefined || criteria=='regex') criteria='^.*$';
   if(value)
      return new RegExp(criteria).test(value);
   return true;
}, 'Please enter the value in valid format: ${1}', 10, false);
