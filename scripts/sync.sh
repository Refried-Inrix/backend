file="$1"

rsync -e "ssh -i ./secrets/key-pair.pem" $file ec2-user@ec2-44-236-44-204.us-west-2.compute.amazonaws.com:/home/ec2-user/dev/backend/$file
