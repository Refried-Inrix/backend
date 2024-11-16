# TODO
## Backend
- [ ] Calculate priority of message based on content
- [ ] Connect to Database!
    - [X] Running EC2
    - [X] Working Public API

## Frontend
- [ ] Get TTS on the client working 
    - [ ] Commit changes to `Adding Lines` endpoint

# DONE
## Backend
- [X] Set Up SQL Databases 'database-1.cluster-cr20c6qq8ktf.us-west-2.rds.amazonaws.com'
- [X] Prompting

## Frontend

# Api
## Adding Lines
```json
POST: http://ec2-44-236-44-204.us-west-2.compute.amazonaws.com:5000/api/v1/transcript
{
    "date": STRING,
    "author": STRING,
    "location": (OPTION){
        "lat": NUMBER, "lon": NUMBER // Latitude and longitude of input
    },
    "message": STRING,
}
```

# Database
## Transcript Table
| INDEX | DATE | MESSAGE | AUTHOR | LOCATIONX | LOCATIONY | PRIORITY |


