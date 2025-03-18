from aws_cdk import (
    aws_cloudfront as cf,
    aws_route53 as r53,
    aws_route53_targets as r53_targets,
    Stack,
)
from constructs import Construct


class HostedZone(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        domain_name: str,
        cf_distribution: cf.Distribution,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        zone = r53.HostedZone.from_lookup(self, "hosted-zone", domain_name=domain_name)
        r53.ARecord(
            self,
            "alias",
            zone=zone,
            target=r53.RecordTarget.from_alias(r53_targets.CloudFrontTarget(cf_distribution)),
        )
