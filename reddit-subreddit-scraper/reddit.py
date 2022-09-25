# static: true
# encoding: utf8

# Imports
import dataclasses
import datetime
import typing
import uuid
import dotenv
import praw
import typer
import json

# Load Config Data
dotenv.load_dotenv()
config = dotenv.dotenv_values(".env")

# Initialize CLI
cli = typer.Typer()
client = praw.Reddit(
    client_id=config["client_id"],
    client_secret=config["client_secret"],
    user_agent=f"mac:{config['client_id']}:v1.0 (by u/{config['username']})",
)

# Define Objects
@dataclasses.dataclass
class Post:
    """
    A dataclass representing scraped post data.

    Attributes:
        post_id: the post submission ID.
        author: the Reddit username of the post author.
        score: a total count of the post upvotes minus downvotes.
        title: the post submission title.
        body: the body content of the post.
        url: a permanent link to the Reddit post.
        num_comments: the total number of comments on the post.
        top_comments: a list of the scores, authors, and contents of
          the top 10 comments on the post.
    """

    post_id: str
    author: str
    score: int
    title: str
    body: str
    url: str
    num_comments: int
    top_comments: list[dict[str, int | str]]


def __fetch_comments(
    comments: list[praw.models.Comment],  # type: ignore
) -> list[dict[str, int | str]]:
    """
    Internal helper for fetching comment data from comment list.
    """

    return [
        {"score": com.score, "author": f"{com.author}", "body": com.body}
        for com in comments
        if isinstance(com, praw.models.Comment)  # type: ignore
    ]


def __store_output(result: typing.Any, output_type: str) -> None:
    """
    Internal helper for storing command outputs.
    """

    # Determine file data
    output_type = output_type.lower()
    file_id = f"{uuid.uuid4()}"[:8]
    file_ext = "json" if output_type == "json" else "txt"
    file_path = f"output/{file_id}.{file_ext}"

    # Write content to file
    with open(file_path, "w", encoding="utf8") as file:
        if output_type == "json":
            json.dump(result, file)
        else:
            file.writelines(f"{result}")

    print(f"Successfully stored command output in ./{file_path}")


@cli.command(name="keyword_search")
def search_for_keyword(
    subreddit_name: str,
    search_query: str,
    sorting: str = "hot",
    interval: str = "day",
    output: str = "json",
) -> list[Post]:
    # sourcery skip: class-extract-method
    """
    Search subreddit posts by query.

    Searches subreddit posts for posts containing the search query. Sorts subreddit
    submissions by hot by default. Searched posts are from the most recent day by default.

    Args:
        subreddit_name: name of the subreddit to search.
        search_query: string representing the search query.
        sorting: string representing the sorting of submissions. Acceptable
            values are "relevance", "hot", "top", "new", "comments".
        interval: string representing the time filter for submissions. Acceptable
            values are "all", "day", "hour", "month", "week", "year".
        output: controls whether to output data as 'json' or 'dataclass'.

    Returns:
        A list of reddit.Post objects containing submission data.

    Raises:
        urllib.error.HTTPError: occurs when the scraper is unable to search posts.
    """

    # Search subreddit for content
    subreddit = client.subreddit(subreddit_name.replace("r/", ""))
    search_results = subreddit.search(
        query=search_query, sort=sorting, time_filter=interval
    )

    # Store submission data as list of reddit.Post objects
    post_data = []
    for submission in search_results:
        # Configure comment search
        submission.comment_sort = "confidence"
        submission.comment_limit = 10

        # Create reddit.Post object
        post = Post(
            post_id=submission.id,
            author=f"{submission.author}",
            score=submission.score,
            title=submission.title,
            body=submission.selftext,
            url=f"https://reddit.com{submission.permalink}",
            num_comments=submission.num_comments,
            top_comments=__fetch_comments(submission.comments.list()),
        )

        # Append reddit.Post object to list
        post_data.append(dataclasses.asdict(post) if output == "json" else post)

    __store_output(post_data, output_type=output)
    return post_data


@cli.command(name="top_posts")
def posts_from_half_year(subreddit_name: str, output: str = "json") -> list[Post]:
    """
    Fetch top posts of the last 26 weeks.

    Searches through the top subreddit posts within the last year. Returns posts
    created within a 26 week interval from the run date.

    Args:
        subreddit_name: name of the subreddit to search.
        output: controls whether to output data as 'json' or 'dataclass'.

    Returns:
        A list of reddit.Post objects containing submission data.

    Raises:
        urllib.error.HTTPError: occurs when the scraper is unable to search posts.
    """

    # Fetch top posts from last year
    subreddit = client.subreddit(subreddit_name.replace("r/", ""))
    top_posts = subreddit.top(time_filter="year")

    # Calculate unix epoch time
    current_time = datetime.datetime.now(datetime.timezone.utc).timestamp()

    # Store submission data as list of reddit.Post objects
    post_data = []
    for submission in top_posts:
        # Filter for submissions from <26 weeks
        if submission.created_utc > current_time - 15720000:
            # Configure comment search
            submission.comment_sort = "confidence"
            submission.comment_limit = 10

            # Create reddit.Post object
            post = Post(
                post_id=submission.id,
                author=f"{submission.author}",
                score=submission.score,
                title=submission.title,
                body=submission.selftext,
                url=f"https://reddit.com{submission.permalink}",
                num_comments=submission.num_comments,
                top_comments=__fetch_comments(submission.comments.list()),
            )

            # Append reddit.Post object to list
            post_data.append(dataclasses.asdict(post) if output == "json" else post)

    __store_output(post_data, output_type=output)
    return post_data


@cli.command(name="top_comments")
def comments_from_half_year(
    subreddit_name: str, output: str = "json"
) -> list[list[dict[str, int | str]]]:
    """
    Fetch comments from top posts of the last 26 weeks.

    Searches through the top subreddit posts within the last year. Returns top comments
    of posts created within a 26 week interval from the run date.

    Args:
        subreddit_name: name of the subreddit to search.
        output: controls whether to output data as 'json' or 'dataclass

    Returns:
        A list of dictionaries containing comment scores, authors, and bodies.

    Raises:
        urllib.error.HTTPError: occurs when the scraper is unable to search posts.
    """

    # Get comments from posts
    top_posts = posts_from_half_year(subreddit_name, output=output)
    top_comments = [post.top_comments for post in top_posts]

    __store_output(top_comments, output_type=output)
    return top_comments


if __name__ == "__main__":
    cli()
