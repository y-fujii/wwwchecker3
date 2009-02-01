# by y-fujii <fuji at mail-box.jp>, public domain

import os


timeOut = 30
nParallel = 4
infoFile = os.environ["HOME"] + "/.www-info-1.2"
listFile = os.environ["HOME"] + "/.www-list"
htmlFile = os.environ["HOME"] + "/.www-check.html"

maxRatio = 8
maxLine = 4
fgColor =  ( (127, 127, 127), (127, 127, 127), (  0,   0,   0) )
bgColor =  ( (243, 247, 247), (247, 245, 239), (240, 236, 224) )
uriColor = ( (135, 191, 135), (135, 191, 135), ( 16, 128,  16) )

htmlHeader = u"""\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja">
	<head>
		<title>wwwChecker</title>
		<style type="text/css">
			table {
				width: 95%;
				line-height: 1.5em;
				margin-left: auto;
				margin-right: auto;
				table-layout: fixed;
				border-spacing: 0.5em;
			}

			td.info {
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
<td class="info">%(yyyy)04d-%(mo)02d-%(dd)02d&nbsp;%(hh)02d:%(mi)02d&nbsp;&nbsp;%(info)s</td>
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
