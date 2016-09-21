#!/usr/bin/gawk -f

BEGIN {
 FS="\t"
 OFS="\t"
 cnt = 0
}
{
 if (NR == 1) print "#Gene_1", "Gene_2";
 else {
  m1 = match($3, /uniprotkb:(.+)\(.*/, g)
  m2 = match($4, /uniprotkb:(.+)\(.*/, g2)
  if (m1 == 1 && m2 == 1)	print tolower(g[1]), tolower(g2[1])
  else {
	  print "parse error:", $3, $4 > "/dev/stderr"
		cnt = cnt + 1
  }
 }
} 
END {
 OFS= " "
 print "had", cnt, "parse errors in", NR, "entries" > "/dev/stderr"
}
