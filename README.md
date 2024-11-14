# Refried
*Recording Fire Radio and Documenting*

## Building
### Backend
`TODO`

### Frontend
`TODO`

## Tech Stack
An EC2 instatance scrapes data from public radio broadcasts and filters out
dead air. 

It then forwards the useful air time to a Sage instance that converts
the audio to text and creates a list of bullet points with priority. 

That is sent to an agregator which keeps track of notes temporally and
locationally. 

This data is queried by a website where it is displayed.

## Usage
Visit PROJECT_URL (refried.gingerfocus.dev). Alternativly, query the api
directly.

## Possible Improvments
Using dedicated hardware to read radio waves instead of a software middleware.
