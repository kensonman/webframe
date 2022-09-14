/*
 * Date:   2022-09-12 15:01
 * Author: Kenson Man <kenson.idv.hk@gmail.com>
 * Version: v2.0
 * File:    webframe/static/webframe/js/fileupload.js
 * Desc:    Create the file-upload component(s)
 *
*/


document.addEventListener('DOMContentLoaded', evt=>{
   Webframe().fileupload(document.querySelectorAll('input[type=file]'));
});
