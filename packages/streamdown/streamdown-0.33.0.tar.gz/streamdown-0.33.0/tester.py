#!/usr/bin/env python3
import re
m=r"(.?)(~~|\*\*_|_\*\*|\*{1,3}|_{1,3}|`+)(.?)|(.)"
print(m)

# we intentionally return closer false positives because
# openers can consume some closing indicators. We are ok 
# with being trigger happy on closers
def has_closer(mlist, token):
    for a in mlist:
        a = [b.strip() for b in a]
        if a[1] == token and not a[2] and not a[3]:
            return True
    return False

for word in [" _hello_", "_a_", "_a", "_a_ "]: 
    p = re.findall(m, word)
    c = []
    print("")
    print(p)
    for j in p:
        a = [x.strip() for x in j]
        if not a[0] and a[1] and a[2]:
            if has_closer(p, a[1]):
                print(f"token for {a[1]}", word, a)
        c += list(filter(lambda x: x, j))

    if ''.join(c) != word:
       print("(" + ''.join(c) + ")", " is not ",  f"({word})")
