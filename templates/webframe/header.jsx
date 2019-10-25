{%load i18n urlexists getitem%}
function Menu(props){
   return (
      <div id="pnl_header"><nav className="navbar navbar-expand-lg navbar-expand-md navbar-light bg-light">
         <a className="navbar-brand" href="{%if 'dashboard'|urlexists%}{%url 'dashboard'%}{%else%}/{%endif%}" title="Brand">Brand</a>
         <div className="collapse navbar-collapse" id="navbarCollapsibleContent">
            <ul className="navbar-nav mr-auto">
               <MenuItem url="#" text="Action"/>
               <MenuItem url="#" text="Another action"/>
               <MenuDropdown text="Dropdown">
                  <MenuItem url="#" text="Action"/>
                  <MenuItem url="#" text="Another action"/>
                  <MenuSeparator/>
                  <MenuItem url="#" text="Something else here"/>
               </MenuDropdown>
               <MenuInput action="" text="Searching..." icon="search" name="q" style={%templatetag openvariable%}'width': '200px'{%templatetag closevariable%}/>
            </ul>

            <ul className="nav navbar-nav navbar-right">
               <MenuDropdown icon="globe">{%for l in LANGS%}
                  <MenuItem url="?lang={{l|getitem:0}}" text="{{l|getitem:1}}"/>
               {%endfor%}</MenuDropdown>
               {%if user.is_staff%}
                  <MenuItem url="{%url 'admin:index'%}" icon="cogs" text="{%trans 'control-panel'%}"/>
               {%endif%}
               {%if user.is_authenticated%}
                  {%if 'webframe:prefs'|urlexists or 'webframe:logout'|urlexists%}
                     <MenuDropdown text="{%blocktrans with username=user.get_full_name|default:user.username%}Hi, {{username}}{%endblocktrans%}">
                        {%if 'webframe:users'|urlexists%}{%if perms.auth.add_user or perms.auth.change_user%}
                           <MenuItem url="{%url 'webframe:users'%}" icon="users" text="{%trans 'users'%}"/>
                        {%endif%}{%endif%}
                        {%if 'webframe:prefs'|urlexists%}
                           <MenuItem url="{%url 'webframe:prefs' user=user%}" icon="cogs" text="{%blocktrans with user=user%}{{user}}'s preferrences{%endblocktrans%}"/>
                        {%endif%}
                        {%if 'webframe:logout'|urlexists%}
                           <MenuSeparator/>
                           <MenuItem url="{%url 'webframe:logout'%}" icon="sign-out-alt" text="{%trans 'logout'%}"/>
                        {%endif%}
                     </MenuDropdown>
                  {%else%}
                     <MenuItem url="#" text="{%blocktrans with username=user.get_full_name%}Hi, {{username}}{%endblocktrans%}"/>
                  {%endif%}
               {%else%}
                  {%if 'webframe:login'|urlexists%}<MenuItem url="{%url 'webframe:login'%}" icon="sign-in-alt" text="{%trans 'login'%}"/>{%endif%}
               {%endif%}
            </ul>
         </div>

         <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarCollapsibleContent" aria-expanded="false" aria-label="Toggle navigation">
           <span className="navbar-toggler-icon"></span>
         </button>
      </nav></div>
   );
};
