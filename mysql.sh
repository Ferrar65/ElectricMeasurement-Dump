#!/bin/bash

if [ -t 0 ]
then

   docker exec -ti Electric-Measurement mysql -uroot -pSolenoide meter $*
else
   # La Password migliore del mondo!
   docker exec -i Electric-Measurement mysql -uroot -pSolenoide meter $*
fi
