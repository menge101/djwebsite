from aws_cdk import (
    aws_certificatemanager as acm,
    aws_apigateway as api,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as cf_origins,
    aws_dynamodb as ddb,
    aws_iam as iam,
    aws_lambda as lam,
    aws_route53 as r53,
    aws_s3 as s3,
    aws_s3_deployment as s3_deploy,
    Aws,
    CfnOutput,
    RemovalPolicy,
)
from constructs import Construct
from typing import cast, Optional
import secrets


class Web(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        handler_paths: dict[str, str],
        code_package_paths: dict[str, str],
        default_root_object: str,
        removal_policy: Optional[RemovalPolicy] = RemovalPolicy.RETAIN,
        logging_level: Optional[str] = None,
        tracing: Optional[bool] = False,
        cache_policy: Optional[cloudfront.CachePolicy] = cloudfront.CachePolicy.CACHING_OPTIMIZED,
        origin_policy: Optional[cloudfront.OriginRequestPolicy] = cloudfront.OriginRequestPolicy.ALL_VIEWER,
        function_environment_variables: Optional[dict[str, str]] = None,
        domain_name: str | None = None,
    ) -> None:
        logging_level = logging_level.upper() if logging_level else "DEBUG"
        super().__init__(scope, id_)
        function_environment_variables = function_environment_variables or {}
        lambda_policy = iam.ManagedPolicy(
            self,
            "lambda_policy",
            statements=[
                iam.PolicyStatement(
                    actions=["logs:*"],
                    effect=iam.Effect.ALLOW,
                    resources=["arn:aws:logs:*"],
                )
            ],
        )
        lambda_role = iam.Role(
            self,
            "lambda_role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[lambda_policy],
        )
        bucket = s3.Bucket(
            self,
            "bucket",
            removal_policy=removal_policy,
            auto_delete_objects=(removal_policy == RemovalPolicy.DESTROY),
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
        )
        self.table = ddb.Table(
            self,
            "data",
            removal_policy=removal_policy,
            billing_mode=ddb.BillingMode.PAY_PER_REQUEST,
            partition_key=ddb.Attribute(name="pk", type=ddb.AttributeType.STRING),
            sort_key=ddb.Attribute(name="sk", type=ddb.AttributeType.STRING),
            time_to_live_attribute="ttl",
        )
        self.table.grant_read_write_data(lambda_role)
        function_environment_variables["logging_level"] = logging_level
        function_environment_variables["ddb_table_name"] = self.table.table_name
        proxy_fn = lam.Function(
            self,
            "proxy_fn",
            code=lam.Code.from_asset(code_package_paths["proxy"]),
            handler=handler_paths["proxy"],
            runtime=cast(lam.Runtime, lam.Runtime.PYTHON_3_13),
            role=lambda_role,
            tracing=lam.Tracing.ACTIVE if tracing else lam.Tracing.DISABLED,
            environment=function_environment_variables,
            memory_size=512,
            reserved_concurrent_executions=3,
        )
        fn_url = proxy_fn.add_function_url(auth_type=lam.FunctionUrlAuthType.AWS_IAM)
        proxy_integration = api.LambdaIntegration(cast(lam.IFunction, proxy_fn))
        contact_fn = lam.Function(
            self,
            "contact_fn",
            code=lam.Code.from_asset(code_package_paths["contact"]),
            handler=handler_paths["contact"],
            runtime=cast(lam.Runtime, lam.Runtime.PYTHON_3_13),
            role=lambda_role,
            tracing=lam.Tracing.ACTIVE if tracing else lam.Tracing.DISABLED,
            environment=function_environment_variables,
            memory_size=512,
            reserved_concurrent_executions=3,
        )
        contact_integration = api.LambdaIntegration(cast(lam.IFunction, contact_fn))
        api_origin = self.define_api_gateway(proxy_integration, contact_integration)

        s3_origin_access_control = cloudfront.S3OriginAccessControl(
            self,
            "s3-origin-access-control",
            signing=cast(cloudfront.Signing, cloudfront.Signing.SIGV4_ALWAYS),
        )
        certificate = self.create_certificate(domain_name=domain_name) if domain_name else None
        domain_names: list[str] | None = [cast(str, domain_name)] if domain_name else None
        self.distribution = cloudfront.Distribution(
            self,
            "distribution",
            default_root_object=default_root_object,
            default_behavior=cloudfront.BehaviorOptions(
                origin=cast(
                    cloudfront.IOrigin,
                    cf_origins.S3BucketOrigin.with_origin_access_control(
                        bucket=cast(s3.IBucket, bucket),
                        origin_access_control=s3_origin_access_control,
                        origin_access_levels=[cloudfront.AccessLevel.READ, cloudfront.AccessLevel.READ_VERSIONED],
                    ),
                ),
                cache_policy=cache_policy,
                origin_request_policy=origin_policy,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            additional_behaviors={
                "/api*": cloudfront.BehaviorOptions(
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    origin=cast(cloudfront.IOrigin, api_origin),
                    cache_policy=cache_policy,
                    origin_request_policy=origin_policy,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                ),
            },
            domain_names=domain_names,
            certificate=certificate,
        )
        proxy_fn.add_permission(
            "cloudfront_permission",
            principal=iam.ServicePrincipal("cloudfront.amazonaws.com"),
            action="lambda:InvokeFunctionUrl",
            function_url_auth_type=lam.FunctionUrlAuthType.AWS_IAM,
            source_arn=f"arn:aws:cloudfront::{Aws.ACCOUNT_ID}:distribution/{self.distribution.distribution_id}",
        )
        contact_fn.add_permission(
            "cloudfront_permission_for_contact",
            principal=iam.ServicePrincipal("cloudfront.amazonaws.com"),
            action="lambda:InvokeFunctionUrl",
            function_url_auth_type=lam.FunctionUrlAuthType.AWS_IAM,
            source_arn=f"arn:aws:cloudfront::{Aws.ACCOUNT_ID}:distribution/{self.distribution.distribution_id}",
        )
        s3_deploy.BucketDeployment(
            self,
            "source_deploy",
            destination_bucket=cast(s3.IBucket, bucket),
            sources=[s3_deploy.Source.asset("./src")],
            prune=False,
        )
        CfnOutput(self, "cf_domain", value=self.distribution.domain_name)

    def create_certificate(self, domain_name: str) -> acm.Certificate:
        hosted_zone = r53.HostedZone.from_lookup(self, "hosted-zone", domain_name=domain_name)
        return acm.Certificate(
            self,
            "cert",
            domain_name=domain_name,
            validation=acm.CertificateValidation.from_dns(hosted_zone),
        )

    def define_api_gateway(self, proxy_int, contact_int) -> cf_origins.RestApiOrigin:
        gateway = api.RestApi(
            self,
            "api",
            deploy=True,
            endpoint_types=[api.EndpointType.REGIONAL],
            deploy_options=api.StageOptions(
                caching_enabled=False,
                logging_level=api.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
                tracing_enabled=True,
                stage_name="api",
            ),
        )
        gateway.root.add_proxy(default_integration=proxy_int)
        usage_plan = gateway.add_usage_plan(
            "api-uage-plan",
            throttle=api.ThrottleSettings(burst_limit=25, rate_limit=5),
            quota=api.QuotaSettings(limit=500, period=api.Period.DAY),
        )
        api_rsrc = gateway.root.add_resource("api", default_integration=proxy_int)
        proxy = api_rsrc.add_proxy(default_integration=proxy_int)
        contact_rsrc = api_rsrc.add_resource("contact")
        contact_get = contact_rsrc.add_method("GET", contact_int)
        usage_plan.add_api_stage(
            api=gateway,
            stage=gateway.deployment_stage,
            throttle=[
                api.ThrottlingPerMethod(
                    method=contact_get,
                    throttle=api.ThrottleSettings(
                        burst_limit=2,
                        rate_limit=1,
                    ),
                ),
                api.ThrottlingPerMethod(
                    method=cast(api.Method, proxy.any_method),
                    throttle=api.ThrottleSettings(
                        burst_limit=25,
                        rate_limit=5,
                    ),
                ),
            ],
        )

        secret_header_name = "X-Origin-Auth"
        secret_header_value = "my-shared-secret"
        api_key_key = "X-API-KEY"
        api_key_value = f"{secrets.randbits(128):032x}"
        usage_plan.add_api_key(api.ApiKey(self, "api-key", value=api_key_value))
        api_origin = cf_origins.RestApiOrigin(
            gateway,
            custom_headers={secret_header_name: secret_header_value, api_key_key: api_key_value},
        )
        return api_origin
