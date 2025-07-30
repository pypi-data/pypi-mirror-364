from infradsl import AWS, DriftAction

DOMAIN = "jspzyasana.com"
CERT = "arn:aws:acm:us-east-1:901920399424:certificate/7a31403e-f7b4-4a46-9c4e-7a6804ca5fcc"

cdn = (
    AWS.CloudFront(f"nolimitjs-cdn-jspzyasana")
    .copy_from("E1G3JSJNE43F6L")
    .clear_domains()
    .custom_domain(f"nolimitjs.{DOMAIN}")
    .ssl_certificate(CERT)
    .drift_policy(DriftAction.IGNORE)
)

route53 = (
    AWS.Route53(f"nolimitjs-dns")
    .use_existing_zone(DOMAIN)
    .cname_record(cdn.name, "nolimitjs")
    .depends_on(cdn)
)
