#! /bin/bash
cd ~/torrents && 7z a ./$(date "+%F").7z ./filelists.sqlite && gh release create $(date "+%F") $(pwd)/$(date "+%F").7z --generate-notes && rm ./*.7z && rm ./nohup.out
# && rm $(pwd)/*.7z && rm $(pwd)/*.7z.tmp*
# gh release list -L 1000 | grep Draft |  awk '{print $1 " \t"}' |  while read -r line; do gh release delete -y "$line"; done