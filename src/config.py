# by Yasuhiro Fujii <y-fujii at mimosa-pudica.net>, public domain

import os


timeOut = 30
nParallel = 16
infoFile = os.environ["HOME"] + "/.www-info-3.0"
listFile = os.environ["HOME"] + "/.www-list"
htmlFile = os.environ["HOME"] + "/.www-check.html"

maxRatio = 4
maxLine = 4
fgColor =  ( (127, 127, 127), (127, 127, 127), (  0,   0,   0) )
bgColor =  ( (243, 247, 247), (247, 245, 239), (240, 236, 224) )
uriColor = ( (135, 191, 135), (135, 191, 135), ( 16, 128,  16) )

htmlHeader = """\
<!doctype html>
<html lang="ja">
	<head>
		<meta charset="utf-8">
		<title>wwwChecker</title>
		<style type="text/css">
			* {
				font: 100%/1.6 sans-serif;
				margin:  0;
				padding: 0;
				text-decoration: none;
			}

			body {
			    margin: 1em 0;
			}

			table {
				width: 95%;
				margin: 0 auto;
				table-layout: fixed;
				border-spacing: 0.6em;
			}

			td:nth-child(1), td:nth-child(2) {
				font-family: monospace, monospace;
				white-space: nowrap;
				vertical-align: top;
				text-align: center;
			}

			td:nth-child(1) {
				width: 8.0em;
			}

			td:nth-child(2) {
				width: 8.5em;
			}

			div {
				max-height: 6.4em;
				margin:  0.3em 0.0em;
				padding: 0.3em 0.6em;
				overflow: hidden;
			}

			a:hover {
				text-decoration: underline;
			}
		</style>
	</head>
<body>
<table>
"""

htmlContent = """
<tr style="color: %(fgColor)s">
<td>%(yyyy)04d-%(mo)02d-%(dd)02d %(hh)02d:%(mi)02d</td>
<td>%(status)s</td>
<td>
<a href="%(url)s" style="color: %(uriColor)s">%(title)s</a>
<div style="background-color: %(bgColor)s">
%(summary)s
</div>
</td>
</tr>
"""

htmlFooter = """\
</table>
</body>
</html>
"""
