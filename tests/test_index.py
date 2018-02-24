import boto3
from moto import mock_route53
from index import lambda_handler
from index import MSG_EMPTY_PROPS, MSG_MISSING_PROP


def create_zone(hosted_zone_name):

    client = boto3.client('route53')
    z = client.create_hosted_zone(
        Name=hosted_zone_name,
        CallerReference='uafidjaklfeor'
    )

    return z['HostedZone']['Id']


def get_event():
    return {
        "StackId": "12345",
        "RequestId": "ohai!",
        "LogicalResourceId": "best-logical-resource-evar",
        "RequestType": "Create",
        "ResourceProperties": {"HostedZoneId": "changeme"}
    }


def test_empty_params():
    event = get_event()
    del event['ResourceProperties']
    response = lambda_handler(event)
    assert 'Status' in response
    assert response['Status'] == 'FAILED'
    assert response['StackId'] == event['StackId']
    assert response['LogicalResourceId'] == event['LogicalResourceId']
    assert response['RequestId'] == event['RequestId']
    assert response['Reason'] == MSG_EMPTY_PROPS


def test_missing_params():
    event = get_event()
    event['ResourceProperties'] = {'SomeGarbage': 'DoNotWant'}
    response = lambda_handler(event)
    assert 'Status' in response
    assert response['Status'] == 'FAILED'
    assert response['StackId'] == event['StackId']
    assert response['LogicalResourceId'] == event['LogicalResourceId']
    assert response['RequestId'] == event['RequestId']
    assert response['Reason'] == MSG_MISSING_PROP


def test_delete():
    event = get_event()
    event['RequestType'] = 'Delete'
    response = lambda_handler(event)
    assert response['Status'] == 'SUCCESS'
    assert response['StackId'] == event['StackId']
    assert response['LogicalResourceId'] == event['LogicalResourceId']
    assert response['RequestId'] == event['RequestId']


@mock_route53
def test_no_such_hosted_zone():
    event = get_event()
    response = lambda_handler(event)
    assert 'Status' in response
    assert response['Status'] == 'FAILED'
    assert response['StackId'] == event['StackId']
    assert response['LogicalResourceId'] == event['LogicalResourceId']
    assert response['RequestId'] == event['RequestId']
    assert response['Reason'].startswith('An error occurred (')

@mock_route53
def test_success_basic():

    hosted_zone_name = 'bestzoneevar.com.'
    hosted_zone_id = create_zone(hosted_zone_name)
    event = get_event()
    event['ResourceProperties']['HostedZoneId'] = hosted_zone_id
    response = lambda_handler(event)
    assert response['Status'] == 'SUCCESS'
    assert response['StackId'] == event['StackId']
    assert response['LogicalResourceId'] == event['LogicalResourceId']
    assert response['PhysicalResourceId'] == hosted_zone_id
    assert response['RequestId'] == event['RequestId']

    data = response['Data']
    assert data['Name'] == hosted_zone_name
