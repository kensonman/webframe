/*
**Date** 2016-04-28 17:08
**File** jquery.dropdown.js
**Version** v2.0
**Desc** The jquery plugin for dropdown widget.
**License** BSD 

#Usage
    $('selector').wf_dropdown(Options);

# Options
**item** The jquery selector to find the item. Once the item was clicked, the onclick action will be fired; Default is "a.item";

**onclick** The function to handle the item clicking; Default is jQuery.fn.wf_dropdown.onclick;

**value** The jQuery selector to find the input. Default is "input:first";

# Example
    <div class="dropdown">
        <input type="hidden" name="field-name" value="default-value"/>
        <button type="button" data-toggle="dropdown">Label</button>
        <ul class="dropdown-menu">
                <li><a href="#" class="item">Opt1</a></li>
                <li><a href="#" class="item">Opt2</a></li>
                <li><a href="#" class="item">Opt3</a></li>
                <li><a href="#" class="item">Opt4</a></li>
        </ul>
     </div>
    <script type="text/javascript"><!--
    $(document).ready(function(){
        $('div.dropdown').wf_dropdown({
                'items':'a.item',
                'onclick':jQuery.wf_dropdown.onclick,
                'value': 'input:first',
        });
    });
    //--></script>
*/

;(function($) {
	$.extend($, {wf_dropdown:{
		onclick: function( evt ){
			var element=$(this).parents('.wf_dropdown:first');
			var value=null;
			if(typeof($(this).attr('val'))=='undefined')
				value=$(this).text();
			else
				value=$(this).attr('val');
			$(element)
				.find($(element).attr('value')).val(value).end()
				.find('.wf_dropdown_lbl').text($(this).text()).end()
				.trigger('change')
			;
		},
	}});
	
	// jQuery plugin definition
	$.fn.wfdropdown = function(params) {
		// merge default and user parameters
		params = $.extend({'items':'a.item','value':'input:first','onclick':jQuery.wf_dropdown.onclick}, params);
		var text=$(this).find('button:first').html();
		
		$(this)
			.find('button').empty().append('<span class="wf_dropdown_lbl">'+text+'</span><span class="caret"></span>').end()
			.addClass('wf_dropdown')
			.attr({'value':params.value})
			.find(params.items).click(params.onclick);
		
		// allow jQuery chaining
		return this;
	};
})(jQuery);
