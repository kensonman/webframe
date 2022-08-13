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
   elem.classList.add('animated');
   elem.classList.add('flash');
   elem.innerText=msg;
   document.querySelector('#msgPnl').appendChild(elem);
}
function toggleFrm(enabled=true){
   if(enabled)
      $('#registerFrm')
         .find('input,select,textarea').removeAttr('disabled').end()
         .find('#registerBtn').removeAttr('disabled').end()
      ;
   else
      $('#registerFrm')
         .find('input,select,textarea').attr('disabled', 'disabled').end()
         .find('#registerBtn').attr('disabled', 'disabled').end()
      ;
}
function register( opts ){
   startRegistration(opts).then(cred=>{
      cred.username=$('#registerFrm').find('input[name=username]').val();
      cred.displayName=$('#registerFrm').find('input[name=displayName]').val();
      showMsg(gettext('Got authentication credential, verifying...'), false, cred);
      axios.post($('#registerFrm').attr('action'), JSON.stringify(cred), {'headers':{'X-CSRFToken': Cookies.get('csrftoken'), 'Content-Type':'application/json'}}).then(rep=>{
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
}
$(document).ready(function(){
   $('input[name=username]').focus().select();
   $(this).find('input[name=displayName]').val(DEFAULT_DEVICE_NAME);
   $('#registerFrm').submit(function(evt){
      evt.preventDefault();
      toggleFrm(false);
      let data={};
      if($(this).find('input[name=displayName]').val()=='')
         $(this).find('input[name=displayName]').val(DEFAULT_DEVICE_NAME);
      data['username']=$(this).find('input[name=username]').val();
      data['displayName']=$(this).find('input[name=displayName]').val();
      if(regOpts==null){
         showMsg(gettext('Getting the challenge and related information from server...'), true);
         axios.get($(this).attr('action'), {params: data, headers:{'Accept': 'application/json'}})
            .then(rep=>{
               showMsg(gettext('Got server generated Authentication Options, authenticating...'));
               regOpts=rep.data;
               if(regOpts.passwordRequired){
                  $('#field-password').removeAttr('d-none');
                  toggleFrm(true);
               }else register(regOpts);
            })
            .catch(err=>{
               toggleFrm(true);
               if(err.name==='InvalidStateError')
                  showMsg(gettext('Error: Authenticator was probably already registered by user'), false, err);
               else
                  showMsg(err, false, err);
            }); //Log the error when getting AuthOptions
      }else register(regOpts);
      return false;
   });
   $('#registerBtn').removeAttr('disabled');
});
