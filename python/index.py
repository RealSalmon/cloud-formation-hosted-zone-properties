#! /usr/bin/env python
#
# The following IAM permissions are required . . .
#
#   route53:GetHostedZone


import http.client
import json
import logging
import os
from urllib.parse import urlparse

import boto3

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get('LOGLEVEL', 'INFO').upper())

MSG_EMPTY_PROPS = 'Empty resource properties'
MSG_MISSING_PROP = 'Required resource property HostedZoneId is not set'
MSG_UNKNOWN_ERROR = 'Unable to get hosted zone properties - See CloudWatch ' \
                    'logs for the Lambda function backing this custom ' \
                    'resource for details'


def send_response(request, response, status=None, reason=None):
    """ Send our response to the pre-signed URL supplied by CloudFormation
    If no ResponseURL is found in the request, there is no place to send a
    response. This may be the case if the supplied event was for testing.
    """
    if status is not None:
        response['Status'] = status

    if reason is not None:
        response['Reason'] = reason

    logger.debug("Response body is: %s", response)

    if 'ResponseURL' in request and request['ResponseURL']:
        url = urlparse(request['ResponseURL'])
        body = json.dumps(response)
        https = http.client.HTTPSConnection(url.hostname)
        logger.debug("Sending response to %s", request['ResponseURL'])
        https.request('PUT', url.path + '?' + url.query, body)
    else:
        logger.debug("No response sent (ResponseURL was empty)")

    return response


def send_fail(request, response, reason=None):
    if reason is not None:
        logger.error(reason)
    else:
        reason = 'Unknown Error - See CloudWatch log stream of the Lambda ' \
                 'function backing this custom resource for details'

    return send_response(request, response, 'FAILED', reason)


def lambda_handler(event, context=None):

    response = {
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Status': 'SUCCESS'
    }

    # Make sure resource properties are there
    try:
        props = event['ResourceProperties']
    except KeyError:
        return send_fail(event, response, MSG_EMPTY_PROPS)

    try:
        rid = props['HostedZoneId']
    except KeyError:
        return send_fail(event, response, MSG_MISSING_PROP)

    # PhysicalResourceId is meaningless here, but CloudFormation requires it
    # returning the ID seems to make the most sense...
    response['PhysicalResourceId'] = rid

    # There is nothing to do for a delete request
    if event['RequestType'] == 'Delete':
        return send_response(event, response)

    # Lookup the hosted zone
    client = boto3.client('route53')
    try:
        zone = client.get_hosted_zone(Id=rid)
        response['Data'] = {
            'Name': zone['HostedZone']['Name']
        }
    except Exception as E:
        return send_fail(event, response, str(E))

    return send_response(event, response)
