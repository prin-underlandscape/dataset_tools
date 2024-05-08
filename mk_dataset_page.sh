#/bin/bash -e

BASE_URL="https://github.com/prin-underlandscape"
L=4
TD_STYLE='style="border:1px solid black;border-collapse:collapse;padding:15px;"'
TABLE_STYLE='style="border-collapse:collapse;padding:15px;"'

mk_table () {
n=0
echo "<table $TABLE_STYLE>"
for f in $(ls ../Master | grep $1 | sort)
do
  (( $n == 0 )) && echo -n "<tr>"
  name=$(basename $f .geojson)
  url=$BASE_URL/$name
  echo -n "<td $TD_STYLE><a href='$url'>$name</a></td>"
#  echo -n $BASE_URL/$(basename $f .geojson)
  if (( $n == (( L-1)) ))
  then
    echo "</tr>"
    n=0
  else
    ((n++))
  fi
done
echo "</table>"
}


echo "<h3>Dataset Sito</h3>"
mk_table "ULS"

echo "<h3>Dataset ricognizioni Fase 1</h3>"
mk_table "Fase1"

echo "<h3>Dataset QRtag</h3>"
mk_table "QR"


