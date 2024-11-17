rsync -e "ssh -i ./secrets/key-pair.pem" main.py ec2-user@ec2-44-236-44-204.us-west-2.compute.amazonaws.com:/home/ec2-user/dev/backend/main.py
# ssh -i ./secrets/key-pair.pem ec2-user@ec2-44-236-44-204.us-west-2.compute.amazonaws.com
