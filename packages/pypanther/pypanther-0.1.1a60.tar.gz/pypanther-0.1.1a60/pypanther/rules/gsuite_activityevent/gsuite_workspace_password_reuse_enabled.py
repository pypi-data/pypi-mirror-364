from pypanther import LogType, Rule, RuleTest, Severity, panther_managed


@panther_managed
class GSuiteWorkspacePasswordReuseEnabled(Rule):
    id = "GSuite.Workspace.PasswordReuseEnabled-prototype"
    display_name = "GSuite Workspace Password Reuse Has Been Enabled"
    log_types = [LogType.GSUITE_ACTIVITY_EVENT]
    tags = ["GSuite"]
    default_severity = Severity.HIGH
    reports = {"MITRE ATT&CK": ["TA0006:T1110"]}
    default_description = "A Workspace Admin Has Enabled Password Reuse\n"
    default_reference = "https://support.google.com/a/answer/139399?hl=en#"
    default_runbook = "Verify the intent of this Password Reuse Setting Change. If intent cannot be verified, then a search on the actor's other activities is advised.\n"
    summary_attributes = ["actor:email"]

    def rule(self, event):
        if event.deep_get("id", "applicationName", default="").lower() != "admin":
            return False
        if all(
            [
                event.get("name", "") == "CHANGE_APPLICATION_SETTING",
                event.get("type", "") == "APPLICATION_SETTINGS",
                event.deep_get("parameters", "NEW_VALUE", default="").lower() == "true",
                event.deep_get("parameters", "SETTING_NAME", default="")
                == "Password Management - Enable password reuse",
            ],
        ):
            return True
        return False

    def title(self, event):
        return f"GSuite Workspace Password Reuse Has Been Enabled By [{event.deep_get('actor', 'email', default='<NO_ACTOR_FOUND>')}]"

    tests = [
        RuleTest(
            name="Workspace Admin Enabled Password Reuse",
            expected_result=True,
            log={
                "actor": {"callerType": "USER", "email": "example@example.io", "profileId": "12345"},
                "id": {
                    "applicationName": "admin",
                    "customerId": "D12345",
                    "time": "2022-12-11 01:18:47.973000000",
                    "uniqueQualifier": "-12345",
                },
                "ipAddress": "12.12.12.12",
                "kind": "admin#reports#activity",
                "name": "CHANGE_APPLICATION_SETTING",
                "parameters": {
                    "APPLICATION_EDITION": "standard",
                    "APPLICATION_NAME": "Security",
                    "NEW_VALUE": "true",
                    "OLD_VALUE": "false",
                    "ORG_UNIT_NAME": "Example IO",
                    "SETTING_NAME": "Password Management - Enable password reuse",
                },
                "type": "APPLICATION_SETTINGS",
            },
        ),
        RuleTest(
            name="Admin Set Default Calendar SHARING_OUTSIDE_DOMAIN Setting to READ_ONLY_ACCESS",
            expected_result=False,
            log={
                "actor": {"callerType": "USER", "email": "example@example.io", "profileId": "12345"},
                "id": {
                    "applicationName": "admin",
                    "customerId": "D12345",
                    "time": "2022-12-11 01:06:26.303000000",
                    "uniqueQualifier": "-12345",
                },
                "ipAddress": "12.12.12.12",
                "kind": "admin#reports#activity",
                "name": "CHANGE_CALENDAR_SETTING",
                "parameters": {
                    "DOMAIN_NAME": "example.io",
                    "NEW_VALUE": "READ_ONLY_ACCESS",
                    "OLD_VALUE": "DEFAULT",
                    "ORG_UNIT_NAME": "Example IO",
                    "SETTING_NAME": "SHARING_OUTSIDE_DOMAIN",
                },
                "type": "CALENDAR_SETTINGS",
            },
        ),
        RuleTest(
            name="ListObject Type",
            expected_result=False,
            log={
                "actor": {"email": "user@example.io", "profileId": "118111111111111111111"},
                "id": {
                    "applicationName": "drive",
                    "customerId": "D12345",
                    "time": "2022-12-20 17:27:47.080000000",
                    "uniqueQualifier": "-7312729053723258069",
                },
                "ipAddress": "12.12.12.12",
                "kind": "admin#reports#activity",
                "name": "rename",
                "parameters": {
                    "actor_is_collaborator_account": None,
                    "billable": True,
                    "doc_id": "1GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
                    "doc_title": "Document Title- Found Here",
                    "doc_type": "presentation",
                    "is_encrypted": None,
                    "new_value": ["Document Title- Found Here"],
                    "old_value": ["Document Title- Old"],
                    "owner": "user@example.io",
                    "owner_is_shared_drive": None,
                    "owner_is_team_drive": None,
                    "primary_event": True,
                    "visibility": "private",
                },
                "type": "access",
            },
        ),
    ]
