# by y.fujii <y-fujii at mimosa-pudica.net>, public domain

import os


timeOut = 30
nParallel = 4
infoFile = os.environ["HOME"] + "/.www-info-1.3"
listFile = os.environ["HOME"] + "/.www-list"
htmlFile = os.environ["HOME"] + "/.www-check.html"

maxRatio = 8
maxLine = 4
fgColor =  ( (127, 127, 127), (127, 127, 127), (  0,   0,   0) )
bgColor =  ( (243, 247, 247), (247, 245, 239), (240, 236, 224) )
uriColor = ( (135, 191, 135), (135, 191, 135), ( 16, 128,  16) )

htmlHeader = u"""\
<!doctype html>
<html lang="ja">
	<head>
		<meta charset="utf-8" />
		<title>wwwChecker</title>
		<style type="text/css">
			table {
				width: 95%;
				line-height: 1.5;
				margin-left: auto;
				margin-right: auto;
				table-layout: fixed;
				border-spacing: 0.5em;
			}

			td.status {
				width: 18em;
				font-family: monospace;
				vertical-align: top;
			}

			div {
				max-height: 6em;
				_height: 6em;
				margin: 0.25em 0em;
				padding: 0.25em 0.5em;
				overflow: hidden;
				border-radius: 0.5em;
				-moz-border-radius: 0.5em;
			}

			a {
				text-decoration: none;
			}

			a:hover {
				text-decoration: underline;
			}
		</style>
	</head>
	<body>

<table>
"""

htmlContent = u"""
<tr style="color: %(fgColor)s">
<td class="status">%(yyyy)04d-%(mo)02d-%(dd)02d&nbsp;%(hh)02d:%(mi)02d&nbsp;&nbsp;%(status)s</td>
<td class="text">
<a href="%(url)s" style="color: %(uriColor)s">%(title)s</a>
<div style="background-color: %(bgColor)s">
%(summary)s
</div>
</td>
</tr>
"""

htmlFooter = u"""
</table>
</body>
</html>
"""
