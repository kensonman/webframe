//Date: 2022-08-16 10:26
//Date: 2022-09=16 15:28 (Rewrite for Vanilla JS)
//Author: Kenson Man <kenson.idv.hk@gmail.com>
//Desc:   Provide the basic feature for generating the header by WEBFRAME's header data

/**
 * Create the element
 * @param tagName The html tag, example: a, div, span
 * @param props   The complex properties of the element. example:
 *                {classes: 'btn-outline-info btn-info', styles: 'cursor: pointer; font-weight:bold', attrs: {onmouseout: '', onclick:''}}
 * @param parent  The parent element. (Optional). It will append this element automatically.
 */
Webframe.createElement=function ( tagName, props={classes:null, styles:null, attrs:null, text:null, html:null}, parent=null){
   let elem=document.createElement(tagName);
   if(props.classes){
      if(typeof(props.classes)==='string') props.classes=props.classes.split(' ');
      props.classes.forEach(cls=>{elem.classList.add(cls);});
   }
   if(props.styles) elem.style.cssText=props.styles;
   if(props.attrs){
      let array=props.attrs;
      if(!Array.isArray(array))array=[props.attrs];
      array.forEach(attrs=>{
         Object.keys(attrs).forEach(name=>{ 
            elem.setAttribute(name, attrs[name]) 
            if(name=='href' && !attrs[name].startsWith('/'))
               axios.get(`${Webframe.URL_API}?url=${attrs[name]}`).then(url=>{ elem.setAttribute('href', url.data); });
         });
      });
   }
   if(props.text)elem.innerText=props.text;
   if(props.html)elem.innerHTML=props.html;
   if(parent)parent.appendChild(elem);
   return elem;
}

Webframe._generateNavbarMenu=function( data, menubar ){
   let menu=Webframe.createElement('ul', {classes:'navbar-nav', attrs:{'id':data.id}}, menubar);
   data.childs.forEach(mi=>{ Webframe._generateNavbarMenuItem(mi, menu); });
   return menu;
}

Webframe._generateNavbarMenuItem=function( data, menu ){
   let item=Webframe.createElement('li', {
      classes: 'nav-item',
      attrs: {id: data.id},
   }, menu);

   let a;
   if(data.childs && data.childs.length>0){
      item.classList.add('dropdown');
      a=Webframe.createElement('a', {classes: 'nav-link dropdown-toggle', attrs:[
         data.props,
         {
            id: `${data.id}-dropdownTrigger`,
            role: 'button',
            'data-toggle':'dropdown',
            'aria-expanded': false,
         }]}, item);
      let dl=Webframe.createElement('ul', {classes:'dropdown-menu', attrs:{id:`${data.id}-dropdown`}}, item);
      data.childs.forEach(child=>{ Webframe._generateNavbarMenuItem(child, dl); });
   }else{
      let txt=Webframe.createElement('span', {classes: 'webframe-navitem', attrs:{id:`${data.id}-txt`}}, item);
      a=Webframe.createElement('a', {classes:'nav-link', attrs:[{id:`${data.id}-lnk`}, data.props]}, txt);
   }
   if(data.icon)Webframe.createElement('i', {classes:`fas ${data.icon}`}, a);
   if(data.label){
      let txt=data.label;
      txt=txt.replace(/\{(\w+)\}/, '%($1)s');
      txt=interpolate(txt, USER, true);
      Webframe.createElement('span', {text:txt}, a);
   }
   return item;
}

Webframe.loadNavBar=function( qsResult ){
   if(!qsResult) return Webframe.loadNavBar(document.querySelectorAll('navbar[href]'));

   qsResult.forEach( elem => {
      elem.innerText='Loading...'
      console.debug(`Loading navbar from ${elem.attributes['href'].value} ...`);
      elem.classList.add('navbar', 'navbar-expand-lg', 'navbar-light', 'bg-light', 'webframe-navbar');
      axios.get(elem.attributes['href'].value)
         .then(rep=>{
            let data=rep.data;
            console.debug(data);
            elem.innerHTML=''; //Clear all elements
            elem=Webframe.createElement('div', {classes:'container-fluid'}, elem);
            let brand=Webframe.createElement('a', {
               classes:data.props['class'], 
               styles:data.props['styles'], 
               attrs: [{'id':`${data.id}-brand`, 'href':data.props.href?data.props.href:'/'}, data.props]
               }, elem);
            brand.classList.add('navbar-brand');
            if(data.icon)Webframe.createElement('i', {classes: `fas ${data.icon} mx-1`}, brand);
            let lbl=Webframe.createElement('label', {attrs: {'for':data.id}, text:data.label}, brand);
            if(data.image){
               lbl.innerText='';
               Webframe.createElement('img', {attrs:{src:data.image, title:data.label}, classes:'webframe-navbar-image'}, lbl);
            }
            let toggle=Webframe.createElement('button', {
               attrs: {
                  'type': 'button', 
                  'data-toggle': 'collapse',
                  'data-target': `[id='${data.id}']`,
                  'aria-controls': data.id,
                  'aria-expanded': false,
                  'aria-label': 'Toggle navigation',
               },
               classes: 'navbar-toggler',
               html: '<span class="navbar-toggler-icon"></span>',
            }, elem);
            let menubar=Webframe.createElement('div', {
               attrs: {'id': data.id},
               classes: 'collapse navbar-collapse justify-content-between',
            }, elem);
            data.childs.forEach(menu=>{ Webframe._generateNavbarMenu( menu, menubar ); });
            menubar.querySelector('.navbar-nav:last-child').classList.add('mr-auto');
         })
         .catch(err=>{
            console.warn(`Error when generate the wfnavbar`);
            console.error(err);
         })
     ;
   });
}
