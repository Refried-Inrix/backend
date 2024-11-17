# TODO
## Backend
- [ ] ~Calculate priority of message based on content~
    - [ ] Filtering in new information
- [ ] Batching AI prompts
- [ ] Working API

## Frontend
- [ ] Get TTS on the client working 
- [ ] Commit changes to `Adding Lines` endpoint

# DONE
- [X] Give project a cool name

## Backend
- [X] Working Databases 'database-1.cluster-cr20c6qq8ktf.us-west-2.rds.amazonaws.com'
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

```json
POST: http://ec2-44-236-44-204.us-west-2.compute.amazonaws.com:5000/api/v1/summary?author=name
{
    "summaries": [STRING],
    "time": STGRIN,
    "author": STGRIN
}
```

# Database
## Transcript Table
| INDEX  | DATE        | MESSAGE       | AUTHOR      | LOCATIONX        | LOCATIONY         | 
| ------ | ----------- | ------------- | ----------- | ---------------- | ----------------- | 
| SERIAL | VARCHAR(63) | VARCHAR(2047) | VARCHAR(63) | DOUBLE PERCISION | DOUBLE PERCISION  | 
| All    | All         | All           | All         | Optional         | Optional          | 

## Parsed Table
| PRIORITY    | SUMMARY      |
| ----------- | ------------ |
| VARCHAR(31) | VARCHAR(255) |
| if PARSED   | if PARSED    |

# Lore
## Name Vote
Firewire - IIIII
firewire - I
