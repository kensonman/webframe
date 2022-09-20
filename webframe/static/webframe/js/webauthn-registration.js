/**
 * File:          webframe/static/webframe/js/webauthn-registration.html
 * Author:        Kenson Man <kenson.idv.hk@gmail.com>
 * Date:          2022-09-15 14:06
 * Description:   The file provide the feature(s) for the webframe webauthn registration.
 */
const DEFAULT_DISPLAY_NAME=`${navigator.appCodeName}(${navigator.appVersion.split(' ')[0]})-${navigator.platform}`;
const { startRegistration } = SimpleWebAuthnBrowser;
const registerFrm=document.querySelector('#registerFrm');
const showMsg=(msg, empty=false, details=null)=>{ document.querySelector('#msgPnl').dispatchEvent(new CustomEvent('msg', {detail:{msg:msg, empty:empty, details:details}})) }

document.addEventListener('DOMContentLoaded', evt=>{
   document.querySelector('input[name=displayName]').value=DEFAULT_DISPLAY_NAME;
   Webframe.dropdown(document.querySelector('.fld-authenticator'), {required: true});
   let pristine=new Pristine(registerFrm);
   registerFrm.attributes['pristine']=pristine;
   document.querySelector('#registerBtn').removeAttribute('disabled');
   document.querySelector('#msgPnlHere').appendChild(document.querySelector('#msgPnl'));
   document.querySelector('#msgPnl').classList.add('light');
});

registerFrm.addEventListener('submit', evt=>{
   evt.preventDefault();
   if(!evt.target.attributes['pristine'].validate())return; //Return false immendate when invalid
   evt.target.dispatchEvent(new CustomEvent('toggle', {value: false}));

   let data={};
   if($(this).find('input[name=displayName]').val()=='')
      $(this).find('input[name=displayName]').val(DEFAULT_DISPLAY_NAME);
   data['username']=registerFrm.querySelector('input[name=username]').value;
   data['displayName']=registerFrm.querySelector('input[name=displayName]').value;
   data['authenticator']=registerFrm.querySelector('input[name=authenticator]').value;
   showMsg(gettext('Getting the challenge and related information from server...'), true);
   axios.get(registerFrm.attributes['action'].value, {params:data, headers:{'Accept':'application/json'}})
      .then(rep=>{
         regOpts=rep.data;
         showMsg(gettext('Got server generated Authentication Options, authenticating...'), true, regOpts);
         if(regOpts.newUserExists){
            showMsg(interpolate(gettext('The user is already registered. Please select another one or <a href="%(loginUrl)s" target="_self">Login</a> to register the new public key'), {'loginUrl': URL_LOGIN}, true), false);
            registerFrm.dispatchEvent(new CustomEvent('toggle', {value:true}));
            return;
         }
         startRegistration(regOpts).then(cred=>{
            showMsg(gettext('Got authentication credential, verifying...'), false, cred);
            cred.username=registerFrm.querySelector('input[name=username]').value;
            if(USER){
               cred.username=USER.username;
               registerFrm.querySelector('input[name=username]').value=cred.username;
            }
            cred.displayName=registerFrm.querySelector('input[name=displayName]').value;
            axios.post(registerFrm.attributes.action.value, JSON.stringify(cred), {'headers':{'X-CSRFToken':Cookies.get('csrftoken'), 'Content-Type':'application/json'}}).then(rep=>{
               let data=rep.data;
               showMsg(gettext('Got server verification result'), false, data)
               if(data.verified){
                  showMsg(gettext('Registration successful, the page will be redirected soon...'));
                  window.setTimeout('window.location.href=document.querySelector("input[name=next]").value', 1000);
               }else{
                  showMsg(gettext('Registration failure'));
                  toggleFrm(true);
               }
            }).catch(err=>{throw err});
         });
      })
      .catch(err=>{
         document.querySelector('#registerFrm').dispatchEvent(new CustomEvent('toggle', {value:true}));
         if(err.name==='InvalidStateError')
            document.querySelector('#msgPnl').dispatchEvent('msg', {msg:gettext('Error: Authenticator was probably already registered by user'), empty:false, details:err});
         else
            document.querySelector('#registerFrm').dispatchEvent(new CustomEvent('toggle', {value:false}));
      }); //Log the error when getting AuthOptions
});

registerFrm.addEventListener('reset', evt=>{
   evt.preventDefault();
   document.querySelectorAll('input[name=username],input[name=displayName]').forEach(e=>e.removeAttribute('readonly'));
   document.querySelector('input[name=username]').select();
   document.querySelector('input[name=username]').focus();
   registerFrm.querySelectorAll('input,textarea,select').forEach(input=>input.removeAttribute('readonly'))
   registerFrm.querySelector('input[name=displayName]').value=DEFAULT_DISPLAY_NAME;
   registerFrm.querySelector('input[name=username]').value='';
   registerFrm.querySelector('input[name=authenticator]').value='';
   registerFrm.querySelector('button.dropdown-toggle').innerText=registerFrm.querySelector('button.dropdown-toggle').attributes.default.value;
});

registerFrm.addEventListener('toggle', evt=>{
   if(evt.value){
      evt.target.querySelectorAll('input,select,textarea').forEach(elem=>{ elem.removeAttribute('readonly') });
      evt.target.querySelectorAll('#registerBtn').forEach(elem=>{ elem.removeAttribute('readonly') });
      if(USER){
         evt.target.querySelector('input[name=username]').value=USER.username;
         evt.target.querySelector('input[name=username]').setAttribute('readonly', 'readonly');
      }
   }else{
      evt.target.querySelectorAll('input,select,textarea').forEach(elem=>{ elem.setAttribute('readonly', true) });
      evt.target.querySelectorAll('#registerBtn').forEach(elem=>{ elem.setAttribute('readonly', true) });
   }
});

document.querySelector('input[name=username]').addEventListener('keyup', evt=>{
   if(evt.keycode==13) document.querySelector('input[name=displayName]').focus();
});

document.querySelector('input[name=displayName]').addEventListener('keyup', evt=>{
   if(evt.keycode==13) Webframe.getFirstMatchedParent('form').submit();
});

document.querySelector('#msgPnl').addEventListener('msg', evt=>{
   if(evt.detail.empty)evt.target.replaceChildren();
   if(!evt.detail.msg)return;
   console.info(evt.detail.msg);
   if(evt.detail.details)console.debug(evt.detail.details);
   let msg=document.createElement('li');
   msg.classList.add('animate__animated');
   msg.classList.add('animate__flash');
   msg.innerHTML+=`<span>${evt.detail.msg}</span>`;
   evt.target.appendChild(msg);
});
