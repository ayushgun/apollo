# static: true
# encoding: utf8

# Imports
import dataclasses
import datetime
import pprint
import dotenv
import praw

# Load Config Data
dotenv.load_dotenv()

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
          the top 6 comments on the post.
    """

    post_id: str
    author: str
    score: int
    title: str
    body: str
    url: str
    num_comments: int
    top_comments: list[dict[str, int | str]]


class Scraper:
    """
    A scraper that extracts data pertaining to a subreddit.

    Attributes:
        subreddit_name: the name of the subreddit to scrape.

    Raises:
        urllib.error.HTTPError: occurs when subreddit_name corresponds to a
          private/banned subreddit.
    """

    def __init__(self, subreddit_name: str) -> None:
        """
        Initializes the reddit.Scraper object with subreddit name.
        """

        self.config = dotenv.dotenv_values(".env")
        self.client = praw.Reddit(
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"],
            user_agent=f"mac:{self.config['client_id']}:v1.0 (by u/{self.config['username']})",
        )
        self.subreddit = self.client.subreddit(subreddit_name.replace("r/", ""))

    def __fetch_comments(
        self, comments: list[praw.models.Comment]
    ) -> list[dict[str, int | str]]:
        """
        Internal helper for fetching comment data from comment list.
        """

        return [
            {"score": com.score, "author": com.author, "body": com.body}
            for com in comments
            if isinstance(com, praw.models.Comment)
        ]

    def search_for_keyword(
        self, search_query: str, sorting: str = "hot", interval: str = "day"
    ) -> list[Post]:
        # sourcery skip: class-extract-method
        """
        Search subreddit posts by query.

        Searches subreddit posts for posts containing the search query. Sorts subreddit
        submissions by hot by default. Searched posts are from the most recent day by default.

        Args:
            search_query: string representing the search query.
            sorting: string representing the sorting of submissions. Acceptable
              values are "relevance", "hot", "top", "new", "comments".
            interval: string representing the time filter for submissions. Acceptable
              values are "all", "day", "hour", "month", "week", "year".

        Returns:
            A list of reddit.Post objects containing submission data.

        Raises:
            urllib.error.HTTPError: occurs when the scraper is unable to search posts.
        """

        # Search subreddit for content
        search_results = self.subreddit.search(
            query=search_query, sort=sorting, time_filter=interval
        )

        # Store submission data as list of reddit.Post objects
        post_data = []
        for submission in search_results:
            # Configure comment search
            submission.comment_sort = "confidence"
            submission.comment_limit = 6

            # Append reddit.Post object to list
            post_data.append(
                Post(
                    post_id=submission.id,
                    author=submission.author,
                    score=submission.score,
                    title=submission.title,
                    body=submission.selftext,
                    url=f"https://reddit.com{submission.permalink}",
                    num_comments=submission.num_comments,
                    top_comments=self.__fetch_comments(submission.comments.list()),
                )
            )

        return post_data

    def posts_from_half_year(self) -> list[Post]:
        """
        Fetch top posts of the last 26 weeks.

        Searches through the top subreddit posts within the last year. Returns posts
        created within a 26 week interval from the run date.

        Returns:
            A list of reddit.Post objects containing submission data.

        Raises:
            urllib.error.HTTPError: occurs when the scraper is unable to search posts.
        """

        # Fetch top posts from last year
        top_posts = self.subreddit.top(time_filter="year")

        # Calculate unix epoch time
        current_time = datetime.datetime.now(datetime.timezone.utc).timestamp()

        # Store submission data as list of reddit.Post objects
        post_data = []
        for submission in top_posts:
            # Filter for submissions from <26 weeks
            if submission.created_utc > current_time - 15720000:
                # Configure comment search
                submission.comment_sort = "confidence"
                submission.comment_limit = 6

                # Append reddit.Post object to list
                post_data.append(
                    Post(
                        post_id=submission.id,
                        author=submission.author,
                        score=submission.score,
                        title=submission.title,
                        body=submission.selftext,
                        url=f"https://reddit.com{submission.permalink}",
                        num_comments=submission.num_comments,
                        top_comments=self.__fetch_comments(submission.comments.list()),
                    )
                )

        return post_data

    def comments_from_half_year(self) -> list[dict[str, int | str]]:
        """
        Fetch comments from top posts of the last 26 weeks.

        Searches through the top subreddit posts within the last year. Returns top comments
        of posts created within a 26 week interval from the run date.

        Returns:
            A list of dictionaries containing comment scores, authors, and bodies.

        Raises:
            urllib.error.HTTPError: occurs when the scraper is unable to search posts.
        """

        top_posts = self.posts_from_half_year()
        return [post.top_comments for post in top_posts]


if __name__ == "__main__":
    scraper = Scraper("r/cryptocurrency")
    pprint.pprint(scraper.search_for_keyword(search_query=""))
