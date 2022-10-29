<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <img src="https://i.imgur.com/1mtaJFe.png" alt="Logo" width="80" height="80">

<h3 align="center">Apollo</h3>

  <p align="center">
    A modular, typed, and explicit Python CLI for extracting and analyzing bulk submission data from Reddit communities.
    <br />
    <a href="https://ayushgun.github.io/apollo/reddit.html"><strong>Explore the API Docs »</strong></a>
    <br />
  </p>
</div>

<!-- GETTING STARTED -->

## Getting Started

To start using Apollo, please follow the following steps to beging the installation and setup process.

### Prerequisites

To install all of the dependencies for the project, run the following command.

```sh
pip3 install -3 requirements.txt
```

### Installation

1. Clone the repo.
   ```sh
   git clone https://github.com/ayushgun/apollo
   ```
2. CD into the scraper directory.
   ```sh
   cd ./apollo/scraper
   ```
3. Create a Reddit application [here](https://www.reddit.com/prefs/apps). Be sure to save your client ID & secret.
4. Input your application information in the `.env` configuration file.<br/>
   Example:
   ```
   client_id=YWcgWmkCtXdjNBoMOmom9D
   client_secret=F9JKcHCdXrZNcv7K_KpEvErNJCjyfu
   username=ayushgun
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

Use the help flag to view all CLI options and commands.

```sh
python3 reddit.py --help
```

To view command-specific help information, also use the help flag.

```sh
python3 reddit.py keyword_search --help
```

![image](https://user-images.githubusercontent.com/34173777/192132451-ffae8b5a-701b-42fb-bbdb-37e896ef6492.png)

The following commands are a sample command usages.

```
python3 reddit.py keyword_search r/stocks "NASDAQ" --sorting top --interval week
```

```
python3 reddit.py top_posts r/investing --output dataclass
```

The output flag has the options `dataclass` and `json`.

<br/>
⚠️ For option and API examples, please refer to the API documentation: https://ayushgun.github.io/apollo/reddit.html
