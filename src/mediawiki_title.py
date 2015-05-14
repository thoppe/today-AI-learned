# Stupid mediawiki-utilites only works with python3
# have to call this externally ...

from mw.lib.title import normalize
import sys
title = ' '.join(sys.argv[1:])
print (normalize(title))

