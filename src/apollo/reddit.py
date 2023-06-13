import datetime

import praw
import requests
from models import Comment, Post


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

    def __init__(self, client: praw.Reddit) -> None:
        self.client = client

    def fetch_comments(
        self, post: praw.models.Post, output: str = "json"
    ) -> list[Comment]:
        """
        Fetches the top comments from a given list of Reddit comments.

        Args:
            post: Reddit post to fetch comments from.

        Returns:
            (list[Comment]): List of models.Comment, including its score, author, and
                body content.
        """

        post_comments = []

        for comment in post.comments.list():
            if (
                isinstance(comment, praw.models.Comment)
                and hasattr(comment, "author")
                and hasattr(comment, "score")
                and hasattr(comment, "body")
            ):
                comment = Comment(str(comment.author), comment.score, comment.body)
                post_comments.append(comment.__dict__ if output == "json" else comment)

        return post_comments

    def validate_access(self, subreddit_name: str) -> bool:
        """
        Validates the access to a given subreddit.

        Args:
            subreddit_name: Name of the subreddit to validate.

        Returns:
            (bool): True if the subreddit is accessible, False otherwise.
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
    ) -> list[Post]:
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
            (list[Post]): List of models.Post objects that match the search criteria.
        """

        if not self.validate_access(subreddit_name):
            raise ValueError(
                (
                    f"Invalid subreddit: {subreddit_name}. If this error persists, "
                    "you may not have correctly configured Apollo."
                )
            )

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
                top_comments=self.fetch_comments(
                    submission.comments.list(), output=output
                ),
            )

            post_data.append(post.__dict__ if output == "json" else post)

        return post_data

    def posts_from_half_year(
        self, subreddit_name: str, output: str = "json"
    ) -> list[Post]:
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
            (list[Post]): List of models.Post objects created in the last 26 weeks.
        """

        if not self.validate_access(subreddit_name):
            raise ValueError(
                (
                    f"Invalid subreddit: {subreddit_name}. If this error persists, "
                    "you may not have correctly configured Apollo."
                )
            )

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
                    author=str(submission.author),
                    score=submission.score,
                    title=submission.title,
                    body=submission.selftext,
                    url=f"https://reddit.com{submission.permalink}",
                    num_comments=submission.num_comments,
                    top_comments=self.fetch_comments(submission, output=output),
                )

                post_data.append(post.__dict__ if output == "json" else post)

        return post_data

    def comments_from_half_year(
        self, subreddit_name: str, output: str
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

        if not self.validate_access(subreddit_name):
            raise ValueError(
                (
                    f"Invalid subreddit: {subreddit_name}. If this error persists, "
                    "you may not have correctly configured Apollo."
                )
            )

        subreddit = self.client.subreddit(subreddit_name.replace("r/", ""))
        top_posts = subreddit.top(time_filter="year")

        current_time = datetime.datetime.now(datetime.timezone.utc).timestamp()

        comment_data = []

        for submission in top_posts:
            if submission.created_utc > current_time - 15720000:
                submission.comment_sort = "confidence"
                submission.comment_limit = 10

                comment_data.extend(self.fetch_comments(submission, output=output))

        return comment_data
