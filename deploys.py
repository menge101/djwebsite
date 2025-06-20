from aws_cdk import (
    aws_cloudfront as cf,
    Duration,
    Environment,
    RemovalPolicy,
    Stack,
    Stage,
)
from constructs import Construct
from infrastructure import cdn_apig_ex, hosted_zone, web
from typing import Optional

DEV_ENV = Environment(account="779846793683", region="us-east-1")
PRD_ENV = Environment(account="473626866269", region="us-east-1")
PRODUCTION_DOMAIN_NAME = "djwzl.com"


class Production(Stage):
    def __init__(self, scope: Construct, id_: str, **kwargs):
        super().__init__(scope, id_, **kwargs)
        removal_policy = RemovalPolicy.RETAIN
        cache_policy_props = cf.CachePolicyProps(
            cookie_behavior=cf.CacheCookieBehavior.all(),
            default_ttl=Duration.seconds(1),
            max_ttl=Duration.seconds(1),
        )
        origin_request_policy_props = cf.OriginRequestPolicyProps(
            cookie_behavior=cf.OriginRequestCookieBehavior.all(),
            header_behavior=cf.OriginRequestHeaderBehavior.none(),
            query_string_behavior=cf.OriginRequestQueryStringBehavior.allow_list("action"),
        )
        throttles = {"proxy": {"burst": 40, "rate": 30}, "contact": {"burst": 2, "rate": 2}}
        notification_email = "nathan.menge@gmail.com"
        api_quota: int = 5000
        website = Website(
            self,
            "djweb",
            removal_policy=removal_policy,
            logging_level="INFO",
            tracing=True,
            cache_policy_props=cache_policy_props,
            origin_request_policy_props=origin_request_policy_props,
            domain_name=PRODUCTION_DOMAIN_NAME,
            throttles=throttles,
            api_quota=api_quota,
            notification_email=notification_email,
        )
        hosted_zone.HostedZone(
            self,
            "prd-hosted-zone",
            domain_name=PRODUCTION_DOMAIN_NAME,
            cf_distribution=website.web.distribution,
        )


class Development(Stage):
    def __init__(self, scope: Construct, id_: str, **kwargs):
        super().__init__(scope, id_, **kwargs)
        removal_policy = RemovalPolicy.DESTROY
        cache_policy_props = cf.CachePolicyProps(
            cookie_behavior=cf.CacheCookieBehavior.all(),
            default_ttl=Duration.seconds(1),
            max_ttl=Duration.seconds(1),
        )
        headers = ["HX-*", "Origin", "Referer", "User-Agent", "Sec*", "Accept*"]
        origin_policy_props = cf.OriginRequestPolicyProps(
            cookie_behavior=cf.OriginRequestCookieBehavior.all(),
            header_behavior=(cf.OriginRequestHeaderBehavior.allow_list(*headers)),
            query_string_behavior=(cf.OriginRequestQueryStringBehavior.all()),
        )
        throttles = {"proxy": {"burst": 40, "rate": 30}, "contact": {"burst": 2, "rate": 2}}
        notification_email = "nathan.menge+dev@gmail.com"
        api_quota: int = 5000
        Website(
            self,
            "djweb",
            removal_policy=removal_policy,
            logging_level="DEBUG",
            tracing=True,
            cache_policy_props=cache_policy_props,
            origin_request_policy_props=origin_policy_props,
            function_environment_variables={"environment_name": "dev"},
            throttles=throttles,
            notification_email=notification_email,
            api_quota=api_quota,
        )


class Website(Stack):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        removal_policy: RemovalPolicy,
        cache_policy_props: cf.CachePolicyProps,
        origin_request_policy_props: cf.OriginRequestPolicyProps,
        logging_level: str,
        tracing: bool,
        api_quota: int,
        throttles: dict[str, dict[str, int]],
        notification_email: str,
        domain_name: str | None = None,
        function_environment_variables: Optional[dict[str, str]] = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, id_, **kwargs)
        cache_policy: cf.CachePolicy = cf.CachePolicy(self, "cache-policy", **cache_policy_props._values)
        origin_request_policy: cf.OriginRequestPolicy = cf.OriginRequestPolicy(
            self, "origin-request-policy", **origin_request_policy_props._values
        )
        self.web = web.Web(
            self,
            "web-application-construct",
            handler_paths={"proxy": "lib.web.handler", "log": "lib.log.handler", "contact": "lib.web.contact"},
            code_package_paths={
                "proxy": "./build/web.zip",
                "log": "./build/logging.zip",
                "contact": "./build/contact.zip",
            },
            default_root_object="test.html",
            removal_policy=removal_policy,
            logging_level=logging_level,
            tracing=tracing,
            cache_policy=cache_policy,
            origin_policy=origin_request_policy,
            domain_name=domain_name,
            function_environment_variables=function_environment_variables,
            api_quota=api_quota,
            throttles=throttles,
            notification_email=notification_email,
        )


class Testing(Stack):
    def __init__(self, scope: Construct, id_: str, **kwargs):
        super().__init__(scope, id_, **kwargs)
        cdn_apig_ex.CdnAPIGLam(
            self,
            "stuff",
            handler_path="lib.log.handler",
            code_package_path="./build/logging.zip",
            logging_level="DEBUG",
        )
