import dotenv
import praw


class RedditConfig:
    """
    A class that handles the configuration needed for Reddit API interaction.

    This class is responsible for loading environment variables and returning a
    praw.Reddit instance configured with these variables.
    """

    def __init__(self, config_file: str) -> None:
        dotenv.load_dotenv()
        self.config = dotenv.dotenv_values(config_file)

    def get_client(self) -> praw.Reddit:
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
