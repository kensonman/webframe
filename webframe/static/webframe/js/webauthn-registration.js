var regOpts=null;
var b64=(ab)=>btoa(String.fromCharCode.apply(null, new Uint8Array(ab)));
const { startRegistration } = SimpleWebAuthnBrowser;
const DEFAULT_DEVICE_NAME=`${navigator.appCodeName}(${navigator.appVersion.split(' ')[0]})-${navigator.platform}`;
function showMsg(msg, empty=false, details=null){
   if(empty)document.querySelector('#msgPnl').replaceChildren();
   if(msg==null)return;
   console.info(msg);
   if(details!=null)console.debug(details);
   let elem=document.createElement('li');
   elem.classList.add('animate__animated');
   elem.classList.add('animate__flash');
   elem.innerHTML+=`<span>${msg}</span>`;
   document.querySelector('#msgPnl').appendChild(elem);
}
function toggleFrm(enabled=true){
   if(enabled){
      document.querySelector('#registerFrm').querySelectorAll('input,select,textarea').forEach(elem=>{ elem.removeAttribute('readonly') });
      document.querySelector('#registerFrm').querySelectorAll('#registerBtn').forEach(elem=>{ elem.removeAttribute('readonly') });
      if(USER){
         document.querySelector('#registerFrm').querySelector('input[name=username]').value=USER.username;
         document.querySelector('#registerFrm').querySelector('input[name=username]').setAttribute('readonly', 'readonly');
      }
   }else{
      document.querySelector('#registerFrm').querySelectorAll('input,select,textarea').forEach(elem=>{ elem.setAttribute('readonly', true) });
      document.querySelector('#registerFrm').querySelectorAll('#registerBtn').forEach(elem=>{ elem.setAttribute('readonly', true) });
   }
}
function register( opts ){
   startRegistration(opts).then(cred=>{
      showMsg(gettext('Got authentication credential, verifying...'), false, cred);
      cred.username=document.querySelector('#registerFrm').querySelector('input[name=username]').value;
      if(USER){
         cred.username=USER.username;
         document.querySelector('#registerFrm').querySelector('input[name=username]').value=cred.username;
      }
      cred.displayName=document.querySelector('#registerFrm').querySelector('input[name=displayName]').value;
      axios.post(document.querySelector('#registerFrm').attributes.action, JSON.stringify(cred), {'headers':{'X-CSRFToken':Cookies.get('csrftoken'), 'Content-Type':'application/json'}}).then(rep=>{
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
}
function focus(ele){
   window.setTimeout(`document.querySelector('${ele}').select(); document.querySelector('${ele}').focus();`, 500);
}

document.addEventListener('DOMContentLoaded', evt=>{
   focus('input[name=username]');
   $(this).find('input[name=displayName]').val(DEFAULT_DEVICE_NAME).attr('value', DEFAULT_DEVICE_NAME);
   $('#registerFrm')
      .on('submit', function(evt){
         evt.preventDefault();
         if(!$(this).valid())return;
         toggleFrm(false);
         let data={};
         if($(this).find('input[name=displayName]').val()=='')
            $(this).find('input[name=displayName]').val(DEFAULT_DEVICE_NAME);
         data['username']=$(this).find('input[name=username]').val();
         data['displayName']=$(this).find('input[name=displayName]').val();
         data['authenticator']=$(this).find('input[name=authenticator]').val();
         showMsg(gettext('Getting the challenge and related information from server...'), true);
         axios.get($(this).attr('action'), {params: data, headers:{'Accept': 'application/json'}})
            .then(rep=>{
               regOpts=rep.data;
               showMsg(gettext('Got server generated Authentication Options, authenticating...'), false, regOpts);
               if(regOpts.newUserExists){
                  showMsg(interpolate(gettext('The user is already registered. Please select another one or <a href="%(loginUrl)s" target="_self">Login</a> to register the new public key'), {'loginUrl': URL_LOGIN}, true), false);
                  toggleFrm(true);
                  return;
               }
               register(regOpts);
            })
            .catch(err=>{
               toggleFrm(true);
               if(err.name==='InvalidStateError')
                  showMsg(gettext('Error: Authenticator was probably already registered by user'), false, err);
               else
                  showMsg(err, false);
            }); //Log the error when getting AuthOptions
         return false;
      })
      .on('reset', function(evt){
         $('input[name=username],input[name=displayName]').removeAttr('readonly');
         window.setTimeout("$('input[name=displayName]').val(DEFAULT_DEVICE_NAME)", 100);
      })
      .validate({autoFocus: false});
   $('#registerBtn').removeAttr('disabled');
   $('#resetBtn').on('click', function(evt){
      evt.preventDefault();
      $('#registerFrm')
         .find('input,textarea,select').removeAttr('readonly').end()
         .find('input[name=displayName]').val(DEFAULT_DEVICE_NAME).end()
         .find('input[name=username]').val('').end()
      ;
   });
   $('input[name=username]').on('keyup', function(evt){
      if(evt.keycode==13)
         focus('input[name=displayName]');
   });
   $('input[name=displayName').on('keyup', function(evt){
      if(evt.keycode==13)
         $(this).parents('form:first').submit();
   });
   $('#authenticatorSelector').find('li[value]').on('click', function(evt){
      evt.preventDefault();
      $('#authenticatorSelector')
         .find('i').remove().end()
         .find('input').val($(this).attr('value')).end()
         .parents('.input-group:first').find('button').text(interpolate(gettext('authenticator:%(authenticator)s'), {'authenticator':$(this).text()}, true))
         ;
      $(this).append($('<i></i>').addClass('fas fa-check mx-1'));
   });
});
