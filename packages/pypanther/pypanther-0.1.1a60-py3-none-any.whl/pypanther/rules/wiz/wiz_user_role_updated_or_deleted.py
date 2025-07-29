from pypanther import LogType, Rule, RuleTest, Severity, panther_managed
from pypanther.helpers.wiz import wiz_actor, wiz_alert_context, wiz_success


@panther_managed
class WizUserRoleUpdatedOrDeleted(Rule):
    id = "Wiz.User.Role.Updated.Or.Deleted-prototype"
    default_description = "This rule detects updates and deletions of Wiz user roles."
    display_name = "Wiz User Role Updated Or Deleted"
    default_runbook = "Verify that this change was planned. If not, revert the change and ensure this doesn't happen again. Review privileges given to accounts to ensure the principle of minimal privilege"
    default_reference = "https://www.wiz.io/blog/cloud-security-custom-roles-democratization"
    default_severity = Severity.MEDIUM
    reports = {"MITRE ATT&CK": ["TA0003:T1098.001"]}
    log_types = [LogType.WIZ_AUDIT]
    SUSPICIOUS_ACTIONS = ["DeleteUserRole", "UpdateUserRole"]

    def rule(self, event):
        if not wiz_success(event):
            return False
        return event.get("action", "ACTION_NOT_FOUND") in self.SUSPICIOUS_ACTIONS

    def title(self, event):
        actor = wiz_actor(event)
        return f"[Wiz]: [{event.get('action', 'ACTION_NOT_FOUND')}] action performed by {actor.get('type')} [{actor.get('name')}]"

    def dedup(self, event):
        return event.get("id")

    def alert_context(self, event):
        return wiz_alert_context(event)

    def severity(self, event):
        action = event.get("action", "ACTION_NOT_FOUND")
        if "Delete" in action:
            return "High"
        return "Default"

    tests = [
        RuleTest(
            name="DeleteUserRole",
            expected_result=True,
            log={
                "id": "671d8e2d-1ca8-47eb-bf1c-d46cd3f0d737",
                "action": "DeleteUserRole",
                "requestId": "a83aba82-c707-4a2f-9761-fe9ee723b703",
                "status": "SUCCESS",
                "timestamp": "2024-07-31T18:09:28.790129Z",
                "actionParameters": {
                    "input": {"id": "b92c4032-9af8-4e2d-b6dc-3bf2005bb7ad"},
                    "selection": ["__typename", "_stub"],
                },
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "sourceIP": "12.34.56.78",
                "serviceAccount": None,
                "user": {"id": "test.user@company.com", "name": "user@company.com"},
            },
        ),
        RuleTest(
            name="CreateUser",
            expected_result=False,
            log={
                "id": "220d23be-f07c-4d97-b4a6-87ad04eddb14",
                "action": "CreateUser",
                "requestId": "0d9521b2-c3f8-4a73-bf7c-20257788752e",
                "status": "SUCCESS",
                "timestamp": "2024-07-29T09:40:15.66643Z",
                "actionParameters": {
                    "input": {
                        "assignedProjectIds": None,
                        "email": "testy@company.com",
                        "expiresAt": None,
                        "name": "Test User",
                        "role": "GLOBAL_ADMIN",
                    },
                    "selection": ["__typename", {"user": ["__typename", "id"]}],
                },
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "sourceIP": "8.8.8.8",
                "serviceAccount": None,
                "user": {"id": "someuser@company.com", "name": "someuser@company.com"},
            },
        ),
        RuleTest(
            name="DeleteUserRole - Fail",
            expected_result=False,
            log={
                "id": "671d8e2d-1ca8-47eb-bf1c-d46cd3f0d737",
                "action": "DeleteUserRole",
                "requestId": "a83aba82-c707-4a2f-9761-fe9ee723b703",
                "status": "FAILED",
                "timestamp": "2024-07-31T18:09:28.790129Z",
                "actionParameters": {},
                "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "sourceIP": "12.34.56.78",
                "serviceAccount": None,
                "user": {"id": "test.user@company.com", "name": "user@company.com"},
            },
        ),
    ]
