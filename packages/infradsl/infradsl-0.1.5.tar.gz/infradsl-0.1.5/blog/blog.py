from infradsl.resources.firebase import FirebaseHosting

project = "infradsl"

blog = (
    FirebaseHosting("blog")
    .project(project)
    .documentation_site()
    .public_directory("site")
    .build_command("mkdocs build")
    .build_directory(".")
    .custom_domain("blog.infradsl.dev")
)
