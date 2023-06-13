import typer
from config import RedditConfig
from models import Comment, Post
from output import OutputManager
from reddit import RedditScraper

cli = typer.Typer(add_completion=False)
config = RedditConfig(".env")
client = config.get_client()
scraper = RedditScraper(client)
storage = OutputManager()


@cli.command(name="keyword-search")
def search_for_keyword(
    subreddit_name: str,
    search_query: str,
    sorting: str = "hot",
    interval: str = "day",
    output: str = "json",
) -> list[Post]:
    """
    Searches for posts in a subreddit that contain a specific keyword.

    Searches for posts in the subreddit that contain the search query in their title
    or body. The posts are sorted by a specified criteria (hot, new, top, etc.) and from
    a specific time interval.

    Args:
        subreddit_name: Name of the subreddit to search in.
        search_query: The keyword to search for.
        sorting: The sorting criteria for the posts (default is "hot").
        interval: The time interval to consider for the posts (default is "day").
        output: The type of output to generate (default is "json").

    Returns:
        (list[Post]): List of models.Post objects that match the search criteria.
    """

    print("Scraping post data...")
    post_data = scraper.search_for_keyword(
        subreddit_name, search_query, sorting, interval, output
    )
    storage.store_output(post_data, output_type=output)


@cli.command(name="top-posts")
def posts_from_half_year(subreddit_name: str, output: str = "json") -> list[Post]:
    """
    Fetches the top posts from the last 26 weeks of a given subreddit.

    This method retrieves the top posts from the past year in the subreddit and then
    filters out the posts that were created in the last 26 weeks.

    Args:
        subreddit_name: Name of the subreddit to fetch posts from.
        output: The type of output to generate (default is "json").

    Returns:
        (list[Post]): List of models.Post objects created in the last 26 weeks.
    """

    print("Scraping post data...")
    post_data = scraper.posts_from_half_year(subreddit_name, output)
    storage.store_output(post_data, output_type=output)


@cli.command(name="top-comments")
def comments_from_half_year(
    subreddit_name: str, output: str = "json"
) -> list[list[Comment]]:
    """
    Fetches the top comments from the top posts of the last 26 weeks of a given
    subreddit.

    This method retrieves the top posts from the past 26 weeks in the subreddit and
    then fetches the top comments from these posts.

    Args:
        subreddit_name: Name of the subreddit to fetch comments from.
        output: The type of output to generate (default is "json").

    Returns:
        (list[list[Comment]]): List of lists of models.Comment and each inner list
            represents the comments of a single post.
    """

    print("Scraping comment data...")
    comment_data = scraper.comments_from_half_year(subreddit_name, output)
    storage.store_output(comment_data, output_type=output)


if __name__ == "__main__":
    cli()
