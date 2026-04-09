"""
Multi-stage workflow — chain REST calls with shared context.

Shows how to use @stage decorators to build sequential workflows
where data flows between stages via the WorkflowContext.
"""

from restful import Client, WorkflowContext, stage
from restful.models import Endpoint

# ── Endpoints ────────────────────────────────────────────────────────────

Users = Endpoint(path="/api/v1/users", methods=("GET",))
Posts = Endpoint(path="/api/v1/posts", methods=("GET",))
Comments = Endpoint(path="/api/v1/comments", methods=("GET",))


# ── Stages ───────────────────────────────────────────────────────────────


@stage("Fetch users")
def fetch_users(ctx: WorkflowContext):
    """Get all users and store the first user's ID."""
    response = ctx.clients.api.get(Users)
    users = response.json()
    print(f"  Found {len(users)} users")

    # Store data for the next stage
    first_user = users[0]
    ctx.set("user_id", str(first_user["id"]))
    ctx.set("user_name", first_user["name"])


@stage("Fetch posts for user")
def fetch_posts(ctx: WorkflowContext):
    """Get posts by the user from the previous stage."""
    user_id = ctx.get("user_id")
    user_name = ctx.get("user_name")

    response = ctx.clients.api.get(Posts, query={"userId": int(user_id)})
    posts = response.json()
    print(f"  {user_name} has {len(posts)} posts")

    # Store the first post for the next stage
    if posts:
        ctx.set("post_id", str(posts[0]["id"]))
        ctx.set("post_title", posts[0]["title"])


@stage("Fetch comments on post")
def fetch_comments(ctx: WorkflowContext):
    """Get comments on the post from the previous stage."""
    post_id = ctx.get("post_id")
    post_title = ctx.get("post_title")

    response = ctx.clients.api.get(Comments, query={"postId": int(post_id)})
    comments = response.json()
    print(f'  Post "{post_title[:40]}..." has {len(comments)} comments')

    ctx.set("comment_count", str(len(comments)))


@stage("Summary")
def summary(ctx: WorkflowContext):
    """Print a summary of what we found."""
    print("\n  === Summary ===")
    print(f"  User: {ctx.get('user_name')} (ID: {ctx.get('user_id')})")
    print(f"  Post: {ctx.get('post_title')}")
    print(f"  Comments: {ctx.get('comment_count')}")


# ── Run ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import tempfile
    from pathlib import Path

    from restful.workflow.context import ClientNamespace
    from restful.workflow.runner import WorkflowRunner
    from restful.workspace.variables import VariableStore

    # Build context manually (normally from_workspace does this)
    ns = ClientNamespace()
    ns._add("api", Client(base_url="https://jsonplaceholder.typicode.com"))

    tmp = Path(tempfile.mkdtemp())
    (tmp / ".restful").mkdir()
    ctx = WorkflowContext(clients=ns, variables=VariableStore(tmp))

    runner = WorkflowRunner(ctx)
    results = runner.run(Path(__file__))

    print(f"\n{'─' * 40}")
    passed = sum(1 for r in results if r.success)
    print(f"Completed: {passed}/{len(results)} stages")
