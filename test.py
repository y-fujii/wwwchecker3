
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
			<script>
			assdfsfd
			<sdfsdf>Sd</fsdfsdf>Sdfsdfs
			<!-- sdfsdfs -->
			aaa
			</script>
			bbb
		</table>
	</body>
</html>
"""

#src = """\
#aaa<br/>aaa<br />aaa
#"""

#src = urllib.urlopen( "http://www-ui.is.s.u-tokyo.ac.jp/~takeo/diary/diary.html" ).read()
#src = urllib.urlopen( "http://morihyphen.infoseek.ne.jp" ).read()
src = urllib.urlopen( "http://www.number21.jp/diary/sanama/" ).read()
print src 

for line in html2text.html2Text( src )[1]:
	print line.encode( "euc-jp", "ignore" )
