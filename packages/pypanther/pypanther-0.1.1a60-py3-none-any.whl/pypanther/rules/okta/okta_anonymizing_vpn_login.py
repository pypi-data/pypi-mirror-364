from pypanther import LogType, Rule, RuleTest, Severity, panther_managed
from pypanther.helpers.okta import okta_alert_context


@panther_managed
class OktaAnonymizingVPNLogin(Rule):
    id = "Okta.Anonymizing.VPN.Login-prototype"
    display_name = "Okta Sign-In from VPN Anonymizer"
    log_types = [LogType.OKTA_SYSTEM_LOG]
    reports = {"MITRE ATT&CK": ["TA0006:T1556"]}
    default_severity = Severity.MEDIUM
    default_description = "A user is attempting to sign-in to Okta from a known VPN anonymizer.  The threat actor would access the compromised account using anonymizing proxy services.\n"
    default_runbook = "Restrict this access to trusted Network Zones and deny access from anonymizing proxies in policy using a Dynamic Network Zone.\n"
    default_reference = "https://sec.okta.com/articles/2023/08/cross-tenant-impersonation-prevention-and-detection\n"
    dedup_period_minutes = 360

    def rule(self, event):
        return event.get("eventType") == "user.session.start" and event.deep_get(
            "securityContext",
            "isProxy",
            default=False,
        )

    def title(self, event):
        ip_context = {}
        client = event.get("client", default={})
        security_context = event.get("securityContext", default={})
        if client.get("ipAddress"):
            ip_context["IP"] = client.get("ipAddress")
        for key, source_value in [
            {"ASO", security_context.get("asOrg")},
            {"ISP", security_context.get("isp")},
            {"Domain", security_context.get("domain")},
        ]:
            if source_value:
                ip_context[key] = source_value
        if service := event.deep_get("p_enrichment", "ipinfo_privacy", "client.ipAddress", "service"):
            ip_context["Service"] = service
        return f"{event.deep_get('actor', 'displayName', default='<displayName-not-found>')} <{event.deep_get('actor', 'alternateId', default='alternateId-not-found')}> attempted to sign-in from anonymizing VPN - {ip_context}"

    def alert_context(self, event):
        return okta_alert_context(event)

    def severity(self, event):
        # If the user is using Apple Private Relay, demote the severity to INFO
        if event.deep_get("p_enrichment", "ipinfo_privacy", "client.ipAddress", "service") == "Apple Private Relay":
            return "INFO"
        # Return Medium by default
        return "MEDIUM"

    tests = [
        RuleTest(
            name="Other Event",
            expected_result=False,
            log={
                "actor": {
                    "alternateId": "homer.simpson@duff.com",
                    "displayName": "Homer Simpson",
                    "id": "00abc123",
                    "type": "User",
                },
                "authenticationcontext": {"authenticationStep": 0, "externalSessionId": "100-abc-9999"},
                "client": {
                    "device": "Computer",
                    "geographicalContext": {
                        "city": "Springfield",
                        "country": "United States",
                        "geolocation": {"lat": 20, "lon": -25},
                        "postalCode": "12345",
                        "state": "Ohio",
                    },
                    "ipAddress": "1.3.2.4",
                    "userAgent": {
                        "browser": "CHROME",
                        "os": "Mac OS X",
                        "rawUserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
                    },
                    "zone": "null",
                },
                "debugcontext": {
                    "debugData": {
                        "requestId": "AbCdEf12G",
                        "requestUri": "/api/v1/users/AbCdEfG/lifecycle/reset_factors",
                        "url": "/api/v1/users/AbCdEfG/lifecycle/reset_factors?",
                    },
                },
                "displaymessage": "Authentication of user via MFA",
                "eventtype": "user.session.start",
                "legacyeventtype": "core.user.factor.attempt_fail",
                "outcome": {"reason": "INVALID_CREDENTIALS", "result": "FAILURE"},
                "published": "2022-06-22 18:18:29.015",
                "request": {
                    "ipChain": [
                        {
                            "geographicalContext": {
                                "city": "Springfield",
                                "country": "United States",
                                "geolocation": {"lat": 20, "lon": -25},
                                "postalCode": "12345",
                                "state": "Ohio",
                            },
                            "ip": "1.3.2.4",
                            "version": "V4",
                        },
                    ],
                },
                "securitycontext": {
                    "asNumber": 701,
                    "asOrg": "verizon",
                    "domain": "verizon.net",
                    "isProxy": False,
                    "isp": "verizon",
                },
                "severity": "INFO",
                "target": [
                    {
                        "alternateId": "peter.griffin@company.com",
                        "displayName": "Peter Griffin",
                        "id": "0002222AAAA",
                        "type": "User",
                    },
                ],
                "transaction": {"detail": {}, "id": "ABcDeFgG", "type": "WEB"},
                "uuid": "AbC-123-XyZ",
                "version": "0",
            },
        ),
        RuleTest(
            name="Anonymizing Proxy Used",
            expected_result=True,
            log={
                "actor": {
                    "alternateId": "homer.simpson@duff.com",
                    "displayName": "Homer Simpson",
                    "id": "00abc123",
                    "type": "User",
                },
                "authenticationcontext": {"authenticationStep": 0, "externalSessionId": "100-abc-9999"},
                "client": {
                    "device": "Computer",
                    "geographicalContext": {
                        "city": "Springfield",
                        "country": "United States",
                        "geolocation": {"lat": 20, "lon": -25},
                        "postalCode": "12345",
                        "state": "Ohio",
                    },
                    "ipAddress": "1.3.2.4",
                    "userAgent": {
                        "browser": "CHROME",
                        "os": "Mac OS X",
                        "rawUserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
                    },
                    "zone": "null",
                },
                "debugcontext": {
                    "debugData": {
                        "requestId": "AbCdEf12G",
                        "requestUri": "/api/v1/users/AbCdEfG/lifecycle/reset_factors",
                        "url": "/api/v1/users/AbCdEfG/lifecycle/reset_factors?",
                    },
                },
                "displaymessage": "Authentication of user via MFA",
                "eventtype": "user.session.start",
                "legacyeventtype": "core.user.factor.attempt_fail",
                "outcome": {"reason": "FastPass declined phishing attempt", "result": "FAILURE"},
                "published": "2022-06-22 18:18:29.015",
                "request": {
                    "ipChain": [
                        {
                            "geographicalContext": {
                                "city": "Springfield",
                                "country": "United States",
                                "geolocation": {"lat": 20, "lon": -25},
                                "postalCode": "12345",
                                "state": "Ohio",
                            },
                            "ip": "1.3.2.4",
                            "version": "V4",
                        },
                    ],
                },
                "securitycontext": {
                    "asNumber": 701,
                    "asOrg": "verizon",
                    "domain": "anonymous.org",
                    "isProxy": True,
                    "isp": "verizon",
                },
                "severity": "INFO",
                "target": [
                    {
                        "alternateId": "peter.griffin@company.com",
                        "displayName": "Peter Griffin",
                        "id": "0002222AAAA",
                        "type": "User",
                    },
                ],
                "transaction": {"detail": {}, "id": "ABcDeFgG", "type": "WEB"},
                "uuid": "AbC-123-XyZ",
                "version": "0",
            },
        ),
        RuleTest(
            name="Apple Private Relay Used",
            expected_result=True,
            log={
                "actor": {
                    "alternateId": "homer.simpson@duff.com",
                    "displayName": "Homer Simpson",
                    "id": "00abc123",
                    "type": "User",
                },
                "authenticationcontext": {"authenticationStep": 0, "externalSessionId": "100-abc-9999"},
                "client": {
                    "device": "Computer",
                    "geographicalContext": {
                        "city": "Springfield",
                        "country": "United States",
                        "geolocation": {"lat": 20, "lon": -25},
                        "postalCode": "12345",
                        "state": "Ohio",
                    },
                    "ipAddress": "1.3.2.4",
                    "userAgent": {
                        "browser": "CHROME",
                        "os": "Mac OS X",
                        "rawUserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
                    },
                    "zone": "null",
                },
                "debugcontext": {
                    "debugData": {
                        "requestId": "AbCdEf12G",
                        "requestUri": "/api/v1/users/AbCdEfG/lifecycle/reset_factors",
                        "url": "/api/v1/users/AbCdEfG/lifecycle/reset_factors?",
                    },
                },
                "displaymessage": "Authentication of user via MFA",
                "eventtype": "user.session.start",
                "legacyeventtype": "core.user.factor.attempt_fail",
                "outcome": {"reason": "FastPass declined phishing attempt", "result": "FAILURE"},
                "p_enrichment": {
                    "ipinfo_privacy": {
                        "client.ipAddress": {
                            "hosting": True,
                            "p_match": "1.2.3.4",
                            "proxy": False,
                            "relay": True,
                            "service": "Apple Private Relay",
                            "tor": False,
                            "vpn": False,
                        },
                    },
                },
                "published": "2022-06-22 18:18:29.015",
                "request": {
                    "ipChain": [
                        {
                            "geographicalContext": {
                                "city": "Springfield",
                                "country": "United States",
                                "geolocation": {"lat": 20, "lon": -25},
                                "postalCode": "12345",
                                "state": "Ohio",
                            },
                            "ip": "1.3.2.4",
                            "version": "V4",
                        },
                    ],
                },
                "securitycontext": {
                    "asNumber": 701,
                    "asOrg": "verizon",
                    "domain": "anonymous.org",
                    "isProxy": True,
                    "isp": "verizon",
                },
                "severity": "INFO",
                "target": [
                    {
                        "alternateId": "peter.griffin@company.com",
                        "displayName": "Peter Griffin",
                        "id": "0002222AAAA",
                        "type": "User",
                    },
                ],
                "transaction": {"detail": {}, "id": "ABcDeFgG", "type": "WEB"},
                "uuid": "AbC-123-XyZ",
                "version": "0",
            },
        ),
    ]
