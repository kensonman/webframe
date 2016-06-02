var dropdownHandler=function( evt ){
	var val=$(this).attr('value');
	var title=$(this).html();
	$(this).parents('.btn-group:first,.dropdown:first')
		.find('input[type=hidden]').val(val).end()
		.find('button').empty().html(title+' <span class="caret"></span>').end()
	;
	return true;
};
