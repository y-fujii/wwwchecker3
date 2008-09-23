
import pprint
import urllib
import html2text

src = """\
<html>
	<body>
		<table>
			<tr>
				<td>A</td>
				<td>B</td>
			</tr>
			<tr>
				<td>C
				<td>D</td>
			</tr>
		</table>
	</body>
</html>
"""

src = """\
aaa<br/>aaa<br />aaa
"""

src = urllib.urlopen( "http://d.hatena.ne.jp/higepon/" ).read()
#src = urllib.urlopen( "http://www-ui.is.s.u-tokyo.ac.jp/~takeo/diary/diary.html" ).read()




for line in html2text.html2Text( src )[1]:
	print line.encode( "euc-jp", "ignore" )
