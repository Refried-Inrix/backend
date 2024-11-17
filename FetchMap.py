import boto3
import json

REGION = "us-west-2"
SECRETNAME = "DBAccess"
def get_secret():
    client = boto3.client("secretsmanager", region_name=REGION)

    try:
        # Fetch the secret value
        response = client.get_secret_value(SecretId=SECRETNAME)
        # Parse the secret as JSON
        secret = json.loads(response["SecretString"])
        return secret
    except Exception as e:
        print(f"Error retrieving secret {SECRETNAME}: {e}")
        return None

# Fetch the secret
user_secret = get_secret()
if user_secret:
    # Extract the secrets
    try:
        ACCESSID = user_secret["SecrAccessID"] 
        ACCESSKEY = user_secret["SecrKey"] 
        print("Successfully retrieved secrets from Secrets Manager.")
    except KeyError as e:
        print(f"Missing key in secret: {e}. Ensure the secret contains all required keys.")
        ACCESSID, ACCESSKEY = None, None
else:
    print("Failed to retrieve the secret.")
    ACCESSID, ACCESSKEY = None, None


# Initialize AWS Cloud Map client
client = boto3.client('servicediscovery', region_name='us-west-2',
                    aws_access_key_id=ACCESSID,
                    aws_secret_access_key=ACCESSKEY)

# Your namespace ID in AWS Cloud Map
namespace_id = "ns-abcpqwmu4n4hrttr"

# Fetch service locations
def get_service_locations(namespace_id):
    services_response = client.list_services(
        Filters=[{
            'Name': 'NAMESPACE_ID',
            'Values': [namespace_id],
            'Condition': 'EQ'
        }]
    )

    locations = []
    for service in services_response['Services']:
        service_id = service['Id']
        instances_response = client.list_instances(ServiceId=service_id)
        for instance in instances_response['Instances']:
            metadata = instance['Attributes']
            if 'latitude' in metadata and 'longitude' in metadata:
                locations.append({
                    'name': metadata.get('name', f"Service-{service_id}"),
                    'latitude': float(metadata['latitude']),
                    'longitude': float(metadata['longitude'])
                })
    return locations

# Fetch and save the locations
locations = get_service_locations(namespace_id)

# Save locations to a JSON file for the frontend
with open('locations.json', 'w') as json_file:
    json.dump(locations, json_file)

print("Locations saved to 'locations.json'")
