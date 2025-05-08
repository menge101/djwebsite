from aws_cdk import (
    aws_apigateway as apig,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as cf_origins,
    aws_iam as iam,
    aws_lambda as lam,
)
from constructs import Construct
from typing import cast, Optional


class CdnAPIGLam(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        *,
        handler_path: str,
        code_package_path: str,
        logging_level: Optional[str] = None,
        tracing: Optional[bool] = False,
    ) -> None:
        logging_level = logging_level.upper() if logging_level else "DEBUG"
        super().__init__(scope, id_)
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
        function_environment_variables = {"logging_level": logging_level}
        log_fn = lam.Function(
            self,
            "log_fn",
            code=lam.Code.from_asset(code_package_path),
            handler=handler_path,
            runtime=cast(lam.Runtime, lam.Runtime.PYTHON_3_13),
            role=lambda_role,
            tracing=lam.Tracing.ACTIVE if tracing else lam.Tracing.DISABLED,
            environment=function_environment_variables,
            memory_size=512,
        )
        api2_log_fn = lam.Function(
            self,
            "api2_log_fn",
            code=lam.Code.from_asset(code_package_path),
            handler=handler_path,
            runtime=cast(lam.Runtime, lam.Runtime.PYTHON_3_13),
            role=lambda_role,
            tracing=lam.Tracing.ACTIVE if tracing else lam.Tracing.DISABLED,
            environment=function_environment_variables,
            memory_size=512,
        )
        yolo_log_fn = lam.Function(
            self,
            "log_fn3",
            code=lam.Code.from_asset(code_package_path),
            handler=handler_path,
            runtime=cast(lam.Runtime, lam.Runtime.PYTHON_3_13),
            role=lambda_role,
            tracing=lam.Tracing.ACTIVE if tracing else lam.Tracing.DISABLED,
            environment=function_environment_variables,
            memory_size=512,
        )
        api1 = apig.RestApi(
            self,
            "testapi1",
            deploy=True,
            deploy_options=apig.StageOptions(stage_name="apitest1"),
            endpoint_types=[apig.EndpointType.REGIONAL],
        )
        test_rsrc = api1.root.add_resource("test")
        test_rsrc.add_method("GET", apig.LambdaIntegration(cast(lam.IFunction, log_fn)))
        api2 = apig.RestApi(
            self,
            "testapi2",
            deploy=True,
            deploy_options=apig.StageOptions(stage_name="apitest2"),
            endpoint_types=[apig.EndpointType.REGIONAL],
        )
        default_int = apig.LambdaIntegration(cast(lam.IFunction, log_fn))
        api2_int = apig.LambdaIntegration(cast(lam.IFunction, api2_log_fn))
        yolo_int = apig.LambdaIntegration(cast(lam.IFunction, yolo_log_fn))
        api2.root.add_proxy(default_integration=default_int)
        api2_rsrc = api2.root.add_resource("api2", default_integration=api2_int)
        api2_rsrc.add_proxy(default_integration=api2_int)
        yolo_rsrc = api2_rsrc.add_resource("yolo", default_integration=yolo_int)
        yolo_rsrc.add_proxy(default_integration=yolo_int)
        cloudfront.Distribution(
            self,
            "test-distribution",
            enable_logging=True,
            default_behavior=cloudfront.BehaviorOptions(
                allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                origin=cf_origins.RestApiOrigin(api1),
            ),
            additional_behaviors={
                "/api2*": cloudfront.BehaviorOptions(
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    origin=cf_origins.RestApiOrigin(api2, origin_path="/apitest2"),
                )
            },
        )
