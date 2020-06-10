/**
 * File:       /src/webframe/static/js/getQueryParams.js
 * Author:     Kenson Man <kenson@mansonsolutions.hk>
 * Date:       2020-06-10 16:21
 * Desc:       Provide the getQueryParam(name) and getQueryParams() javascript function.
 */

function getQueryParams() {
   qs=window.location.search;
   params=Array();
   if(qs){
      vars=qs.substr(1).split('&');
      for(var i=0; i<vars.length; i++){
         pair=vars[i].split('=');
         key=decodeURIComponent(pair[0]);
         val=decodeURIComponent(pair[1]);
         t=typeof(params[key]);
         if(t=='undefined')
            params[key]=val
         else if(t=='string')
            params[key]=Array(params[key], val)
         else
            params[key].push(val);
      }
   }
   return params
};

function getQueryParam( name ){
   return getQueryParams()[name];
};
