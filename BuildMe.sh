#!/bin/bash
mkdir CraigPSA
cd CraigPSA
pulumi new https://github.com/yNosGR/PSA.git
pulumi up -y
pulumi up -y
checkit=0
until [ $checkit == 5 ]; do 
  curl -fsm1  $(pulumi stack output TSAelb) && checkit=$((checkit+1)) 
  sleep 1
done
pulumi destroy -y
pulumi stack rm dev 
exit
