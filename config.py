
import os


nParallel = 8
infoFile = os.environ["HOME"] + "/.www-info-1.1"
listFile = os.environ["HOME"] + "/.www-list"
htmlFile = os.environ["HOME"] + "/web/www-check.html"
browser = 'firefox -remote "openURL(file://%s, new-tab)"' % htmlFile

fgColor = (0, 0, 0)
bgColor = (240, 236, 224)
uriColor = (16, 128, 16)

htmlHeader = u"""\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="ja">
	<head>
		<meta http-equiv="content-type" content="application/xhtml+xml; charset=utf-8" />
		<title>www-checker</title>
		<style type="text/css">
			table {
				margin-left: auto;
				margin-right: auto;
				border-spacing: 0.5em;
			}

			td {
				vertical-align: top;
				white-space: nowrap;
			}

			p {
				margin: 0;
			}

			div {
				width: 40em;
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
<td>%(yyyy)04d-%(mo)02d-%(dd)02d %(hh)02d:%(mi)02d</td>
<td>%(info)s</td>
<td>
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