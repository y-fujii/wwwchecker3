
import pprint
import urllib
import htmlTools

src = """\
<html>
	<body>
		<table>
			<tr>
				<td>A</td>
				<td>B</td>
			</tr>
			<tr>
				<td>C</td>
				<td>D</td>
			</tr>
		</table>
	</body>
</html>
"""

src = urllib.urlopen( "http://d.hatena.ne.jp/KZR/" ).read()

for line in htmlTools.getContent( src )[0]:
	print line.encode( "euc-jp", "ignore" )
