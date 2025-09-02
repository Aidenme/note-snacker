HEADER_TEXT = '''
<html>
<head>
    <link rel="stylesheet" href="../visualize_color.css">
</head>
<body onload="loadScipt()">
<div id="highlightCount"></div>
<body>
'''
ENDER_TEXT = '''
<script>	
	
    function loadScipt(){
		countHighlights()
	}
	
    function countHighlights(){
		highlightCount = document.querySelectorAll('.highlight').length;
		document.getElementById('highlightCount').innerHTML = highlightCount
	}

</script>
'''