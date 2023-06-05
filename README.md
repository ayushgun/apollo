# Apollo User Guide

Apollo is a CLI and Python module that allows you to parse and extract bulk submission data from Reddit subreddits.

## Overview

Apollo is an effective tool that streamlines the process of interfacing with the Reddit API to fetch, parse, and extract valuable data from specified subreddits. The primary functionality involves retrieving submissions, and their associated metadata, from any subreddit based on various criteria.

It sends structured requests to Reddit's API endpoints, fetching data from the returned JSON response. This data includes important details of subreddit posts, such as the post ID, author, score, title, body content, URL, number of comments, and the top 10 comments.

This scraped data is then systematically parsed and transformed into data objects or dictionaries, depending on user preference. These organized data structures allow for simplified subsequent data analysis or processing.

Apollo also offers the capability of storing this data efficiently in different formats. Users have the flexibility to choose between JSON for structured data storage or plain text for simpler needs. By providing the option of output format, Apollo ensures compatibility with a variety of downstream applications or data analysis workflows.

## Features

- Search for posts in a subreddit containing a specific keyword.
- Retrieve top posts from the last 26 weeks of a specified subreddit.
- Fetch the top comments from the top posts of the last 26 weeks of a given subreddit.
- Save output data as a JSON file or dataclasses, based on your preference.

## Requirements

- Python 3.9 or higher
- Reddit application for API credentials (client id and client secret)

## Installation and Setup

1. Ensure that [Python 3.9](https://www.python.org/downloads/) or higher is installed on the machine.
2. Clone the repository with git clone `https://github.com/ayushgun/apollo`.
3. Create a Reddit application here. Save your `client id` & `secret`.
4. Input your Reddit application information in the .env configuration file. See the [example](#example-configuration) below.
5. Move to the Apollo directory with `cd src/apollo`
6. View the help menu with `python3 reddit.py --help`

## Example Configuration

```
client_id=YWcgWmkCtXdjNBoMOmom9D
client_secret=F9JKcHCdXrZNcv7K_KpEvErNJCjyfu
username=ayushgun
```

## Usage

Apollo provides a user-friendly command-line interface for interaction. You can perform three main tasks: keyword-search, top-posts, and top-comments. Check the command-line help for more detailed usage instructions.

```
python3 main.py --help
```

### Examples

#### Keyword Search

This command searches for posts in a subreddit that contain a specific keyword.

Example usage:

```bash
python3 reddit.py keyword-search "learnpython" "web scraping" --sorting "hot" --interval "week" --output "json"
```

This command will search for posts in the "learnpython" subreddit that contain the keyword "web scraping". The posts are sorted by "hot" and are from the past week. The output will be stored in a JSON file.

#### Top Posts

This command fetches the top posts from the last 26 weeks of a given subreddit.

Example usage:

```bash
python3 reddit.py top-posts "news" --output "dataclass"
```

This command will fetch the top posts from the past 26 weeks in the "news" subreddit. The output will be stored in a JSON file.

#### Top Comments

This command fetches the top comments from the top posts of the last 26 weeks of a given subreddit.

Example usage:

```bash
python3 reddit.py top-comments "AskReddit"
```

This command will fetch the top comments from the top posts of the past 26 weeks in the "AskReddit" subreddit. The output will be stored in a JSON file.

## Output

Apollo stores the output data with a unique filename in an output directory. The path to the output file is displayed on the console upon successful completion of the operation.

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/ayushgun/apollo/blob/main/LICENSE) file for details.
