from pypanther import LogType, Rule, RuleTest, Severity, panther_managed
from pypanther.helpers.cloudflare import cloudflare_fw_alert_context


@panther_managed
class CloudflareFirewallL7DDoS(Rule):
    id = "Cloudflare.Firewall.L7DDoS-prototype"
    display_name = "Cloudflare L7 DDoS"
    log_types = [LogType.CLOUDFLARE_FIREWALL]
    tags = ["Cloudflare", "Variable Severity"]
    default_severity = Severity.MEDIUM
    default_description = "Layer 7 Distributed Denial of Service (DDoS) detected"
    default_runbook = "Inspect and monitor internet-facing services for potential outages"
    default_reference = "https://www.cloudflare.com/en-gb/learning/ddos/application-layer-ddos-attack/"
    threshold = 100
    summary_attributes = ["Action", "ClientCountry", "ClientIP", "ClientRequestUserAgent"]

    def rule(self, event):
        return event.get("Source", "") == "l7ddos"

    def title(self, _):
        return "Cloudflare: Detected L7 DDoS"

    def alert_context(self, event):
        return cloudflare_fw_alert_context(event)

    def severity(self, event):
        if event.get("Action", "") == "block":
            return "Info"
        return "Medium"

    tests = [
        RuleTest(
            name="Traffic Marked as L7DDoS",
            expected_result=True,
            log={
                "Action": "skip",
                "ClientASN": 55836,
                "ClientASNDescription": "RELIANCEJIO-IN Reliance Jio Infocomm Limited",
                "ClientCountry": "in",
                "ClientIP": "127.0.0.1",
                "ClientRequestHost": "example.com",
                "ClientRequestMethod": "GET",
                "ClientRequestPath": "/main.php",
                "ClientRequestProtocol": "HTTP/1.1",
                "ClientRequestQuery": "",
                "ClientRequestScheme": "http",
                "ClientRequestUserAgent": "Fuzz Faster U Fool v1.3.1-dev",
                "Datetime": "2022-05-10 06:36:57",
                "EdgeColoCode": "DEL",
                "EdgeResponseStatus": 403,
                "Kind": "firewall",
                "MatchIndex": 0,
                "Metadata": {"dos-source": "dosd-edge"},
                "OriginResponseStatus": 0,
                "OriginatorRayID": "00",
                "RayID": "7090a9da88e333d8",
                "RuleID": "ed651449c4a54f4b99c6e3bf863134d5",
                "Source": "l7ddos",
            },
        ),
        RuleTest(
            name="Traffic Marked as L7DDoS but blocked ( INFO level alert )",
            expected_result=True,
            log={
                "Action": "block",
                "ClientASN": 55836,
                "ClientASNDescription": "RELIANCEJIO-IN Reliance Jio Infocomm Limited",
                "ClientCountry": "in",
                "ClientIP": "127.0.0.1",
                "ClientRequestHost": "example.com",
                "ClientRequestMethod": "GET",
                "ClientRequestPath": "/main.php",
                "ClientRequestProtocol": "HTTP/1.1",
                "ClientRequestQuery": "",
                "ClientRequestScheme": "http",
                "ClientRequestUserAgent": "Fuzz Faster U Fool v1.3.1-dev",
                "Datetime": "2022-05-10 06:36:57",
                "EdgeColoCode": "DEL",
                "EdgeResponseStatus": 403,
                "Kind": "firewall",
                "MatchIndex": 0,
                "Metadata": {"dos-source": "dosd-edge"},
                "OriginResponseStatus": 0,
                "OriginatorRayID": "00",
                "RayID": "7090a9da88e333d8",
                "RuleID": "ed651449c4a54f4b99c6e3bf863134d5",
                "Source": "l7ddos",
            },
        ),
        RuleTest(
            name="Traffic Not Marked as L7DDoS",
            expected_result=False,
            log={
                "Action": "block",
                "ClientASN": 55836,
                "ClientASNDescription": "RELIANCEJIO-IN Reliance Jio Infocomm Limited",
                "ClientCountry": "in",
                "ClientIP": "127.0.0.1",
                "ClientRequestHost": "example.com",
                "ClientRequestMethod": "GET",
                "ClientRequestPath": "/main.php",
                "ClientRequestProtocol": "HTTP/1.1",
                "ClientRequestQuery": "",
                "ClientRequestScheme": "http",
                "ClientRequestUserAgent": "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
                "Datetime": "2022-05-10 06:36:57",
                "EdgeColoCode": "DEL",
                "EdgeResponseStatus": 403,
                "Kind": "firewall",
                "MatchIndex": 0,
                "Metadata": {"dos-source": "dosd-edge"},
                "OriginResponseStatus": 0,
                "OriginatorRayID": "00",
                "RayID": "708174c00f61faa8",
                "RuleID": "e35c9a670b864a3ba0203ffb1bc977d1",
                "Source": "firewallmanaged",
            },
        ),
    ]
