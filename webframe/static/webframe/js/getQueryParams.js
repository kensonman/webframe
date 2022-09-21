/**
 * File:       /src/webframe/static/js/getQueryParams.js
 * Author:     Kenson Man <kenson@mansonsolutions.hk>
 * Date:       2020-06-10 16:21
 * Desc:       Provide the getQueryParam(name) and getQueryParams() javascript function.
 *
 * Date:       2022-09-14 13:37
 * Desc:       Move the function into Webframe namespace
 */
Webframe.getQueryParams=function (qs=null) {
   if(qs==null)qs=window.location.search;
   params={};
   if(qs){
      vars=qs.substr(1).split('&');
      for(var i=0; i<vars.length; i++){
         pair=vars[i].split('=');
         key=decodeURIComponent(pair[0]);
         val=decodeURIComponent(pair[1]);
         t=typeof(params[key]);
         if(t=='undefined' || t=='function') //t=='function' is used for key is reserved keywords, e.g.: filter
            params[key]=val
         else if(t=='string')
            params[key]=Array(params[key], val)
         else if(Array.isArray(params[key]))
            params[key].push(val);
         else{
            console.log('Supported type['+key+']: '+t);
         }
      }
   }
   return params
};

Webframe.getQueryParam=function ( name, queryStr=null ){
   return Webframe.getQueryParams(queryStr)[name];
};
