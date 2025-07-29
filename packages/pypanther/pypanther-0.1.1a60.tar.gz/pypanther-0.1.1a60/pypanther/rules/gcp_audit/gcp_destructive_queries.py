from pypanther import LogType, Rule, RuleTest, Severity, panther_managed


@panther_managed
class GCPDestructiveQueries(Rule):
    default_description = (
        "Detect any destructive BigQuery queries or jobs such as update, delete, drop, alter or truncate."
    )
    display_name = "GCP Destructive Queries"
    default_reference = "https://cloud.google.com/bigquery/docs/managing-tables"
    default_severity = Severity.INFO
    summary_attributes = ["p_alert_context.table"]
    log_types = [LogType.GCP_AUDIT_LOG]
    id = "GCP.Destructive.Queries-prototype"
    DESTRUCTIVE_STATEMENTS = ["UPDATE", "DELETE", "DROP_TABLE", "ALTER_TABLE", "TRUNCATE_TABLE"]

    def rule(self, event):
        if all(
            [
                event.deep_get("resource", "type", default="<RESOURCE_NOT_FOUND>").startswith("bigquery"),
                event.deep_get("protoPayload", "metadata", "jobChange", "job", "jobConfig", "type") == "QUERY",
                event.deep_get(
                    "protoPayload",
                    "metadata",
                    "jobChange",
                    "job",
                    "jobConfig",
                    "queryConfig",
                    "statementType",
                    default="<STATEMENT_NOT_FOUND>",
                )
                in self.DESTRUCTIVE_STATEMENTS,
            ],
        ):
            return True
        if event.deep_get("protoPayload", "metadata", "tableDeletion"):
            return True
        if event.deep_get("protoPayload", "metadata", "datasetDeletion"):
            return True
        return False

    def title(self, event):
        actor = event.deep_get("protoPayload", "authenticationInfo", "principalEmail", default="<ACTOR_NOT_FOUND>")
        statement = event.deep_get(
            "protoPayload",
            "metadata",
            "jobChange",
            "job",
            "jobConfig",
            "queryConfig",
            "statementType",
            default="<STATEMENT_NOT_FOUND>",
        )
        if event.deep_get("protoPayload", "metadata", "jobChange", "job", "jobConfig", "type") == "QUERY":
            return f"GCP: [{actor}] performed a destructive BigQuery [{statement}] query"
        if event.deep_get("protoPayload", "metadata", "tableDeletion"):
            return f"GCP: [{actor}] deleted a table in BigQuery"
        if event.deep_get("protoPayload", "metadata", "datasetDeletion"):
            return f"GCP: [{actor}] deleted a dataset in BigQuery"
        # Default return value
        return f"GCP: [{actor}] performed a destructive BigQuery query"

    def severity(self, event):
        statement = event.deep_get(
            "protoPayload",
            "metadata",
            "jobChange",
            "job",
            "jobConfig",
            "queryConfig",
            "statementType",
            default="<STATEMENT_NOT_FOUND>",
        )
        if statement in ("UPDATE", "DELETE"):
            return "INFO"
        return "DEFAULT"

    def alert_context(self, event):
        return {
            "query": event.deep_get(
                "protoPayload",
                "metadata",
                "jobChange",
                "job",
                "jobConfig",
                "queryConfig",
                "query",
                default="<QUERY_NOT_FOUND>",
            ),
            "actor": event.deep_get(
                "protoPayload",
                "authenticationInfo",
                "principalEmail",
                default="<ACTOR_NOT_FOUND>",
            ),
            "statement": event.deep_get(
                "protoPayload",
                "metadata",
                "jobChange",
                "job",
                "jobConfig",
                "queryConfig",
                "statementType",
                default="<STATEMENT_NOT_FOUND>",
            ),
            "table": event.deep_get(
                "protoPayload",
                "metadata",
                "jobChange",
                "job",
                "jobConfig",
                "queryConfig",
                "destinationTable",
            )
            or event.deep_get("protoPayload", "metadata", "resourceName", default="<TABLE_NOT_FOUND>"),
        }

    tests = [
        RuleTest(
            name="Drop Table Event",
            expected_result=True,
            log={
                "insertid": "abcdefghijklmn",
                "logname": "projects/gcp-project1/logs/cloudaudit.googleapis.com%2Fdata_access",
                "operation": {
                    "id": "1234567890123-gcp-project1:abcdefghijklmnopqrstuvwz",
                    "last": True,
                    "producer": "bigquery.googleapis.com",
                },
                "p_any_emails": ["user@company.io"],
                "p_any_ip_addresses": ["1.2.3.4"],
                "p_event_time": "2023-03-28 18:37:06.079",
                "p_log_type": "GCP.AuditLog",
                "p_parse_time": "2023-03-28 18:38:14.478",
                "p_row_id": "06bf03d9d5dfbadba981899e1787bf05",
                "p_schema_version": 0,
                "p_source_id": "964c7894-9a0d-4ddf-864f-0193438221d6",
                "p_source_label": "gcp-logsource",
                "protopayload": {
                    "at_sign_type": "type.googleapis.com/google.cloud.audit.AuditLog",
                    "authenticationInfo": {"principalEmail": "user@company.io"},
                    "authorizationInfo": [
                        {"granted": True, "permission": "bigquery.jobs.create", "resource": "projects/gcp-project1"},
                    ],
                    "metadata": {
                        "@type": "type.googleapis.com/google.cloud.audit.BigQueryAuditMetadata",
                        "jobChange": {
                            "after": "DONE",
                            "job": {
                                "jobConfig": {
                                    "queryConfig": {
                                        "createDisposition": "CREATE_IF_NEEDED",
                                        "destinationTable": "projects/gcp-project1/datasets/test1/tables/newtable",
                                        "priority": "QUERY_INTERACTIVE",
                                        "query": "DROP TABLE test1.newtable",
                                        "statementType": "DROP_TABLE",
                                        "writeDisposition": "WRITE_EMPTY",
                                    },
                                    "type": "QUERY",
                                },
                                "jobName": "projects/gcp-project1/jobs/abcdefghijklmnopqrstuvwz",
                                "jobStats": {
                                    "createTime": "2023-03-28T18:37:05.842Z",
                                    "endTime": "2023-03-28T18:37:06.073Z",
                                    "queryStats": {},
                                    "startTime": "2023-03-28T18:37:05.934Z",
                                },
                                "jobStatus": {"jobState": "DONE"},
                            },
                        },
                    },
                    "methodName": "google.cloud.bigquery.v2.JobService.InsertJob",
                    "requestMetadata": {
                        "callerIP": "1.2.3.4",
                        "callerSuppliedUserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36,gzip(gfe),gzip(gfe)",
                    },
                    "resourceName": "projects/gcp-project1/jobs/abcdefghijklmnopqrstuvwz",
                    "serviceName": "bigquery.googleapis.com",
                    "status": {},
                },
                "receivetimestamp": "2023-03-28 18:37:06.745",
                "resource": {"labels": {"location": "US", "project_id": "gcp-project1"}, "type": "bigquery_project"},
                "severity": "INFO",
                "timestamp": "2023-03-28 18:37:06.079",
            },
        ),
        RuleTest(
            name="TableDeletion",
            expected_result=True,
            log={
                "insertid": "abcdefghijklmn",
                "logname": "projects/gcp-project1/logs/cloudaudit.googleapis.com%2Factivity",
                "operation": {
                    "id": "1234567890123-gcp-project1:abcdefghijklmnopqrstuvwz",
                    "last": True,
                    "producer": "bigquery.googleapis.com",
                },
                "p_any_emails": ["user@company.io"],
                "p_any_ip_addresses": ["1.2.3.4"],
                "p_event_time": "2023-03-28 18:37:06.079",
                "p_log_type": "GCP.AuditLog",
                "p_parse_time": "2023-03-28 18:38:14.478",
                "p_row_id": "06bf03d9d5dfbadba981899e1787bf05",
                "p_schema_version": 0,
                "p_source_id": "964c7894-9a0d-4ddf-864f-0193438221d6",
                "p_source_label": "gcp-logsource",
                "protopayload": {
                    "at_sign_type": "type.googleapis.com/google.cloud.audit.AuditLog",
                    "authenticationInfo": {"principalEmail": "user@company.io"},
                    "authorizationInfo": [
                        {
                            "granted": True,
                            "permission": "bigquery.tables.delete",
                            "resource": "projects/gcp-project1/datasets/test1/tables/newtable",
                        },
                    ],
                    "metadata": {
                        "@type": "type.googleapis.com/google.cloud.audit.BigQueryAuditMetadata",
                        "methodName": "google.cloud.bigquery.v2.JobService.InsertJob",
                        "requestMetadata": {
                            "callerIP": "1.2.3.4",
                            "callerSuppliedUserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36,gzip(gfe),gzip(gfe)",
                        },
                        "resourceName": "projects/gcp-project1/datasets/test1/tables/newtable",
                        "serviceName": "bigquery.googleapis.com",
                        "status": {},
                        "tableDeletion": {
                            "jobName": "projects/gcp-project1/jobs/bquxjob_5e4a0679_18729a639d7",
                            "reason": "QUERY",
                        },
                    },
                    "receivetimestamp": "2023-03-28 18:37:06.745",
                    "resource": {
                        "labels": {"dataset_id": "test1", "project_id": "gcp-project1"},
                        "type": "bigquery_dataset",
                    },
                    "severity": "NOTICE",
                    "timestamp": "2023-03-28 18:37:06.079",
                },
            },
        ),
        RuleTest(
            name="DataDeletion",
            expected_result=True,
            log={
                "insertid": "abcdefghijklmn",
                "logname": "projects/gcp-project1/logs/cloudaudit.googleapis.com%2Fdata_access",
                "operation": {
                    "id": "1234567890123-gcp-project1:abcdefghijklmnopqrstuvwz",
                    "last": True,
                    "producer": "bigquery.googleapis.com",
                },
                "p_any_emails": ["user@company.io"],
                "p_any_ip_addresses": ["1.2.3.4"],
                "p_event_time": "2023-03-28 18:37:06.079",
                "p_log_type": "GCP.AuditLog",
                "p_parse_time": "2023-03-28 18:38:14.478",
                "p_row_id": "06bf03d9d5dfbadba981899e1787bf05",
                "p_schema_version": 0,
                "p_source_id": "964c7894-9a0d-4ddf-864f-0193438221d6",
                "p_source_label": "gcp-logsource",
                "protopayload": {
                    "at_sign_type": "type.googleapis.com/google.cloud.audit.AuditLog",
                    "authenticationInfo": {"principalEmail": "user@company.io"},
                    "authorizationInfo": [
                        {"granted": True, "permission": "bigquery.jobs.create", "resource": "projects/gcp-project1"},
                    ],
                    "metadata": {
                        "@type": "type.googleapis.com/google.cloud.audit.BigQueryAuditMetadata",
                        "jobChange": {
                            "after": "DONE",
                            "job": {
                                "jobConfig": {
                                    "queryConfig": {
                                        "createDisposition": "CREATE_IF_NEEDED",
                                        "destinationTable": "projects/gcp-project1/datasets/test1/tables/newtable",
                                        "priority": "QUERY_INTERACTIVE",
                                        "query": "DELETE from test1.newtable WHERE foo = bar",
                                        "statementType": "DELETE",
                                        "writeDisposition": "WRITE_EMPTY",
                                    },
                                    "type": "QUERY",
                                },
                                "jobName": "projects/gcp-project1/jobs/abcdefghijklmnopqrstuvwz",
                                "jobStats": {
                                    "createTime": "2023-03-28T18:37:05.842Z",
                                    "endTime": "2023-03-28T18:37:06.073Z",
                                    "queryStats": {},
                                    "startTime": "2023-03-28T18:37:05.934Z",
                                },
                                "jobStatus": {"jobState": "DONE"},
                            },
                        },
                    },
                    "methodName": "google.cloud.bigquery.v2.JobService.InsertJob",
                    "requestMetadata": {
                        "callerIP": "1.2.3.4",
                        "callerSuppliedUserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36,gzip(gfe),gzip(gfe)",
                    },
                    "resourceName": "projects/gcp-project1/jobs/abcdefghijklmnopqrstuvwz",
                    "serviceName": "bigquery.googleapis.com",
                    "status": {},
                },
                "receivetimestamp": "2023-03-28 18:37:06.745",
                "resource": {"labels": {"location": "US", "project_id": "gcp-project1"}, "type": "bigquery_project"},
                "severity": "INFO",
                "timestamp": "2023-03-28 18:37:06.079",
            },
        ),
    ]
