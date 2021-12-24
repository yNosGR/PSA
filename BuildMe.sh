#!/bin/bash

test -d CraigTSA && exit

mkdir CraigTSA
cd CraigTSA

pulumi new https://github.com/yNosGR/TSA.git
pulumi up -y
pulumi up -y

# wait for everything to come up
echo "Waiting for the ELB/ASG stack to come up"
checkit=0
i=1
sp="/-\|"
until [ $checkit == 5 ]; do
  output=$(curl -fsm1 $(pulumi stack output TSAelb))
  sleep 1
  if [ -z "$output" ] ; then 
    printf "\b${sp:i++%${#sp}:1}"
  else
    test -z "$isItTheFirstTime" && printf "\b"
    echo $output
    isItTheFirstTime=NotAnyMore
    checkit=$((checkit+1))
  fi
done

printf "\n\n\n"

# Check to see if we want to delete this or not, assume no if no answer in 30 seconds
read -t 10 -p "Do you want to destroy the env? Y/n : " yn

# assume if they let it time out that they want to delete it
yn=${yn:-y}

# normalize the input to lowercase, just in case they capitalized it
yn=$(echo ${yn:0:1} | tr [:upper:] [:lower:])  

if [ $yn == y ] ; then
  pulumi destroy -y
  pulumi stack rm dev -y
fi

# Fin
exit
