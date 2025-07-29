from pypanther import LogType, Rule, RuleTest, Severity, panther_managed
from pypanther.helpers.snyk import snyk_alert_context


@panther_managed
class SnykSystemExternalAccess(Rule):
    id = "Snyk.System.ExternalAccess-prototype"
    display_name = "Snyk System External Access Settings Changed"
    log_types = [LogType.SNYK_GROUP_AUDIT, LogType.SNYK_ORG_AUDIT]
    tags = ["Snyk"]
    default_severity = Severity.HIGH
    default_description = "Detects when Snyk Settings that control access for external parties have been changed.\n"
    default_runbook = "This action in the Snyk Audit logs indicate that the setting for allowing external parties to request access to your Snyk installation have changed.\n"
    default_reference = "https://docs.snyk.io/snyk-admin/manage-users-and-permissions/organization-access-requests"
    summary_attributes = ["event"]
    ACTIONS = ["group.request_access_settings.edit", "org.request_access_settings.edit"]

    def rule(self, event):
        action = event.get("event", "<NO_EVENT>")
        return action in self.ACTIONS

    def title(self, event):
        current_setting = event.deep_get("content", "after", "isEnabled", default=False)
        action = event.get("event", "<NO_EVENT>")
        if "." in action:
            action = action.split(".")[0].title()
        return f"Snyk: [{action}] External Access settings have been modified to PermitExternalUsers:[{current_setting}] performed by [{event.deep_get('userId', default='<NO_USERID>')}]"

    def alert_context(self, event):
        a_c = snyk_alert_context(event)
        current_setting = event.deep_get("content", "after", "isEnabled", default=False)
        a_c["current_setting"] = current_setting
        return a_c

    def dedup(self, event):
        return f"{event.deep_get('userId', default='<NO_USERID>')}{event.deep_get('orgId', default='<NO_ORGID>')}{event.deep_get('groupId', default='<NO_GROUPID>')}"

    def severity(self, event):
        current_setting = event.deep_get("content", "after", "isEnabled", default=False)
        if current_setting:
            return "HIGH"
        return "INFO"

    tests = [
        RuleTest(
            name="Snyk External Access Allowed By External Parties - Enabled",
            expected_result=True,
            log={
                "groupId": "8fffffff-1555-4444-b000-b55555555555",
                "event": "group.request_access_settings.edit",
                "content": {"after": {"isEnabled": True}, "before": {}},
                "created": "2023-03-03T19:52:01.628Z",
                "userId": "05555555-3333-4ddd-8ccc-755555555555",
            },
        ),
        RuleTest(
            name="Snyk External Access Allowed By External Parties - Disabled",
            expected_result=True,
            log={
                "groupId": "8fffffff-1555-4444-b000-b55555555555",
                "event": "group.request_access_settings.edit",
                "content": {"after": {}, "before": {"isEnabled": True}},
                "created": "2023-03-03T20:52:01.628Z",
                "userId": "05555555-3333-4ddd-8ccc-755555555555",
            },
        ),
        RuleTest(
            name="Snyk Group SSO Membership sync",
            expected_result=False,
            log={
                "content": {
                    "addAsOrgAdmin": [],
                    "addAsOrgCollaborator": ["group.name"],
                    "addAsOrgCustomRole": [],
                    "addAsOrgRestrictedCollaborator": [],
                    "removedOrgMemberships": [],
                    "userPublicId": "05555555-3333-4ddd-8ccc-755555555555",
                },
                "created": "2023-03-15 13:13:13.133",
                "event": "group.sso.membership.sync",
                "groupId": "8fffffff-1555-4444-b000-b55555555555",
            },
        ),
    ]
