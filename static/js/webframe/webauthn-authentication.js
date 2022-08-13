const { startAuthentication } = SimpleWebAuthnBrowser;
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

$(document).ready(function(){
   $('#loginFrm')
      .on('submit', function(evt){
         evt.preventDefault();
         if($(this).valid()){
            showMsg(gettext('Loading authentication options from server...'));
            let data={'username': $('input[name=username]').val()};
            $('input[name=username]').attr('disabled', 'disabled');
            axios.get(authenticationUrl, {'params':data, 'headers':{'Accept': 'application/json'}})
               .then(rep=>{
                  showMsg(gettext('Got authentication options, authenticating...'), false, rep.data);
                  if(rep.data.allowCredentials.length>-1){
                     startAuthentication(rep.data).then(cred=>{
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
                     $('#field-password').removeClass('d-none').addClass('animate_animated animate__slideInDown');
                  }
               });
         }
      })
      .on('reset', function(evt){
         $('input[name=username]').removeAttr('disabled');
         $('#field-password').removeClass('animate_animated animate__slideInDown').addClass('d-none');
      })
      .validate({focusInvalid: false});
   $('input[name=username]')
      .on('keyup', function(evt){
         if(evt.charCode==13)
            $(this).parents('form:first').submit();
      })
      .focus()
      .select();
   $('#loginBtn').removeAttr('disabled');
});
