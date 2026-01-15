#!/bin/bash
shopt -s nullglob
files=(/pnrgov/*/upload/*.txt)
echo ${#files[@]}

if [ ${#files[@]} -eq 0 ]
then
echo "no files to transfer"
exit 0
fi
create_filename(){
for a in ${files[@]}
do
#res=$(basename "$(dirname "$a")")
res=$(basename "$(dirname "$(dirname "$a")")")
fl_name=$(basename "$a")
mv $a  /output/"$res-"$fl_name"-`date +%F-%H-%M-%S`"
done
}

echo `create_filename`

#sed 's/ *$//' file.txt

