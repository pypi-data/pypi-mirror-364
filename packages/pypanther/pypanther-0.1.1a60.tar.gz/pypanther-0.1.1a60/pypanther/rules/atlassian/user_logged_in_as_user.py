from pypanther import LogType, Rule, RuleTest, Severity, panther_managed


@panther_managed
class AtlassianUserLoggedInAsUser(Rule):
    display_name = "Atlassian admin impersonated another user"
    id = "Atlassian.User.LoggedInAsUser-prototype"
    default_severity = Severity.HIGH
    log_types = [LogType.ATLASSIAN_AUDIT]
    tags = ["Atlassian", "User impersonation"]
    default_description = "Reports when an Atlassian user logs in (impersonates) another user.\n"
    default_runbook = "Validate that the Atlassian admin did log in (impersonate) as another user.\n"
    default_reference = "https://support.atlassian.com/user-management/docs/log-in-as-another-user/"

    def rule(self, event):
        return event.deep_get("attributes", "action", default="<unknown-action>") == "user_logged_in_as_user"

    def title(self, event):
        actor = event.deep_get("attributes", "actor", "email", default="<unknown-email>")
        context = event.deep_get("attributes", "context", default=[{}])
        impersonated_user = context[0].get("attributes", {}).get("email", "<unknown-email>")
        return f"{actor} logged in as {impersonated_user}."

    def alert_context(self, event):
        return {
            "Timestamp": event.deep_get("attributes", "time", default="<unknown-time>"),
            "Actor": event.deep_get("attributes", "actor", "email", default="<unknown-actor-email>"),
            "Impersonated user": event.deep_get("attributes", "context", default=[{}])[0]
            .get("attributes", {})
            .get("email", "<unknown-email>"),
            "Event ID": event.get("id"),
        }

    tests = [
        RuleTest(
            name="Admin impersonated user successfully",
            expected_result=True,
            log={
                "attributes": {
                    "action": "user_logged_in_as_user",
                    "actor": {
                        "email": "example.admin@example.com",
                        "id": "1234567890abcdefghijklmn",
                        "name": "Example Admin",
                    },
                    "container": [
                        {
                            "attributes": {"siteHostName": "https://example.atlassian.net", "siteName": "example"},
                            "id": "12345678-abcd-9012-efgh-1234567890abcd",
                            "links": {"alt": "https://example.atlassian.net"},
                            "type": "sites",
                        },
                    ],
                    "context": [
                        {
                            "attributes": {
                                "accountType": "atlassian",
                                "email": "example.user@example.io",
                                "name": "example.user@example.io",
                            },
                            "type": "users",
                        },
                    ],
                    "time": "2022-12-15T00:35:15.890Z",
                },
                "id": "2508d209-3336-4763-89a0-aceaf1322fcf",
                "message": {"content": "Logged in as example.user@example.io", "format": "simple"},
            },
        ),
        RuleTest(
            name="user_logged_in_as_user not in log",
            expected_result=False,
            log={
                "attributes": {
                    "action": "user_login",
                    "actor": {
                        "email": "example.admin@example.com",
                        "id": "1234567890abcdefghijklmn",
                        "name": "Example Admin",
                    },
                    "container": [
                        {
                            "attributes": {"siteHostName": "https://example.atlassian.net", "siteName": "example"},
                            "id": "12345678-abcd-9012-efgh-1234567890abcd",
                            "links": {"alt": "https://example.atlassian.net"},
                            "type": "sites",
                        },
                    ],
                    "context": [
                        {
                            "attributes": {
                                "accountType": "atlassian",
                                "email": "example.user@example.io",
                                "name": "example.user@example.io",
                            },
                            "type": "users",
                        },
                    ],
                    "time": "2022-12-15T00:35:15.890Z",
                },
                "id": "2508d209-3336-4763-89a0-aceaf1322fcf",
                "message": {"content": "Logged in as example.user@example.io", "format": "simple"},
            },
        ),
    ]
