/*
 * File: /src/webframe/static/js/preloadImage.js
 * Author:     Kenson Man <kesnon.idv.hk@gmail.com>
 * Date:       2020-05-23 14:32
 * Desc:       Provide the preloadImage( src, callback) and preloadImages( src..., callback ) function.
 *
 * Date:       2022-09-14 13:50
 * Desc:       Move the features into Webframe namespace
 */
Webframe._preloadImage=function(src, callback){
   let img=new Image();
   img.onload=callback;
   img.src=src;
};

Webframe.preloadImage=function(src, callback){
   console.debug(`Preloading imge: ${src}...`);
   if(src instanceof Node || src instanceof NodeList){
      Webframe.nodeList(src).forEach(img=>{
         if(img.attributes.src)
            Webframe._preloadImage(img.attributes[src], callback);
         if(img.attributes['preload-images'])
            img.attributes['preload-images'].split(',').forEach(pl=>{ Webframe._preloadImage(pl, callback) });
      });
   }else if(Array.isArray(src)
      src.forEach(pl=>{ Webframe._preloadImage(pl, callback) })
   else 
      Webframe._preloadImage(src, callback);
};

Webframe.preloadImages=Webframe.preloadImage; //Alias for backward compatibility
