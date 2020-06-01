<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">

<html>

<head>

  <title>Scalable CSS Buttons Using PNG and Background Colors</title>

  <meta http-equiv="content-type" content="text/html; charset=ISO-8859-1">

  <script type="text/javascript" src="../assets/jquery-1.2.6.min.js"></script>

  <style type="text/css" media="screen">

.button, .button:visited {

	background: #222 url(overlay.png) repeat-x;

	display: inline-block; 

	padding: 5px 10px 6px; 

	color: #fff; 

	text-decoration: none;

	-moz-border-radius: 6px; 

	-webkit-border-radius: 6px;

	-moz-box-shadow: 0 1px 3px rgba(0,0,0,0.6);

	-webkit-box-shadow: 0 1px 3px rgba(0,0,0,0.6);

	text-shadow: 0 -1px 1px rgba(0,0,0,0.25);

	border-bottom: 1px solid rgba(0,0,0,0.25);

	position: relative;

	cursor: pointer

}

.button:hover							{ background-color: #111; color: #fff; }

.button:active							{ top: 1px; }

.button, .button:visited,



.blue	 { background-color: #E0E0E0;color:#000; font-size:14px; padding:16px; height:85px; cursor:auto; margin-bottom:8px; width:300px; }

.red	 { background-color: #2981e4;color:#fff; font-size:12px; width:110px; height:50px;cursor:pointer }

.buy	 { background-color: #3399CC;color:#fff; font-size:12px;width:110px; height:50px;cursor:pointer }/*3399CC*/

.green	 { background-color:#66CC33;color:#fff; font-size:12px;width:110px; height:50px;cursor:pointer }

.super.button, .super.button:visited 		{ font-size: 20px; 

											 padding: 8px 14px 9px; }

.buy.button, .buy.button:visited 			{

												padding: 6px; }

.green.button, .green.button:visited 			{

												padding: 6px; }

.red.button, .red.button:visited			{ background-color: #e62727; }

.red.button:hover							{ background-color: #cf2525; }



#container{

	-moz-border-radius: 6px; 

	-webkit-border-radius: 6px;

	-moz-box-shadow: 0 1px 3px rgba(0,0,0,0.6);

	-webkit-box-shadow: 0 1px 3px rgba(0,0,0,0.6);

	padding:10px 20px 20px 20px;

	text-align:justify;

	font-size:14px;

	font-family:Arial, Helvetica, sans-serif;

	text-shadow: 0 -1px 1px rgba(0,0,0,0.25);

	height:400px; float:left; width:600px;

}

#container label{

	font-size:24px;

	color:#336699;

	font-weight:bolder;

}

  </style>

  <script type="text/javascript">

	// <![CDATA[	

	$(document).ready(function(){	

		$('.super').click(function(){

			$('#container').fadeOut();

			var a = $(this).attr('id');

			$.post("ajax_page.php?id="+a, {

			}, function(response){

				//$('#container').html(unescape(response));

				///$('#container').fadeIn();

				setTimeout("finishAjax('container', '"+escape(response)+"')", 400);

			});

		});	

	});	

	function finishAjax(id, response){

	  $('#'+id).html(unescape(response));

	  $('#'+id).fadeIn();

	} 

	// ]]>

</script>



</head>

<body>

<div style="float:left">

	<input type="button" name="test" class="super red button" id="1" value="Home" />

	<br />

	<input type="button" name="test" class="super buy button" id="2" value="About" />

	<br />

	<input type="button" name="test" class="super green button" id="3" value="Services" />

</div>

<div id="container">

  <label>Hai</label>

	  <br/>

	  <p>

	 <img src="99.jpg" alt="" style="float:left; margin-right:10px;" />

	 

	  </p>

</div>

</body>

</html>

