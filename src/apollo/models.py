from dataclasses import dataclass


@dataclass
class Comment:
    """
    A dataclass representing scraped comment data.

    Attributes:
        author: the Reddit username of the post author.
        score: a total count of the post upvotes minus downvotes.
        body: the body content of the post.
    """

    author: str
    score: int
    body: str


@dataclass
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

    post_id: str
    author: str
    score: int
    title: str
    body: str
    url: str
    num_comments: int
    top_comments: list[Comment]
