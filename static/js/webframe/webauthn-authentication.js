const { startAuthentication } = SimpleWebAuthnBrowser;
var authOpts=null;

function showMsg(msg, empty=true, detail=null){
   console.info(msg);
   if(detail!=null)console.debug(detail);
   if(empty)
      document.querySelector('#msgPnl').replaceChildren();
   let elem=document.createElement('li');
   elem.classList.add('animated');
   elem.classList.add('flash');
   elem.innerText=msg;
   document.querySelector('#msgPnl').appendChild(elem);
}

function loadingAuthOpts(evt, cb){
   showMsg(gettext('Loading authentication options from server...'));
   let data={'username': $('input[name=username]').val()};
   axios.get(authenticationUrl, {'params':data, 'headers':{'Accept': 'application/json'}})
      .then(rep=>{ authOpts=rep.data; return authOpts; })
      .then(cb);
}

function loginWithPubkey(evt){
   evt.preventDefault();
   $('input[name=username]').attr('readonly', 'readonly');
   showMsg(gettext('Loading authentication options from server...'));
   let data={'username': $('input[name=username]').val()};
   axios.get(authenticationUrl, {'params':data, 'headers':{'Accept': 'application/json'}}).then(rep=>{
      let data=rep.data;
      showMsg(gettext('Got authentication options, authenticating...'), false, data);
      if(data.allowCredentials.length>0){
         startAuthentication(data).then(cred=>{
            showMsg(gettext('Authenticated, verification in progress...'), false, cred);
            axios.post(authenticationUrl, JSON.stringify(cred), {'headers':{'X-CSRFToken': Cookies.get('csrftoken'), 'Content-Type':'application/json'}}).then(rep=>{
               showMsg(gettext('Got server verification result'), false, rep.data);
               let data=rep.data;
               if(data.verified){
                  showMsg(gettext('Authentication successful, the page will be redirected soon...'));
                  window.setTimeout('window.location.href=document.querySelector("input[name=next]").value', 1000);
               }else
                  showMsg(interpolate(gettext('Authentication failure: %(error)s'), {'error': data.error}, true), false, data.message);
            });
         });
      }else{
         //Required to login with Password
         $('#field-password').removeClass('d-none').addClass('animate_animated animate__slideInDown');
         focus('input[name=current-password]');
      }
   });
   return false;
}

function loginWithPassword(evt){
   $('input[name=username]').attr('readonly', 'readonly');
   $('input[name=current-password]').attr('readonly', 'readonly');
   $('#loginFrm').attr('action', loginUrl); //Chaning the login url
   $('input[name=csrfmiddlewaretoken]').val(Cookies.get('csrftoken'));
   return true;
}

function focus(ele){
   window.setTimeout(`$('${ele}').focus().select()`, 500);
}

$(document).ready(function(){
   $('#loginFrm')
      .on('submit', function(evt){
         if($(this).valid()){
            if($('#field-password').is(':visible'))
               return loginWithPassword(evt);
            else
               return loginWithPubkey(evt);
         }
      })
      .on('reset', function(evt){
         $('input[name=username]').removeAttr('readonly');
         $('#field-password').addClass('d-none').removeClass('animate_animated animate__slideInDown');
      })
      .validate({focusInvalid: false});
   $('input[name=username]')
      .on('keyup', function(evt){
         if(evt.charCode==13)
            if($('#field-password').is(':visible'))
               focus('input[name=current-password]');
            else
               $('#loginFrm').submit();
      });
   focus('input[name=username]');
   $('#loginBtn').removeAttr('disabled');
   $('#loginWithPwdBtn').on('click', function(){
      $('#field-password').removeClass('d-none').addClass('animate_animated animate__slideInDown');
      focus('input[name=current-password]');
   });
});
