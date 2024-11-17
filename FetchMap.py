import boto3
import json

# Initialize AWS Cloud Map client
client = boto3.client('servicediscovery', region_name='us-west-2',
                    aws_access_key_id='TODO',
                    aws_secret_access_key='TODO')

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
