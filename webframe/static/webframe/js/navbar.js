//Date: 2022-08-16 10:26
//Author: Kenson Man <kenson.idv.hk@gmail.com>
//Desc:   Provide the basic feature for generating the header by WEBFRAME's header data
(function($){
   let generateMenu=function(data){
      let menu=$('<ul></ul>').attr({'id': data.id}).addClass('navbar-nav');
      $(data.childs).each((idx, val)=>{
         generateMenuItem(val).appendTo(menu);
      });
      return menu;
   }

   let generateMenuItem=function(data){
      let menuitem=$('<li></li>').attr({'id': data.id,}).addClass('nav-item');
      let a=null;
      if(data.childs && data.childs.length>0){
         $(menuitem).addClass('dropdown');
         a=$('<a></a>').addClass('nav-link dropdown-toggle').attr({
               'id': `${data.id}-dropdownTrigger`,
               'role': 'button',
               'data-toggle': 'dropdown',
               'aria-expanded': 'false',
            }).appendTo(menuitem);
         let dl=$('<ul></ul>').attr('id', `${data.id}-dropdown`).addClass('dropdown-menu').appendTo(menuitem);
         $(data.childs).each((idx, val)=>{ generateMenuItem(val).appendTo(dl); })
      }else{
         let txt=$('<span></span>').attr({'id': `${data.id}-txt`}).addClass('webframe-navitem').appendTo(menuitem);
         a=$('<a></a>').attr({'id':`${data.id}-lnk`}).addClass('nav-link').appendTo(txt);
      }
      if(data.props.href)$(a).attr('href', data.props.href);
      if(data.props.target)$(a).attr('a', data.props.target);
      if(data.props.title)$(a).attr('a', data.props.title);
      if(data.onclick)$(a).attr('onclick', data.onclick);
      if(data.mousein)$(a).attr('onmousein', data.mousein);
      if(data.mouseout)$(a).attr('onmouseout', data.mouseout);
      if(data.icon)$(a).append(`<i class="fas ${data.icon}"></i> `);
      if(data.label){
         let text=data.label;
         text=text.replace(/\{(\w+)\}/, '%($1)s');
         text=interpolate(text, USER, true);
         $(a).append(`<span>${text}</span>`);
      }
      return menuitem;
   }

   $.fn.wfnavbar=function(opts){
      $(this).each(function(){
         $(this)
            .addClass('navbar navbar-expand-lg navbar-light bg-light webframe-navbar')
            .text('loading...');
         $.ajax({
            context: this,
            url: $(this).attr('href'),
            success: (data)=>{
               $(this).empty();
               let brand=$('<a></a>').attr({ 'id':`${data.id}-brand`, 'href':$(data).attr('props').href }).addClass('navbar-brand').appendTo(this);
               if($(data.props).attr('class'))$(brand).addClass($($(data).attr('props')).attr('class'));
               if(data.props.styles)$(brand).css(data.props.styles);
               if(data.props.title)$(brand).attr('title', data.props.title);
               if(data.props.target)$(brand).attr('target', data.props.target);
               if(data.onclick)$(brand).attr('onclick', data.onclick);
               if(data.mousein)$(brand).attr('onmousein', data.mousein);
               if(data.mouseout)$(brand).attr('onmouseout', data.mouseout);
               let lbl=$('<label></label>').attr({ 'for':$(data).attr('id') }).text(data.label).appendTo(brand);
               
               let brandToggle=$('<button></button>').attr({
                     'type': 'button',
                     'data-toggle': 'collapse',
                     'data-target': `[id='${data.id}']`,
                     'aria-controls': data.id,
                     'aria-expanded': false,
                     'aria-label': 'Toggle navigation',
                  })
                  .addClass('navbar-toggler')
                  .append('<span class="navbar-toggler-icon"></span>')
                  .appendTo(this)
               ;

               let menubar=$('<div></div>').attr('id', data.id).addClass('collapse navbar-collapse justify-content-between').appendTo(this);
               $(data.childs).each((idx, val)=>generateMenu(val).appendTo(menubar));
               $(menubar).find('.navbar-nav:first').addClass('mr-auto');
            },
            error: (jqXHR, txtStatus, err)=>{
               console.warning(`Error when generate the wfnavbar: ${txtStatus}`);
               console.error(err);
            },
         });
      });
   };
}(jQuery));
