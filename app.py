import aws_cdk as cdk
import deploys

app = cdk.App()
deploys.Development(app, "development", env=deploys.DEV_ENV)
deploys.Production(app, "production", env=deploys.PRD_ENV)
app.synth()
