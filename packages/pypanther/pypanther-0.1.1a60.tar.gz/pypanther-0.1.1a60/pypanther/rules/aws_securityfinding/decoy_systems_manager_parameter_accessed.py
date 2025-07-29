from pypanther import LogType, Rule, RuleTest, Severity, panther_managed


@panther_managed
class DecoySystemsManagerParameterAccessed(Rule):
    id = "Decoy.Systems.Manager.Parameter.Accessed-prototype"
    display_name = "Decoy Systems Manager Parameter Accessed"
    enabled = False
    log_types = [LogType.AWS_SECURITY_FINDING_FORMAT]
    default_severity = Severity.HIGH
    default_description = "Actor accessed Decoy Systems Manager parameter"
    default_reference = "https://aws.amazon.com/blogs/security/how-to-detect-suspicious-activity-in-your-aws-account-by-using-private-decoy-resources/"
    inline_filters = [{"All": []}]

    def rule(self, event):
        # List of suspicious API events
        # NOTE: There may be more API events that's not listed
        suspicious_api_events = ["Decrypt"]
        # Return True if the API value is in the list of suspicious API events
        if event["GeneratorId"] == "ssm.amazonaws.com":
            # Extract the API value from the event
            api_value = event["Action"]["AwsApiCallAction"]["Api"]
            return api_value in suspicious_api_events
        return False

    def title(self, event):
        # (Optional) Return a string which will be shown as the alert title.
        # If no 'dedup' function is defined, the return value of this method will act as dedup string.
        # NOTE: Not sure if the offending actor Id will always be in the 0th index of Resources
        # It's possible to just return the Title as a whole string
        secret = event["Resources"][0]["Id"]
        return f"Suspicious activity detected accessing     private decoy Systems Manager parameter {secret}"

    tests = [
        RuleTest(
            name="Systems-Manager-Parameter-Decoy-Accessed",
            expected_result=True,
            log={
                "Action": {
                    "ActionType": "AWS_API_CALL",
                    "AwsApiCallAction": {
                        "Api": "Decrypt",
                        "CallerType": "remoteIp",
                        "DomainDetails": {},
                        "ServiceName": "kms.amazonaws.com",
                    },
                    "DnsRequestAction": {},
                    "NetworkConnectionAction": {"LocalPortDetails": {}, "RemotePortDetails": {}},
                    "PortProbeAction": {},
                },
                "AwsAccountId": "123456789012",
                "CompanyName": "Custom",
                "CreatedAt": "2024-05-24 22:34:07.000000000",
                "Description": "Private decoy Systems Manager parameter arn:aws:ssm:us-east-1:123456789012:parameter/info-parameter was accessed by arn:aws:iam::123456789012:user/tester. This Systems Manager parameter has been provisioned to monitor and generate security events when accessed and can be an indicator of unintended or unauthorized access to your AWS Account.",
                "FindingProviderFields": {
                    "Severity": {"Label": "HIGH", "Normalized": 70},
                    "Types": ["Unusual Behaviors"],
                },
                "GeneratorId": "ssm.amazonaws.com",
                "Id": "6abc0de0-69ea-4e15-91c6-27eb4a07bd21",
                "ProcessedAt": "2024-05-24T22:34:15.644Z",
                "ProductArn": "arn:aws:securityhub:us-east-1:123456789012:product/123456789012/default",
                "ProductFields": {
                    "Custom/DecoyDetector/apiResult": "SUCCESS",
                    "Custom/DecoyDetector/requestID": "ab8cd646-1986-4c45-8546-fdb1776e23b0",
                    "Custom/DecoyDetector/userAgent": "AWS Internal",
                    "aws/securityhub/CompanyName": "Personal",
                    "aws/securityhub/FindingId": "arn:aws:service:region:123456789012:resource/12345ab6-436d-4d59-ac58-ed6b3127e440",
                    "aws/securityhub/ProductName": "Default",
                },
                "ProductName": "DecoyDetector",
                "RecordState": "ACTIVE",
                "Region": "us-east-1",
                "Resources": [
                    {
                        "Id": "arn:aws:ssm:us-east-1:123456789012:parameter/info-parameter",
                        "Partition": "aws",
                        "Region": "us-east-1",
                        "ResourceRole": "Target",
                        "Type": "Other",
                    },
                    {
                        "Id": "arn:aws:kms:us-east-1:123456789012:key/007ab31c-bf66-2264-a916-49f6d2ebd1db",
                        "Partition": "aws",
                        "Region": "us-east-1",
                        "ResourceRole": "Target",
                        "Type": "AwsKmsKey",
                    },
                    {
                        "Details": {
                            "AwsIamAccessKey": {
                                "AccessKeyId": "ABC9ONWNS3155VIEJC8U",
                                "AccountId": "123456789012",
                                "PrincipalId": "ABCDEFG0TOGJSGNQKI0:john.doe",
                                "PrincipalType": "AssumedRole",
                                "SessionContext": {
                                    "Attributes": {"CreationDate": "2024-05-24T22:32:38Z", "MfaAuthenticated": False},
                                    "SessionIssuer": {
                                        "AccountId": "123456789012",
                                        "Arn": "arn:aws:iam::123456789012:user/tester",
                                        "PrincipalId": "ABCDEFG0TOGJSGNQKI0",
                                        "Type": "Role",
                                        "UserName": "user_ab21cde50f",
                                    },
                                },
                            },
                        },
                        "Id": "ABC9ONWNS3155VIEJC8U",
                        "Partition": "aws",
                        "Region": "us-east-1",
                        "ResourceRole": "Actor",
                        "Type": "AwsIamAccessKey",
                    },
                    {
                        "Id": "arn:aws:iam::123456789012:user/tester",
                        "Partition": "aws",
                        "Region": "us-east-1",
                        "ResourceRole": "Actor",
                        "Type": "AwsIamRole",
                    },
                ],
                "SchemaVersion": "2018-10-08",
                "Severity": {"Label": "HIGH", "Normalized": 70},
                "Title": "Suspicious activity detected accessing private decoy Systems Manager parameter arn:aws:ssm:us-east-1:123456789012:parameter/info-parameter",
                "Types": ["Unusual Behaviors"],
                "UpdatedAt": "2024-05-24 22:34:07.000000000",
                "Workflow": {"Status": "NEW"},
                "WorkflowState": "NEW",
                "p_any_actor_ids": [],
                "p_any_aws_account_ids": [],
                "p_any_aws_arns": [],
                "p_any_trace_ids": [],
                "p_any_usernames": [],
                "p_event_time": "2024-05-24 22:34:07.000000000",
                "p_log_type": "AWS.SecurityFindingFormat",
                "p_parse_time": "2024-05-24 22:35:04.272574202",
                "p_row_id": "zjj8nmnw9f90uulxfa3bmen8rv5stlcx",
                "p_schema_version": 0,
                "p_source_id": "bb4e16c5-43dd-450c-9227-39f0d152659c",
                "p_source_label": "AWS Security Hub",
            },
        ),
        RuleTest(
            name="Systems-Manager-Parameter-Decoy-Not-Accessed",
            expected_result=False,
            log={
                "Action": {
                    "ActionType": "AWS_API_CALL",
                    "AwsApiCallAction": {
                        "Api": "DescribeParameters",
                        "CallerType": "remoteIp",
                        "DomainDetails": {},
                        "ServiceName": "kms.amazonaws.com",
                    },
                    "DnsRequestAction": {},
                    "NetworkConnectionAction": {"LocalPortDetails": {}, "RemotePortDetails": {}},
                    "PortProbeAction": {},
                },
                "AwsAccountId": "123456789012",
                "CompanyName": "Custom",
                "CreatedAt": "2024-05-24 22:34:07.000000000",
                "Description": "Private decoy Systems Manager parameter arn:aws:ssm:us-east-1:123456789012:parameter/info-parameter was not accessed by arn:aws:iam::123456789012:user/tester. This Systems Manager parameter has been provisioned to monitor and generate security events when accessed and can be an indicator of unintended or unauthorized access to your AWS Account.",
                "FindingProviderFields": {
                    "Severity": {"Label": "HIGH", "Normalized": 70},
                    "Types": ["Unusual Behaviors"],
                },
                "GeneratorId": "ssm.amazonaws.com",
                "Id": "6abc0de0-69ea-4e15-91c6-27eb4a07bd21",
                "ProcessedAt": "2024-05-24T22:34:15.644Z",
                "ProductArn": "arn:aws:securityhub:us-east-1:123456789012:product/123456789012/default",
                "ProductFields": {
                    "Custom/DecoyDetector/apiResult": "SUCCESS",
                    "Custom/DecoyDetector/requestID": "ab1cd234-1986-4c45-8546-fdb1776e23b0",
                    "Custom/DecoyDetector/userAgent": "AWS Internal",
                    "aws/securityhub/CompanyName": "Personal",
                    "aws/securityhub/FindingId": "arn:aws:service:region:123456789012:resource/12345ab6-436d-4d59-ac58-ed6b3127e440",
                    "aws/securityhub/ProductName": "Default",
                },
                "ProductName": "DecoyDetector",
                "RecordState": "ACTIVE",
                "Region": "us-east-1",
                "Resources": [
                    {
                        "Id": "arn:aws:ssm:us-east-1:123456789012:parameter/info-parameter",
                        "Partition": "aws",
                        "Region": "us-east-1",
                        "ResourceRole": "Target",
                        "Type": "Other",
                    },
                    {
                        "Id": "arn:aws:kms:us-east-1:123456789012:key/007ab31c-bf66-2264-a916-49f6d2ebd1db",
                        "Partition": "aws",
                        "Region": "us-east-1",
                        "ResourceRole": "Target",
                        "Type": "AwsKmsKey",
                    },
                    {
                        "Details": {
                            "AwsIamAccessKey": {
                                "AccessKeyId": "ABC9ONWNS3155VIEJC8U",
                                "AccountId": "123456789012",
                                "PrincipalId": "ABCDEFG0TOGJSGNQKI0:john.doe",
                                "PrincipalType": "AssumedRole",
                                "SessionContext": {
                                    "Attributes": {"CreationDate": "2024-05-24T22:32:38Z", "MfaAuthenticated": False},
                                    "SessionIssuer": {
                                        "AccountId": "123456789012",
                                        "Arn": "arn:aws:iam::123456789012:user/tester",
                                        "PrincipalId": "ABCDEFG0TOGJSGNQKI0",
                                        "Type": "Role",
                                        "UserName": "user_ab21cde50f",
                                    },
                                },
                            },
                        },
                        "Id": "ABC9ONWNS3155VIEJC8U",
                        "Partition": "aws",
                        "Region": "us-east-1",
                        "ResourceRole": "Actor",
                        "Type": "AwsIamAccessKey",
                    },
                    {
                        "Id": "arn:aws:iam::123456789012:user/tester",
                        "Partition": "aws",
                        "Region": "us-east-1",
                        "ResourceRole": "Actor",
                        "Type": "AwsIamRole",
                    },
                ],
                "SchemaVersion": "2018-10-08",
                "Severity": {"Label": "HIGH", "Normalized": 70},
                "Title": "Non-Suspicious activity detected accessing private decoy Systems Manager parameter arn:aws:ssm:us-east-1:123456789012:parameter/info-parameter",
                "Types": ["Unusual Behaviors"],
                "UpdatedAt": "2024-05-24 22:34:07.000000000",
                "Workflow": {"Status": "NEW"},
                "WorkflowState": "NEW",
                "p_any_actor_ids": [],
                "p_any_aws_account_ids": [],
                "p_any_aws_arns": [],
                "p_any_trace_ids": [],
                "p_any_usernames": [],
                "p_event_time": "2024-05-24 22:34:07.000000000",
                "p_log_type": "AWS.SecurityFindingFormat",
                "p_parse_time": "2024-05-24 22:35:04.272574202",
                "p_row_id": "zjj8nmnw9f90uulxfa3bmen8rv5stlcx",
                "p_schema_version": 0,
                "p_source_id": "bb4e16c5-43dd-450c-9227-39f0d152659c",
                "p_source_label": "AWS Security Hub",
            },
        ),
    ]
