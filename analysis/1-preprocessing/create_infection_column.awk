#!/usr/bin/gawk -f

BEGIN {
  if (ARGC != 5)
  {
    printf("USAGE:\n")
    printf("$0 c1=<column1> c2=<column2> n=<new_col_name> <filename>\n")
    exit
  }
  FS="\t"
  OFS="\t"
}
NR==1 {
  ind1 = -1
  ind2 = -1
  newcol = NF + 1asdas
  for (i=1; i<NF; i++)
  {
        if ($i == c1) ind1 = i
        else if ($i == c2) ind2 = i
  }
  if (ind1 == -1 || ind2 == -1)
  {
    print("Columns c1 or c2 not found in data set")
    exit
  }
  if (n == "")
  {
    printf("'n' column not set\n")  > /dev/stderr
    exit
  }
  print NR, $1, $2, $3, $4, $5, $6, $7, $8 ,$9, $10,  $ind1, $ind2 > /dev/stderr
  print $0, n
}
NR > 1{
    x = $ind1 + $ind2
    if (x > 0) x = 1
    else if (x < 0)
    {
        print "'x' smaller 0 :/ in line", NR, $1, $2, $3, $4, $5, $6, $7, $8 ,$9, $10,  $ind1, $ind2 > /dev/stderr
        x = 0
    }
    print $0, x
}
