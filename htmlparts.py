PRE_HEADER_HTML = '''
<html>
<head>
    <link rel="stylesheet" href="../visualize_color.css">
</head>
<body onload="loadScipt()">
<div id="highlightCount"></div>
<body>
'''
ENDER_HTML = '''
<script>
	
    function loadScipt(){
		console.log("Loaded")
		const highlightList = document.querySelectorAll('.highlight')
		countHighlights(highlightList)
		insertHR(highlightList)
	}
	
    function countHighlights(highlights){
		document.getElementById('highlightCount').innerHTML = highlights.length
	}

	function insertHR(highlights){
		console.log("insertHR ran")
		console.log(highlights[0].classList[1])
		for (let i = 0; i < highlights.length; i++) {
			console.log("Loop ran")
			if (highlights[i].classList[1] == 'Blue') {
				highlights[i].insertAdjacentHTML('afterend', '<HR>')
			} else if (highlights[i].classList[1] == 'Pink' && highlights[i + 1].classList[1] == 'Yellow') {
				console.log("If passed")
				highlights[i + 1].insertAdjacentHTML('afterend', '<HR>')
			}
		}
	}

</script>
'''