/*
 * File: /src/webframe/static/js/preloadImage.js
 * Author:     Kenson Man <kesnon.idv.hk@gmail.com>
 * Date:       2020-05-23 14:32
 * Desc:       Provide the preloadImage( src, callback) and preloadImages( src..., callback ) function.
 */
var preloadImage=function(src, callback){
   console.debug(`Preloading imge: ${src}...`);
   var img=new Image();
   img.onload=callback;
   img.src=src;
};

var preloadImages=function(src, callback){
   var loadedCounter=0;
   if(Array.isArray(src)){
      var length=src.length;
      src.forEach(function(url){
         preloadImage(url, function(){
            loadedCounter++;
            if(loadedCounter==length) callback();
         });
      });
   }else
      preloadImage(src, callback);
};
