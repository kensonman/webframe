/**
 * Date: 2022-09-20 11:06
 * Author:     Kenson Man <kenson.idv.hk@gmail.com>
 * File:       webframe/static/webframe/js/login.js
 * Desc:       Provide the related features for login
 */
const { startAuthentication } = SimpleWebAuthnBrowser;
const showMsg=(msg, empty=false, details=null)=>{ document.querySelector('#msgPnl').dispatchEvent(new CustomEvent('msg', {detail:{msg:msg, empty:empty, details:details}})) }
const loginFrm=document.querySelector('#loginFrm');
const focus=query=>{ document.querySelectorAll(query).forEach(em=>{ em.focus(); em.select(); }); }

document.addEventListener('DOMContentLoaded', evt=>{
   document.querySelector('.card-footer').appendChild(document.querySelector('#pnl_footer'));
   focus('input[name=username]');
   loginFrm.querySelector('#loginBtn').removeAttribute('disabled');
   document.querySelector('#msgPnlHere').appendChild(document.querySelector('#msgPnl'));
});

loginFrm.addEventListener('submit', evt=>{
   evt.preventDefault();
   let valid=new Pristine(loginFrm).validate();
   console.debug('login form validation: '+(valid?'valid':'invalid'));
   if(!valid)return; //Return false immendate when invalid
   evt.target.dispatchEvent(new CustomEvent('toggle', {value: false}));
   let pwdVisible=document.querySelector('#field-password');//checking is visible,according to [here](https://makandracards.com/makandra/1339-check-whether-an-element-is-visible-or-hidden-with-javascript)
   pwdVisible=(pwdVisible.offsetWidth > 0 && pwdVisible.offsetHeight > 0)?'loginWithPassword':'loginWithPubkey';
   loginFrm.dispatchEvent(new Event(pwdVisible));
});

loginFrm.addEventListener('loginWithPassword', evt=>{
   evt.preventDefault();
   console.debug('loginWithPassword');
   document.querySelector('input[name=username]').setAttribute('readonly', 'readonly');
   document.querySelector('input[name=current-password]').setAttribute('readonly', 'readonly');
   document.querySelector('input[name=csrfmiddlewaretoken]').value=Cookies.get('csrftoken');
   axios.post(Webframe.URL_AUTHENTICATION, new FormData(loginFrm), {'headers':{'X-CSRFToken':Cookies.get('csrftoken'), 'Content-Type':'application/json'}})
      .then(rep=>{
         showMsg(gettext('Authentication successful, the page will be redirected soon...'));
         window.setTimeout(`window.location.href='${rep.data.next}'`, 1000);
         //window.setTimeout('window.location.href=document.querySelector("input[name=next]").value', 1000);
      })
      .catch(err=>{
         if(err.response){
            let data=err.response.data;
            data=interpolate(gettext('Authentication failure: %(error)s'), {error:data.message}, true);
            showMsg(data, true);
            let fld=loginFrm.querySelector('input[name=current-password]');
            fld.removeAttribute('readonly');
            fld.select();
            fld.focus();
         }else console.error(err);
      });
});

loginFrm.addEventListener('loginWithPubkey', evt=>{
   evt.preventDefault();
   document.querySelector('input[name=username]').setAttribute('readonly', 'readonly');
   showMsg(gettext('Loading authentication options from server...'), true);
   let data={'username': loginFrm.querySelector('input[name=username]').value};
   axios.get(Webframe.URL_AUTHENTICATION, {'params':data, 'headers':{'Accept': 'application/json'}})
      .then(rep=>{
         let data=rep.data;
         showMsg(gettext('Got authentication options, authenticating...'), false, data);
         if(data.allowCredentials.length>0){
            startAuthentication(data).then(cred=>{
               showMsg(gettext('Authenticated, verification in progress...'), false, cred);
               axios.post(Webframe.URL_AUTHENTICATION, JSON.stringify(cred), {'headers':{'X-CSRFToken': Cookies.get('csrftoken'), 'Content-Type':'application/json'}}).then(rep=>{
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
            loginFrm.qureySelector('input[name=authenticating]').value='password';
            let pwdFld=loginFrm.querySelector('#field-password');
            pwdFld.classList.remove('d-none');
            pwdFld=loginFrm.querySelector('input[name=current-password]');
            pwdFld.classList.add('animate__animated', 'animate__slideInDown');
            pwdFld.removeAttribute('readonly');
            pwdFld.dispatchEvent(new Event('required'));
            focus('input[name=current-password]');
         }
      })
      .catch(err=>{
         if(err.response){
            let data=err.response.data;
            data=data.split('\n');
            data=`${err.response.status}: ${data[0]}\n<br/>${data[1]}`;
            console.info(data);
            showMsg(data, true);
            let fld=loginFrm.querySelector('input[name=username]');
            fld.removeAttribute('readonly');
            fld.select();
            fld.focus();
         }else console.error(err);
      });
});

loginFrm.addEventListener('reset', evt=>{
   document.querySelector('input[name=username]').removeAttribute('readonly');
   document.querySelector('#field-password').classList.add('d-none');
   document.querySelector('#field-password').remove('animate__animated', 'animate__slideInDown');
   loginFrm.qureySelector('input[name=authenticating]').value='pubkey';
   showMsg(null, true);
});


document.querySelector('#msgPnl').addEventListener('msg', evt=>{
   if(evt.detail.empty)evt.target.replaceChildren();
   if(!evt.detail.msg)return;
   console.info(evt.detail.msg);
   if(evt.detail.details)console.debug(evt.detail.details);
   let msg=document.createElement('li');
   msg.classList.add('animate__animated', 'animate__flash');
   msg.innerHTML+=`<span>${evt.detail.msg}</span>`;
   evt.target.appendChild(msg);
});

loginFrm.querySelector('#loginWithPwdBtn').addEventListener('click', evt=>{
   document.querySelector('#field-password').classList.remove('d-none');
   document.querySelector('#field-password').classList.add('animate__animated', 'animate__slideInDown');
   document.querySelector('#platformBtn').hidden=true;
   focus('input[name=current-password]');
});
