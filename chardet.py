
encodings = [
	"utf-8",
	"euc-jp",
	"utf-8",
	"cp932",
	"iso-2022-jp",
]


def detect( text ):
	bestScore = 0
	bestEnc = None
	for enc in encodings:
		try:
			unicode( text, enc )
		except UnicodeDecodeError, err:
			if err.end > best:
				bestScore = err.end
				bestEnc = enc
		else:
			bestEnc = enc
			break

	return { "encoding": bestEnc }
