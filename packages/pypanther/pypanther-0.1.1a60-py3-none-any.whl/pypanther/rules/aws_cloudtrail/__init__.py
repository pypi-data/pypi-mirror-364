from pypanther.rules.aws_cloudtrail.aws_add_malicious_lambda_extension import (
    AWSLambdaUpdateFunctionConfiguration as AWSLambdaUpdateFunctionConfiguration,
)
from pypanther.rules.aws_cloudtrail.aws_ami_modified_for_public_access import (
    AWSCloudTrailAMIModifiedForPublicAccess as AWSCloudTrailAMIModifiedForPublicAccess,
)
from pypanther.rules.aws_cloudtrail.aws_backdoor_lambda_function import (
    AWSPotentialBackdoorLambda as AWSPotentialBackdoorLambda,
)
from pypanther.rules.aws_cloudtrail.aws_bedrock_deletemodelinvocationloggingconfiguration import (
    AWSBedrockDeleteModelInvocationLoggingConfiguration as AWSBedrockDeleteModelInvocationLoggingConfiguration,
)
from pypanther.rules.aws_cloudtrail.aws_bedrock_guardrail_update_delete import (
    AWSBedrockGuardrailUpdateDelete as AWSBedrockGuardrailUpdateDelete,
)
from pypanther.rules.aws_cloudtrail.aws_cloudtrail_account_discovery import (
    AWSCloudTrailAccountDiscovery as AWSCloudTrailAccountDiscovery,
)
from pypanther.rules.aws_cloudtrail.aws_cloudtrail_attempt_to_leave_org import (
    AWSCloudTrailAttemptToLeaveOrg as AWSCloudTrailAttemptToLeaveOrg,
)
from pypanther.rules.aws_cloudtrail.aws_cloudtrail_created import AWSCloudTrailCreated as AWSCloudTrailCreated
from pypanther.rules.aws_cloudtrail.aws_cloudtrail_event_selectors_disabled import (
    AWSCloudTrailEventSelectorsDisabled as AWSCloudTrailEventSelectorsDisabled,
)
from pypanther.rules.aws_cloudtrail.aws_cloudtrail_loginprofilecreatedormodified import (
    AWSCloudTrailLoginProfileCreatedOrModified as AWSCloudTrailLoginProfileCreatedOrModified,
)
from pypanther.rules.aws_cloudtrail.aws_cloudtrail_password_policy_discovery import (
    AWSCloudTrailPasswordPolicyDiscovery as AWSCloudTrailPasswordPolicyDiscovery,
)
from pypanther.rules.aws_cloudtrail.aws_cloudtrail_region_enabled import (
    AWSCloudTrailEnableRegion as AWSCloudTrailEnableRegion,
)
from pypanther.rules.aws_cloudtrail.aws_cloudtrail_ses_check_identity_verifications import (
    AWSCloudTrailSESCheckIdentityVerifications as AWSCloudTrailSESCheckIdentityVerifications,
)
from pypanther.rules.aws_cloudtrail.aws_cloudtrail_ses_check_send_quota import (
    AWSCloudTrailSESCheckSendQuota as AWSCloudTrailSESCheckSendQuota,
)
from pypanther.rules.aws_cloudtrail.aws_cloudtrail_ses_check_ses_sending_enabled import (
    AWSCloudTrailSESCheckSESSendingEnabled as AWSCloudTrailSESCheckSESSendingEnabled,
)
from pypanther.rules.aws_cloudtrail.aws_cloudtrail_ses_list_identities import (
    AWSCloudTrailSESListIdentities as AWSCloudTrailSESListIdentities,
)
from pypanther.rules.aws_cloudtrail.aws_cloudtrail_short_lifecycle import (
    AWSCloudTrailShortLifecycle as AWSCloudTrailShortLifecycle,
)
from pypanther.rules.aws_cloudtrail.aws_cloudtrail_stopped import AWSCloudTrailStopped as AWSCloudTrailStopped
from pypanther.rules.aws_cloudtrail.aws_cloudtrail_unsuccessful_mfa_attempt import (
    AWSUnsuccessfulMFAattempt as AWSUnsuccessfulMFAattempt,
)
from pypanther.rules.aws_cloudtrail.aws_cloudtrail_useraccesskeyauth import (
    AWSCloudTrailUserAccessKeyAuth as AWSCloudTrailUserAccessKeyAuth,
)
from pypanther.rules.aws_cloudtrail.aws_codebuild_made_public import (
    AWSCloudTrailCodebuildProjectMadePublic as AWSCloudTrailCodebuildProjectMadePublic,
)
from pypanther.rules.aws_cloudtrail.aws_config_service_created import AWSConfigServiceCreated as AWSConfigServiceCreated
from pypanther.rules.aws_cloudtrail.aws_config_service_disabled_deleted import (
    AWSConfigServiceDisabledDeleted as AWSConfigServiceDisabledDeleted,
)
from pypanther.rules.aws_cloudtrail.aws_console_login import AWSConsoleLogin as AWSConsoleLogin
from pypanther.rules.aws_cloudtrail.aws_console_login_without_mfa import (
    AWSConsoleLoginWithoutMFA as AWSConsoleLoginWithoutMFA,
)
from pypanther.rules.aws_cloudtrail.aws_console_login_without_saml import (
    AWSConsoleLoginWithoutSAML as AWSConsoleLoginWithoutSAML,
)
from pypanther.rules.aws_cloudtrail.aws_console_root_login import AWSConsoleRootLogin as AWSConsoleRootLogin
from pypanther.rules.aws_cloudtrail.aws_console_root_login_failed import (
    AWSConsoleRootLoginFailed as AWSConsoleRootLoginFailed,
)
from pypanther.rules.aws_cloudtrail.aws_console_signin import AWSConsoleSignIn as AWSConsoleSignIn
from pypanther.rules.aws_cloudtrail.aws_dns_logs_deleted import (
    AWSCloudTrailDNSLogsDeleted as AWSCloudTrailDNSLogsDeleted,
)
from pypanther.rules.aws_cloudtrail.aws_ec2_download_instance_user_data import (
    AWSEC2DownloadInstanceUserData as AWSEC2DownloadInstanceUserData,
)
from pypanther.rules.aws_cloudtrail.aws_ec2_ebs_encryption_disabled import (
    AWSEC2EBSEncryptionDisabled as AWSEC2EBSEncryptionDisabled,
)
from pypanther.rules.aws_cloudtrail.aws_ec2_gateway_modified import AWSEC2GatewayModified as AWSEC2GatewayModified
from pypanther.rules.aws_cloudtrail.aws_ec2_launch_unusual_ec2_instances import (
    AWSEC2LaunchUnusualEC2Instances as AWSEC2LaunchUnusualEC2Instances,
)
from pypanther.rules.aws_cloudtrail.aws_ec2_manual_security_group_changes import (
    AWSEC2ManualSecurityGroupChange as AWSEC2ManualSecurityGroupChange,
)
from pypanther.rules.aws_cloudtrail.aws_ec2_many_passwors_read_attempts import (
    AWSEC2ManyPasswordReadAttempts as AWSEC2ManyPasswordReadAttempts,
)
from pypanther.rules.aws_cloudtrail.aws_ec2_monitoring import AWSEC2Monitoring as AWSEC2Monitoring
from pypanther.rules.aws_cloudtrail.aws_ec2_multi_instance_connect import (
    AWSEC2MultiInstanceConnect as AWSEC2MultiInstanceConnect,
)
from pypanther.rules.aws_cloudtrail.aws_ec2_network_acl_modified import (
    AWSEC2NetworkACLModified as AWSEC2NetworkACLModified,
)
from pypanther.rules.aws_cloudtrail.aws_ec2_route_table_modified import (
    AWSEC2RouteTableModified as AWSEC2RouteTableModified,
)
from pypanther.rules.aws_cloudtrail.aws_ec2_security_group_modified import (
    AWSEC2SecurityGroupModified as AWSEC2SecurityGroupModified,
)
from pypanther.rules.aws_cloudtrail.aws_ec2_startup_script_change import (
    AWSEC2StartupScriptChange as AWSEC2StartupScriptChange,
)
from pypanther.rules.aws_cloudtrail.aws_ec2_stopinstances import AWSEC2StopInstances as AWSEC2StopInstances
from pypanther.rules.aws_cloudtrail.aws_ec2_traffic_mirroring import AWSEC2TrafficMirroring as AWSEC2TrafficMirroring
from pypanther.rules.aws_cloudtrail.aws_ec2_vpc_modified import AWSEC2VPCModified as AWSEC2VPCModified
from pypanther.rules.aws_cloudtrail.aws_ec2_vulnerable_xz_image_launched import (
    AWSEC2VulnerableXZImageLaunched as AWSEC2VulnerableXZImageLaunched,
)
from pypanther.rules.aws_cloudtrail.aws_ecr_crud import AWSECRCRUD as AWSECRCRUD
from pypanther.rules.aws_cloudtrail.aws_ecr_events import AWSECREVENTS as AWSECREVENTS
from pypanther.rules.aws_cloudtrail.aws_iam_anything_changed import (
    AWSCloudTrailIAMAnythingChanged as AWSCloudTrailIAMAnythingChanged,
)
from pypanther.rules.aws_cloudtrail.aws_iam_assume_role_blocklist_ignored import (
    AWSCloudTrailIAMAssumeRoleBlacklistIgnored as AWSCloudTrailIAMAssumeRoleBlacklistIgnored,
)
from pypanther.rules.aws_cloudtrail.aws_iam_attach_admin_role_policy import (
    AWSIAMAttachAdminRolePolicy as AWSIAMAttachAdminRolePolicy,
)
from pypanther.rules.aws_cloudtrail.aws_iam_attach_admin_user_policy import (
    AWSIAMAttachAdminUserPolicy as AWSIAMAttachAdminUserPolicy,
)
from pypanther.rules.aws_cloudtrail.aws_iam_backdoor_role import AWSIAMBackdoorRole as AWSIAMBackdoorRole
from pypanther.rules.aws_cloudtrail.aws_iam_compromised_key_quarantine import (
    AWSCloudTrailIAMCompromisedKeyQuarantine as AWSCloudTrailIAMCompromisedKeyQuarantine,
)
from pypanther.rules.aws_cloudtrail.aws_iam_create_role import AWSIAMCreateRole as AWSIAMCreateRole
from pypanther.rules.aws_cloudtrail.aws_iam_create_user import AWSIAMCreateUser as AWSIAMCreateUser
from pypanther.rules.aws_cloudtrail.aws_iam_entity_created_without_cloudformation import (
    AWSCloudTrailIAMEntityCreatedWithoutCloudFormation as AWSCloudTrailIAMEntityCreatedWithoutCloudFormation,
)
from pypanther.rules.aws_cloudtrail.aws_iam_group_read_only_events import (
    AWSIAMGroupReadOnlyEvents as AWSIAMGroupReadOnlyEvents,
)
from pypanther.rules.aws_cloudtrail.aws_iam_policy_modified import AWSIAMPolicyModified as AWSIAMPolicyModified
from pypanther.rules.aws_cloudtrail.aws_iam_user_key_created import AWSIAMBackdoorUserKeys as AWSIAMBackdoorUserKeys
from pypanther.rules.aws_cloudtrail.aws_iam_user_recon_denied import (
    AWSIAMUserReconAccessDenied as AWSIAMUserReconAccessDenied,
)
from pypanther.rules.aws_cloudtrail.aws_ipset_modified import AWSIPSetModified as AWSIPSetModified
from pypanther.rules.aws_cloudtrail.aws_key_compromised import AWSIAMAccessKeyCompromised as AWSIAMAccessKeyCompromised
from pypanther.rules.aws_cloudtrail.aws_kms_cmk_loss import AWSKMSCustomerManagedKeyLoss as AWSKMSCustomerManagedKeyLoss
from pypanther.rules.aws_cloudtrail.aws_lambda_crud import AWSLAMBDACRUD as AWSLAMBDACRUD
from pypanther.rules.aws_cloudtrail.aws_macie_evasion import AWSMacieEvasion as AWSMacieEvasion
from pypanther.rules.aws_cloudtrail.aws_modify_cloud_compute_infrastructure import (
    AWSModifyCloudComputeInfrastructure as AWSModifyCloudComputeInfrastructure,
)
from pypanther.rules.aws_cloudtrail.aws_network_acl_permissive_entry import (
    AWSCloudTrailNetworkACLPermissiveEntry as AWSCloudTrailNetworkACLPermissiveEntry,
)
from pypanther.rules.aws_cloudtrail.aws_overwrite_lambda_code import (
    AWSLambdaUpdateFunctionCode as AWSLambdaUpdateFunctionCode,
)
from pypanther.rules.aws_cloudtrail.aws_rds_manual_snapshot_created import (
    AWSRDSManualSnapshotCreated as AWSRDSManualSnapshotCreated,
)
from pypanther.rules.aws_cloudtrail.aws_rds_master_pass_updated import (
    AWSRDSMasterPasswordUpdated as AWSRDSMasterPasswordUpdated,
)
from pypanther.rules.aws_cloudtrail.aws_rds_publicrestore import AWSRDSPublicRestore as AWSRDSPublicRestore
from pypanther.rules.aws_cloudtrail.aws_rds_snapshot_shared import AWSRDSSnapshotShared as AWSRDSSnapshotShared
from pypanther.rules.aws_cloudtrail.aws_resource_made_public import (
    AWSCloudTrailResourceMadePublic as AWSCloudTrailResourceMadePublic,
)
from pypanther.rules.aws_cloudtrail.aws_root_access_key_created import (
    AWSCloudTrailRootAccessKeyCreated as AWSCloudTrailRootAccessKeyCreated,
)
from pypanther.rules.aws_cloudtrail.aws_root_activity import AWSRootActivity as AWSRootActivity
from pypanther.rules.aws_cloudtrail.aws_root_password_changed import (
    AWSCloudTrailRootPasswordChanged as AWSCloudTrailRootPasswordChanged,
)
from pypanther.rules.aws_cloudtrail.aws_s3_bucket_deleted import AWSS3BucketDeleted as AWSS3BucketDeleted
from pypanther.rules.aws_cloudtrail.aws_s3_bucket_policy_modified import (
    AWSS3BucketPolicyModified as AWSS3BucketPolicyModified,
)
from pypanther.rules.aws_cloudtrail.aws_s3_copy_object_with_client_side_encryption import (
    AWSS3CopyObjectWithClientSideEncryption as AWSS3CopyObjectWithClientSideEncryption,
)
from pypanther.rules.aws_cloudtrail.aws_s3_delete_object import AWSS3DeleteObject as AWSS3DeleteObject
from pypanther.rules.aws_cloudtrail.aws_s3_delete_objects import AWSS3DeleteObjects as AWSS3DeleteObjects
from pypanther.rules.aws_cloudtrail.aws_saml_activity import AWSSuspiciousSAMLActivity as AWSSuspiciousSAMLActivity
from pypanther.rules.aws_cloudtrail.aws_secretsmanager_retrieve_secrets import (
    AWSSecretsManagerRetrieveSecrets as AWSSecretsManagerRetrieveSecrets,
)
from pypanther.rules.aws_cloudtrail.aws_secretsmanager_retrieve_secrets_batch import (
    AWSSecretsManagerBatchRetrieveSecrets as AWSSecretsManagerBatchRetrieveSecrets,
)
from pypanther.rules.aws_cloudtrail.aws_secretsmanager_retrieve_secrets_catchall import (
    AWSSecretsManagerBatchRetrieveSecretsCatchAll as AWSSecretsManagerBatchRetrieveSecretsCatchAll,
)
from pypanther.rules.aws_cloudtrail.aws_secretsmanager_retrieve_secrets_multiregion import (
    AWSSecretsManagerRetrieveSecretsMultiRegion as AWSSecretsManagerRetrieveSecretsMultiRegion,
)
from pypanther.rules.aws_cloudtrail.aws_security_configuration_change import (
    AWSCloudTrailSecurityConfigurationChange as AWSCloudTrailSecurityConfigurationChange,
)
from pypanther.rules.aws_cloudtrail.aws_securityhub_finding_evasion import (
    AWSSecurityHubFindingEvasion as AWSSecurityHubFindingEvasion,
)
from pypanther.rules.aws_cloudtrail.aws_snapshot_made_public import (
    AWSCloudTrailSnapshotMadePublic as AWSCloudTrailSnapshotMadePublic,
)
from pypanther.rules.aws_cloudtrail.aws_software_discovery import AWSSoftwareDiscovery as AWSSoftwareDiscovery
from pypanther.rules.aws_cloudtrail.aws_ssm_decrypt_ssm_params import AWSSSMDecryptSSMParams as AWSSSMDecryptSSMParams
from pypanther.rules.aws_cloudtrail.aws_ssm_distributed_command import (
    AWSSSMDistributedCommand as AWSSSMDistributedCommand,
)
from pypanther.rules.aws_cloudtrail.aws_unauthorized_api_call import (
    AWSCloudTrailUnauthorizedAPICall as AWSCloudTrailUnauthorizedAPICall,
)
from pypanther.rules.aws_cloudtrail.aws_unused_region import AWSUnusedRegion as AWSUnusedRegion
from pypanther.rules.aws_cloudtrail.aws_update_credentials import AWSIAMCredentialsUpdated as AWSIAMCredentialsUpdated
from pypanther.rules.aws_cloudtrail.aws_vpc_flow_logs_deleted import AWSVPCFlowLogsDeleted as AWSVPCFlowLogsDeleted
from pypanther.rules.aws_cloudtrail.aws_vpce_access_denied import (
    AWSCloudTrailVPCEAccessDenied as AWSCloudTrailVPCEAccessDenied,
)
from pypanther.rules.aws_cloudtrail.aws_vpce_external_principal import (
    AWSCloudTrailVPCEExternalPrincipal as AWSCloudTrailVPCEExternalPrincipal,
)
from pypanther.rules.aws_cloudtrail.aws_vpce_s3_external_ip import (
    AWSCloudTrailVPCES3ExternalIP as AWSCloudTrailVPCES3ExternalIP,
)
from pypanther.rules.aws_cloudtrail.aws_vpce_sensitive_api_calls import (
    AWSCloudTrailVPCESensitiveAPICalls as AWSCloudTrailVPCESensitiveAPICalls,
)
from pypanther.rules.aws_cloudtrail.aws_waf_disassociation import AWSWAFDisassociation as AWSWAFDisassociation
from pypanther.rules.aws_cloudtrail.retrieve_sso_access_token import RetrieveSSOaccesstoken as RetrieveSSOaccesstoken
from pypanther.rules.aws_cloudtrail.role_assumed_by_aws_service import (
    RoleAssumedbyAWSService as RoleAssumedbyAWSService,
)
from pypanther.rules.aws_cloudtrail.role_assumed_by_user import RoleAssumedbyUser as RoleAssumedbyUser
from pypanther.rules.aws_cloudtrail.signin_with_aws_cli_prompt import SigninwithAWSCLIprompt as SigninwithAWSCLIprompt
