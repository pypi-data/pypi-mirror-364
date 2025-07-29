from collections.abc import Mapping

from pypanther import LogType, Rule, RuleTest, Severity, panther_managed
from pypanther.helpers.aws import aws_cloudtrail_success, aws_rule_context
from pypanther.helpers.base import deep_get


@panther_managed
class AWSCloudTrailSnapshotMadePublic(Rule):
    id = "AWS.CloudTrail.SnapshotMadePublic-prototype"
    display_name = "AWS Snapshot Made Public"
    log_types = [LogType.AWS_CLOUDTRAIL]
    default_severity = Severity.MEDIUM
    reports = {"MITRE ATT&CK": ["TA0010:T1537"]}
    default_description = "An AWS storage snapshot was made public."
    default_reference = "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-modifying-snapshot-permissions.html"
    default_runbook = "Adjust the snapshot configuration so that it is no longer public."
    summary_attributes = ["userAgent", "sourceIpAddress", "recipientAccountId", "p_any_aws_arns"]
    tags = ["AWS", "Exfiltration:Transfer Data to Cloud Account"]
    IS_SINGLE_USER_SHARE = False  # Used to adjust severity

    def rule(self, event):
        if not aws_cloudtrail_success(event):
            return False
        # EC2 Volume snapshot made public
        if event.get("eventName") == "ModifySnapshotAttribute":
            parameters = event.get("requestParameters", {})
            if parameters.get("attributeType") != "CREATE_VOLUME_PERMISSION":
                return False
            items = deep_get(parameters, "createVolumePermission", "add", "items", default=[])
            for item in items:
                if not isinstance(item, (Mapping, dict)):
                    continue
                if item.get("userId") or item.get("group") == "all":
                    self.IS_SINGLE_USER_SHARE = "userId" in item  # Used for dynamic severity
                    return True
            return False
        return False

    def severity(self, _):
        # Set severity to INFO if only shared with a single user
        if self.IS_SINGLE_USER_SHARE:
            return "INFO"
        return "DEFAULT"

    def alert_context(self, event):
        return aws_rule_context(event)

    tests = [
        RuleTest(
            name="Snapshot Made Publicly Accessible",
            expected_result=True,
            log={
                "awsRegion": "us-west-2",
                "eventID": "1111",
                "eventName": "ModifySnapshotAttribute",
                "eventSource": "ec2.amazonaws.com",
                "eventTime": "2019-01-01T00:00:00Z",
                "eventType": "AwsApiCall",
                "eventVersion": "1.05",
                "recipientAccountId": "123456789012",
                "requestID": "1111",
                "requestParameters": {
                    "attributeType": "CREATE_VOLUME_PERMISSION",
                    "createVolumePermission": {"add": {"items": [{"group": "all"}]}},
                    "snapshotId": "snap-1111",
                },
                "responseElements": {"_return": True, "requestId": "1111"},
                "sourceIPAddress": "111.111.111.111",
                "userAgent": "Mozilla/2.0 (compatible; NEWT ActiveX; Win32)",
                "userIdentity": {
                    "accessKeyId": "1111",
                    "accountId": "123456789012",
                    "arn": "arn:aws:sts::123456789012:assumed-role/example-role/example-user",
                    "principalId": "1111",
                    "sessionContext": {
                        "attributes": {"creationDate": "2019-01-01T00:00:00Z", "mfaAuthenticated": "true"},
                        "sessionIssuer": {
                            "accountId": "123456789012",
                            "arn": "arn:aws:iam::123456789012:role/example-role",
                            "principalId": "1111",
                            "type": "Role",
                            "userName": "example-role",
                        },
                        "webIdFederationData": {},
                    },
                    "type": "AssumedRole",
                },
            },
        ),
        RuleTest(
            name="Snapshot Not Made Publicly Accessible",
            expected_result=False,
            log={
                "awsRegion": "us-west-2",
                "eventID": "1111",
                "eventName": "ModifySnapshotAttribute",
                "eventSource": "ec2.amazonaws.com",
                "eventTime": "2019-01-01T00:00:00Z",
                "eventType": "AwsApiCall",
                "eventVersion": "1.05",
                "recipientAccountId": "123456789012",
                "requestID": "1111",
                "requestParameters": {
                    "attributeType": "CREATE_VOLUME_PERMISSION",
                    "createVolumePermission": {"add": {"items": [{"group": "none"}]}},
                    "snapshotId": "snap-1111",
                },
                "responseElements": {"_return": True, "requestId": "1111"},
                "sourceIPAddress": "111.111.111.111",
                "userAgent": "Mozilla/2.0 (compatible; NEWT ActiveX; Win32)",
                "userIdentity": {
                    "accessKeyId": "1111",
                    "accountId": "123456789012",
                    "arn": "arn:aws:sts::123456789012:assumed-role/example-role/example-user",
                    "principalId": "1111",
                    "sessionContext": {
                        "attributes": {"creationDate": "2019-01-01T00:00:00Z", "mfaAuthenticated": "true"},
                        "sessionIssuer": {
                            "accountId": "123456789012",
                            "arn": "arn:aws:iam::123456789012:role/example-role",
                            "principalId": "1111",
                            "type": "Role",
                            "userName": "example-role",
                        },
                        "webIdFederationData": {},
                    },
                    "type": "AssumedRole",
                },
            },
        ),
        RuleTest(
            name="Error Making Snapshot Publicly Accessible",
            expected_result=False,
            log={
                "awsRegion": "us-west-2",
                "errorCode": "ValidationError",
                "eventID": "1111",
                "eventName": "ModifySnapshotAttribute",
                "eventSource": "ec2.amazonaws.com",
                "eventTime": "2019-01-01T00:00:00Z",
                "eventType": "AwsApiCall",
                "eventVersion": "1.05",
                "recipientAccountId": "123456789012",
                "requestID": "1111",
                "requestParameters": {
                    "attributeType": "CREATE_VOLUME_PERMISSION",
                    "createVolumePermission": {"add": {"items": [{"group": "all"}]}},
                    "snapshotId": "snap-1111",
                },
                "responseElements": {"_return": True, "requestId": "1111"},
                "sourceIPAddress": "111.111.111.111",
                "userAgent": "Mozilla/2.0 (compatible; NEWT ActiveX; Win32)",
                "userIdentity": {
                    "accessKeyId": "1111",
                    "accountId": "123456789012",
                    "arn": "arn:aws:sts::123456789012:assumed-role/example-role/example-user",
                    "principalId": "1111",
                    "sessionContext": {
                        "attributes": {"creationDate": "2019-01-01T00:00:00Z", "mfaAuthenticated": "true"},
                        "sessionIssuer": {
                            "accountId": "123456789012",
                            "arn": "arn:aws:iam::123456789012:role/example-role",
                            "principalId": "1111",
                            "type": "Role",
                            "userName": "example-role",
                        },
                        "webIdFederationData": {},
                    },
                    "type": "AssumedRole",
                },
            },
        ),
        RuleTest(
            name="Snapshot Mader Available to Single Person",
            expected_result=True,
            log={
                "awsRegion": "us-west-2",
                "eventID": "1111",
                "eventName": "ModifySnapshotAttribute",
                "eventSource": "ec2.amazonaws.com",
                "eventTime": "2019-01-01T00:00:00Z",
                "eventType": "AwsApiCall",
                "eventVersion": "1.05",
                "recipientAccountId": "123456789012",
                "requestID": "1111",
                "requestParameters": {
                    "attributeType": "CREATE_VOLUME_PERMISSION",
                    "createVolumePermission": {"add": {"items": [{"userId": "111122223333"}]}},
                    "snapshotId": "snap-1111",
                },
                "responseElements": {"_return": True, "requestId": "1111"},
                "sourceIPAddress": "111.111.111.111",
                "userAgent": "Mozilla/2.0 (compatible; NEWT ActiveX; Win32)",
                "userIdentity": {
                    "accessKeyId": "1111",
                    "accountId": "123456789012",
                    "arn": "arn:aws:sts::123456789012:assumed-role/example-role/example-user",
                    "principalId": "1111",
                    "sessionContext": {
                        "attributes": {"creationDate": "2019-01-01T00:00:00Z", "mfaAuthenticated": "true"},
                        "sessionIssuer": {
                            "accountId": "123456789012",
                            "arn": "arn:aws:iam::123456789012:role/example-role",
                            "principalId": "1111",
                            "type": "Role",
                            "userName": "example-role",
                        },
                        "webIdFederationData": {},
                    },
                    "type": "AssumedRole",
                },
            },
        ),
    ]
