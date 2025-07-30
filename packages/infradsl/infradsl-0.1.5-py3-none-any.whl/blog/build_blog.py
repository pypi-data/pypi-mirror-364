#!/usr/bin/env python3
"""
Build script to convert markdown blog posts to HTML and generate homepage
"""

import markdown
from pathlib import Path
from datetime import datetime


def build_homepage():
    """Generate the homepage with minimal blog layout"""

    # Blog posts metadata (this could be automated later by scanning files)
    blog_posts = [
        {
            "title": "The Nexus Engine: InfraDSL's Beating Heart",
            "date": "2025-07-23",
            "excerpt": "If InfraDSL is the Rails of infrastructure, then the Nexus Engine is its ActiveRecord — but one that's been reimagined for the cloud era. It's the intelligent core that makes stateless infrastructure management not just possible, but delightfully simple.",
            "url": "nexus-engine-deep-dive.html",
            "tags": ["nexus", "architecture", "stateless", "infrastructure"],
        },
        {
            "title": "Introducing InfraDSL: The Rails of Modern Infrastructure",
            "date": "2025-07-19",
            "excerpt": "For the past decade, I've lived and breathed infrastructure from both the provider and operator sides of the demanding European iGaming industry. It's a world where speed is paramount, downtime is measured in millions, and every decision is a delicate balance between rapid deployment and unwavering stability.",
            "url": "introducing-infradsl.html",
            "tags": ["python", "infrastructure", "devops", "iascode"],
        },
    ]

    # Generate blog post cards
    posts_html = ""
    for post in blog_posts:
        posts_html += f"""
        <article class="post-card">
            <div class="post-date">{datetime.strptime(post['date'], '%Y-%m-%d').strftime('%B %d, %Y')}</div>
            <h2 class="post-title">
                <a href="{post['url']}">{post['title']}</a>
            </h2>
            <p class="post-preview">{post['excerpt']}</p>
            <a href="{post['url']}" class="read-more">Read more</a>
        </article>
        """

    # HTML template for minimal homepage
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InfraDSL Blog</title>
    <meta name="description" content="Infrastructure that actually works like software should. Thoughts on Python, DevOps, and making things simpler.">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <link rel="stylesheet" href="styles.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
</head>
<body>
    <div class="container">
        <header class="site-header">
            <h1 class="site-title">THE INFRADSL BLOG</h1>
            <p class="site-bio">
                Building infrastructure tools for the past decade in high-pressure European iGaming environments. 
                Created <strong>InfraDSL</strong> to bring Rails-like simplicity to infrastructure management. 
                Writing about Python, DevOps, and why infrastructure doesn't have to be complicated.
            </p>
        </header>

        <main class="posts-section">
            {posts_html}
        </main>
    </div>

    <script>hljs.highlightAll();</script>
</body>
</html>"""

    # Write the HTML file to build directory
    build_dir = Path("/Users/bia/repos/infradsl.dev/blog/build")
    build_dir.mkdir(exist_ok=True)

    homepage_file = build_dir / "index.html"
    with open(homepage_file, "w", encoding="utf-8") as f:
        f.write(html_template)

    print(f"✅ Homepage generated: {homepage_file}")


def build_blog_posts():
    """Convert all markdown blog posts to HTML with dark theme styling"""

    blog_posts = [
        {
            "md_file": "introducing-infradsl.md",
            "html_file": "introducing-infradsl.html",
            "title": "Introducing InfraDSL - The Rails of Modern Infrastructure",
            "description": "A deep dive into InfraDSL - the Python-first framework that brings Rails-like simplicity to infrastructure management.",
        },
        {
            "md_file": "nexus-engine-deep-dive.md",
            "html_file": "nexus-engine-deep-dive.html",
            "title": "The Nexus Engine: InfraDSL's Beating Heart",
            "description": "Explore the intelligent core of InfraDSL that makes stateless infrastructure management delightfully simple.",
        },
    ]

    for post in blog_posts:
        # Read the markdown content
        md_file = Path("/Users/bia/repos/infradsl.dev/blog") / post["md_file"]
        html_file = Path("/Users/bia/repos/infradsl.dev/blog/build") / post["html_file"]

        if not md_file.exists():
            print(f"⚠️  Warning: {md_file} not found, skipping...")
            continue

        with open(md_file, "r", encoding="utf-8") as f:
            md_content = f.read()

        # Convert markdown to HTML with extensions
        md = markdown.Markdown(
            extensions=["codehilite", "fenced_code", "tables", "toc"]
        )
        html_content = md.convert(md_content)

        # Clean, minimal HTML template with dark theme
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post["title"]}</title>
    <meta name="description" content="{post["description"]}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <link rel="stylesheet" href="styles.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/terraform.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/bash.min.js"></script>
</head>
<body>
    <div class="nav">
        <a href="/">← Back to Home</a>
    </div>

    <article>
        {html_content}
    </article>

    <div class="nav">
        <a href="/">← Back to Home</a>
    </div>

    <script>hljs.highlightAll();</script>
</body>
</html>"""

        # Write the HTML file
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_template)

        print(f"✅ Blog post converted: {html_file}")


def copy_styles():
    """Copy styles.css to build directory"""
    build_dir = Path("/Users/bia/repos/infradsl.dev/blog/build")
    build_dir.mkdir(exist_ok=True)

    source_styles = Path("/Users/bia/repos/infradsl.dev/blog/styles.css")
    target_styles = build_dir / "styles.css"

    if source_styles.exists():
        import shutil

        shutil.copy2(source_styles, target_styles)
        print(f"✅ Styles copied: {target_styles}")
    else:
        print(f"⚠️  Warning: styles.css not found at {source_styles}")


if __name__ == "__main__":
    print("🚀 Building InfraDSL Blog...")
    build_homepage()
    build_blog_posts()
    copy_styles()
    print("✨ Build complete!")
