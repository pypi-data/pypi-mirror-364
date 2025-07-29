from pypanther import LogType, Rule, RuleTest, Severity, panther_managed
from pypanther.helpers.snyk import snyk_alert_context


@panther_managed
class SnykOrgSettings(Rule):
    id = "Snyk.Org.Settings-prototype"
    display_name = "Snyk Org Settings"
    log_types = [LogType.SNYK_GROUP_AUDIT, LogType.SNYK_ORG_AUDIT]
    tags = ["Snyk"]
    default_reference = "https://docs.snyk.io/snyk-admin/manage-settings/organization-general-settings"
    default_severity = Severity.MEDIUM
    default_description = "Detects when Snyk Organization settings, like Integrations and Webhooks, are changed\n"
    summary_attributes = ["event"]
    ACTIONS = [
        "org.integration.create",
        "org.integration.delete",
        "org.integration.edit",
        "org.integration.settings.edit",
        "org.request_access_settings.edit",
        "org.target.create",
        "org.target.delete",
        "org.webhook.add",
        "org.webhook.delete",
    ]

    def rule(self, event):
        action = event.get("event", "<NO_EVENT>")
        return action in self.ACTIONS

    def title(self, event):
        group_or_org = "<GROUP_OR_ORG>"
        operation = "<NO_OPERATION>"
        action = event.get("event", "<NO_EVENT>")
        if "." in action:
            group_or_org = action.split(".")[0].title()
            operation = ".".join(action.split(".")[1:]).title()
        return f"Snyk: [{group_or_org}] Setting [{operation}] performed by [{event.deep_get('userId', default='<NO_USERID>')}]"

    def alert_context(self, event):
        return snyk_alert_context(event)

    def dedup(self, event):
        return f"{event.deep_get('userId', default='<NO_USERID>')}{event.deep_get('orgId', default='<NO_ORGID>')}{event.deep_get('groupId', default='<NO_GROUPID>')}{event.deep_get('event', default='<NO_EVENT>')}"

    tests = [
        RuleTest(
            name="placeholder",
            expected_result=True,
            log={
                "content": {
                    "after": {
                        "integrationSettings": {
                            "autoDepUpgradeIgnoredDependencies": [],
                            "autoDepUpgradeLimit": 5,
                            "autoRemediationPrs": {"usePatchRemediation": True},
                            "isMajorUpgradeEnabled": True,
                            "manualRemediationPrs": {"useManualPatchRemediation": True},
                            "pullRequestAssignment": {
                                "assignees": ["github_handle", "github_handle2"],
                                "enabled": True,
                                "type": "manual",
                            },
                            "pullRequestTestEnabled": True,
                            "reachableVulns": {},
                        },
                    },
                    "before": {
                        "integrationSettings": {
                            "autoDepUpgradeIgnoredDependencies": [],
                            "autoDepUpgradeLimit": 5,
                            "autoRemediationPrs": {"usePatchRemediation": True},
                            "isMajorUpgradeEnabled": True,
                            "manualRemediationPrs": {"useManualPatchRemediation": True},
                            "pullRequestAssignment": {
                                "assignees": ["github_handle", "github_handle2"],
                                "enabled": True,
                                "type": "manual",
                            },
                            "reachableVulns": {},
                        },
                    },
                    "integrationPublicId": "81111111-cccc-4eee-bfff-3ccccccccccc",
                    "interface": "ui",
                },
                "created": "2023-03-24 14:53:51.334",
                "event": "org.integration.settings.edit",
                "groupId": "8fffffff-1555-4444-b000-b55555555555",
                "orgId": "21111111-a222-4eee-8ddd-a99999999999",
                "userId": "05555555-3333-4ddd-8ccc-755555555555",
            },
        ),
        RuleTest(
            name="Snyk System SSO Setting event happened",
            expected_result=False,
            log={
                "userId": "05555555-3333-4ddd-8ccc-755555555555",
                "event": "group.sso.edit",
                "groupId": "8fffffff-1555-4444-b000-b55555555555",
                "orgId": "21111111-a222-4eee-8ddd-a99999999999",
                "content": {"unknown": "contents"},
            },
        ),
    ]
