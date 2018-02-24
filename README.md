# hosted-zone-vpc-properties

[![CircleCI](https://circleci.com/gh/RealSalmon/cloud-formation-hosted-zone-properties.svg?style=svg)](https://circleci.com/gh/RealSalmon/cloud-formation-hosted-zone-properties)

## A Lambda-backed custom resource for CloudFormation

### Purpose:

This custom resource provides information information about a Route53
Hosted Zone. If all you have is the Hosted Zone ID, this resource will provide 
you with that zone's name, which may be useful for creating Route53 resource
records in your CloudFormation templates.

### Installation
This custom resource can be installed on your AWS account by deploying the 
CloudFormation template at cloud-formation/cloud-formation.yml, and then 
updating the Lambda function it creates with the code from python/index.py

The Lambda function's ARN, which is needed for use as a service token when 
using this custom resource in your CloudFormation  templates, will be exported
as an output with the name _${AWS::StackName}-FunctionArn_.

Once installed, you can test the custom resource by using the CloudFormation
template at cloud-formation/example-cloud-formation.yml, which will create a 
stack using outputs from the custom resource.

### Syntax:

The syntax for declaring this resource:

```yaml
VpcProperties:
  Type: "AWS::CloudFormation::CustomResource"
  Version: "1.0"
  Properties:
    ServiceToken: LAMDA_FUNCTION_ARN
    HostedZoneId: HOSTED_ZONE_ID
```
### Properties

#### Service Token
##### The ARN of the Lambda function backing the custom resource

Type: String

Required: Yes

#### HostedZoneId
##### The ID of the Hosted Zone to use

Type: String

Required: Yes

### Return Values

#### Ref
When the logical ID of this resource is provided to the Ref intrinsic function, 
Ref returns a the id of the Route53 Hosted Zone.

#### Fn::GetAtt

Fn::GetAtt returns a value for a specified attribute of this type. The 
following are the available attributes.

##### Name

The name of the Route53 Hosted Zone
