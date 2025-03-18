from aws_cdk import (
    aws_certificatemanager as acm,
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


class Web(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        handler_path: str,
        code_package_path: str,
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
        )
        bucket.grant_read(lambda_role)
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
        function = lam.Function(
            self,
            "primary_fn",
            code=lam.Code.from_asset(code_package_path),
            handler=handler_path,
            runtime=cast(lam.Runtime, lam.Runtime.PYTHON_3_13),
            role=lambda_role,
            tracing=lam.Tracing.ACTIVE if tracing else lam.Tracing.DISABLED,
            environment=function_environment_variables,
            memory_size=512,
        )
        fn_url = function.add_function_url(auth_type=lam.FunctionUrlAuthType.AWS_IAM)
        lambda_origin_access_control = cloudfront.FunctionUrlOriginAccessControl(
            self,
            "lambda-origin-access-control",
            signing=cast(cloudfront.Signing, cloudfront.Signing.SIGV4_ALWAYS),
        )
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
            default_root_object="index.html",
            default_behavior=cloudfront.BehaviorOptions(
                origin=cast(
                    cloudfront.IOrigin,
                    cf_origins.S3BucketOrigin.with_origin_access_control(
                        bucket=cast(s3.IBucket, bucket),
                        origin_access_control=s3_origin_access_control,
                    ),
                ),
                cache_policy=cache_policy,
                origin_request_policy=origin_policy,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            additional_behaviors={
                "/ui/*": cloudfront.BehaviorOptions(
                    origin=cast(
                        cloudfront.IOrigin,
                        cf_origins.FunctionUrlOrigin.with_origin_access_control(
                            fn_url,
                            origin_access_control=lambda_origin_access_control,
                        ),
                    ),
                    cache_policy=cache_policy,
                    origin_request_policy=origin_policy,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                )
            },
            domain_names=domain_names,
            certificate=certificate,
        )
        function.add_permission(
            "cloudfront_permission",
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
