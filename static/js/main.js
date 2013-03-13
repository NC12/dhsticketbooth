// If the length of the element's string is 0 then display helper message
function notEmpty(){
	var ticketNum = document.getElementById('tickets')
	if(ticketNum.value.length == 0){
		alert('Please enter a value');
		ticketNum.focus(); // set the focus to this input
		return false;
	}
	return true;
}

// if the element's string matches the regular expression it is all numbers
function isNumeric(){
	var ticketNum = document.getElementById('tickets')
	var numericExpression = /^[0-9]+$/;
	if(ticketNum.value.match(numericExpression)){
		alert('Thank you! Your order has been recorded')
		return true;
	}
	else{
		alert('Please enter a number');
		ticketNum.focus();
		return false;
	}
}

	
$(document).ready(function(){	
	// content to fade in
	$('iframe').fadeIn('slow');
});	

