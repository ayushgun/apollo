# encoding: utf8

# Imports
import dataclasses
import datetime
import json
import typing
import uuid

import dotenv
import praw
import requests
import typer


class _RedditConfig:
    """
    A class that handles the configuration needed for Reddit API interaction.

    This class is responsible for loading environment variables and returning a
    praw.Reddit instance configured with these variables.
    """

    def __init__(self):
        dotenv.load_dotenv()
        self.config = dotenv.dotenv_values(".env")

    def get_client(self):
        """
        Returns a praw.Reddit instance configured with client id, client secret, and
        user agent.

        Returns:
            (praw.Reddit): The configured Reddit instance.
        """

        return praw.Reddit(
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"],
            user_agent=(
                f"mac:{self.config['client_id']}:v1.0"
                f" (by u/{self.config['username']})"
            ),
        )


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
        top_comments: a list of the scores, authors, and contents of the top 10 comments
            on the post.
    """

    def __init__(
        self,
        post_id: str,
        author: str,
        score: int,
        title: str,
        body: str,
        url: str,
        num_comments: int,
        top_comments: list[dict[str, int | str]],
    ):
        self.post_id = post_id
        self.author = author
        self.score = score
        self.title = title
        self.body = body
        self.url = url
        self.num_comments = num_comments
        self.top_comments = top_comments


class RedditScraper:
    """
    A class that manages the scraping functionality of Reddit posts and comments.

    This class uses the Reddit API through PRAW to fetch posts and comments from a given
    subreddit based on certain criteria like keyword search or top posts from a specific
    period.

    Attributes:
        client: A configured instance of the praw.Reddit class for
            interaction with Reddit's API.
    """

    def __init__(self, client: praw.Reddit):
        self.client = client

    def fetch_comments(self, comments: list[praw.models.Comment]):
        """
        Fetches the top comments from a given list of Reddit comments.

        Args:
            comments: List of comments fetched from a Reddit post.

        Returns:
            (List[Dict[str, Union[int, str]]]): List of dictionaries representing each
                comment, including its score, author, and body content.
        """

        return [
            {"score": com.score, "author": f"{com.author}", "body": com.body}
            for com in comments
            if isinstance(com, praw.models.Comment)
        ]

    def validate_subreddit(self, subreddit_name: str) -> bool:
        """
        Validates the existence of a given subreddit.

        Args:
            subreddit_name: Name of the subreddit to validate.

        Returns:
            (bool): True if the subreddit exists, False otherwise.
        """

        try:
            self.client.subreddit(subreddit_name).subreddit_type
            return True
        except Exception:
            return False

    def search_for_keyword(
        self,
        subreddit_name: str,
        search_query: str,
        sorting: str = "hot",
        interval: str = "day",
        output: str = "json",
    ):
        """
        Searches for posts in a subreddit that contain a specific keyword.

        Searches for posts in the subreddit that contain the search query in their title
        or body. The posts are sorted by a specified criteria (hot, new, top, etc.) and
        from a specific time interval.

        Args:
            subreddit_name: Name of the subreddit to search in.
            search_query: The keyword to search for.
            sorting: The sorting criteria for the posts (default is "hot").
            interval: The time interval to consider for the posts (default is
                "day").
            output: The type of output to generate (default is "json").

        Raises:
            ValueError: occurs when the scraper is unable to search posts or find the
                subreddit.

        Returns:
            (List[Post]): List of Post objects that match the search criteria.
        """

        if not self.validate_subreddit(subreddit_name):
            raise ValueError(f"Invalid subreddit: {subreddit_name}")

        try:
            subreddit = self.client.subreddit(subreddit_name)
            search_results = subreddit.search(
                query=search_query, sort=sorting, time_filter=interval
            )
        except requests.exceptions.RequestException as e:
            raise ValueError(f"An error occurred: {e}")

        post_data = []
        for submission in search_results:
            submission.comment_sort = "confidence"
            submission.comment_limit = 10

            post = Post(
                post_id=submission.id,
                author=str(submission.author),
                score=submission.score,
                title=submission.title,
                body=submission.selftext,
                url=f"https://reddit.com{submission.permalink}",
                num_comments=submission.num_comments,
                top_comments=self.fetch_comments(submission.comments.list()),
            )

            post_data.append(post.__dict__ if output == "json" else post)

        return post_data

    def posts_from_half_year(self, subreddit_name: str, output: str = "json"):
        """
        Fetches the top posts from the last 26 weeks of a given subreddit.

        This method retrieves the top posts from the past year in the subreddit and then
        filters out the posts that were created in the last 26 weeks.

        Args:
            subreddit_name: Name of the subreddit to fetch posts from.
            output: The type of output to generate (default is "json").

        Raises:
            ValueError: occurs when the scraper is unable to find the subreddit.

        Returns:
            (List[Post]): List of Post objects created in the last 26 weeks.
        """

        if not self.validate_subreddit(subreddit_name):
            raise ValueError(f"Invalid subreddit: {subreddit_name}")

        subreddit = self.client.subreddit(subreddit_name.replace("r/", ""))
        top_posts = subreddit.top(time_filter="year")

        current_time = datetime.datetime.now(datetime.timezone.utc).timestamp()

        post_data = []
        for submission in top_posts:
            if submission.created_utc > current_time - 15720000:
                submission.comment_sort = "confidence"
                submission.comment_limit = 10

                post = Post(
                    post_id=submission.id,
                    author=f"{submission.author}",
                    score=submission.score,
                    title=submission.title,
                    body=submission.selftext,
                    url=f"https://reddit.com{submission.permalink}",
                    num_comments=submission.num_comments,
                    top_comments=self.fetch_comments(submission.comments.list()),
                )

                post_data.append(post.__dict__ if output == "json" else post)

        return post_data

    def comments_from_half_year(self, subreddit_name: str, output: str):
        """
        Fetches the top comments from the top posts of the last 26 weeks of a given
        subreddit.

        This method retrieves the top posts from the past 26 weeks in the subreddit and
        then fetches the top comments from these posts.

        Args:
            subreddit_name: Name of the subreddit to fetch comments from.
            output: The type of output to generate (default is "json").

        Returns:
            (List[List[Dict[str, Union[int, str]]]]): List of list of dictionaries,
                where each dictionary represents a comment and each list represents the
                comments of a single post.
        """

        top_posts = self.posts_from_half_year(subreddit_name)
        top_comments = [post.top_comments for post in top_posts]
        return top_comments


class _OutputManager:
    """
    A class that manages the output of the RedditScraper.

    This class is responsible for storing the output data from the RedditScraper into
    a file in a specified format (JSON or plain text).
    """

    def store_output(self, result: typing.Any, output_type: str) -> None:
        """
        Stores the output data from the RedditScraper into a file in a specified format.

        Args:
            result: The data to store.
            output_type: The format to store the data in (default is "json").

        Raises:
            ValueError: occurs if the output type is not JSON or dataclass.

        Returns:
            (None)
        """

        output_type = output_type.lower()
        file_id = f"{uuid.uuid4()}"[:8]
        file_ext = "json" if output_type == "json" else "txt"
        file_path = f"output/{file_id}.{file_ext}"

        with open(file_path, "w", encoding="utf8") as file:
            if output_type == "json":
                json.dump(result, file)
            elif output_type == "dataclass":
                file.writelines(f"{result}")
            else:
                raise ValueError(f"Invalid output type: {output_type}")

        print(f"Successfully stored command output in ./{file_path}")


cli = typer.Typer(add_completion=False)
config = _RedditConfig()
client = config.get_client()
scraper = RedditScraper(client)
storage = _OutputManager()


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
        (List[Post]): List of Post objects that match the search criteria.
    """

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
        (List[Post]): List of Post objects created in the last 26 weeks.
    """

    post_data = scraper.posts_from_half_year(subreddit_name, output)
    storage.store_output(post_data, output_type=output)


@cli.command(name="top-comments")
def comments_from_half_year(
    subreddit_name: str, output: str = "json"
) -> list[list[dict[str, int | str]]]:
    """
    Fetches the top comments from the top posts of the last 26 weeks of a given
    subreddit.

    This method retrieves the top posts from the past 26 weeks in the subreddit and
    then fetches the top comments from these posts.

    Args:
        subreddit_name: Name of the subreddit to fetch comments from.
        output: The type of output to generate (default is "json").

    Returns:
        (List[List[Dict[str, Union[int, str]]]]): List of lists of dictionaries, where
        each dictionary represents a comment and each list represents the comments
        of a single post.
    """

    comment_data = scraper.comments_from_half_year(subreddit_name, output)
    storage.store_output(comment_data, output_type=output)


if __name__ == "__main__":
    cli()
