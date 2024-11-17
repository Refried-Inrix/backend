curl -d '{"date": "10-21-2004", "message": "yo dog was good", "author": "u mom", "location": { "lat": 2.02, "lon": -3.3 }}' \
    --header "Content-Type:application/json" \
    http://ec2-44-236-44-204.us-west-2.compute.amazonaws.com:5000/api/v1/transcript
