import os
from typing import *
import requests

PATCH_CONTENTS_DELIMETER = "@@"

class side_change_data:
    def __init__(self, start_line: int, end_line: int):
        self._start_line: int = start_line
        self._end_line: int = end_line

    @property
    def start_line(self) -> int:
        return self._start_line

    @property
    def end_line(self) -> int:
        return self._end_line

class patch_change:
    def __init__(self, name: str, contents: str,
                 l_data: side_change_data, r_data: side_change_data):
        self._name: str = name
        self._contents: str = contents
        self._left_change_data: side_change_data = l_data
        self._right_change_data: side_change_data = r_data

    @property
    def name(self) -> str:
        return self._name

    @property
    def contents(self) -> str:
        return self._contents

    @property
    def left_change_data(self) -> side_change_data:
        return self._left_change_data

    @property
    def right_change_data(self) -> side_change_data:
        return self._right_change_data

def get_header():
    # Headers for authentication
    token = os.getenv('GITHUB_TOKEN')
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

def get_pull_request(repo, pull_number):
    url = f'https://api.github.com/repos/{repo}/pulls/{pull_number}'
    response = requests.get(url, headers=get_header())
    response.raise_for_status()
    return response.json()


def get_pull_request_files(repo, pull_number):
    url = f'https://api.github.com/repos/{repo}/pulls/{pull_number}/files'
    response = requests.get(url, headers=get_header())
    response.raise_for_status()
    return response.json()


def create_review_comment(repo, pull_number, commit_id, path, position, body):
    url = f'https://api.github.com/repos/{repo}/pulls/{pull_number}/comments'
    data = {
        'commit_id': commit_id,
        'path': path,
        'position': position,
        'body': body
    }
    response = requests.post(url, headers=get_header(), json=data)
    response.raise_for_status()
    return response.json()


def review_pull_request(repo, pull_number):
    pull_request = get_pull_request(repo, pull_number)

    # Check if the pull request message contains "#ollama_review"
    if "#ollama_review" not in pull_request.get('body', ''):
        print("Pull request does not contain the review trigger.")
        return

    files = get_pull_request_files(repo, pull_number)

    for file in files:
        # Example: Add a review comment for each patch
        # Note: 'patch' contains the diff of the file changes
        for position, line in enumerate(file['patch'].split('\n')):
            comment_body = f'Review comment for line {position + 1}: Check this change.'
            create_review_comment(repo, pull_number, file['sha'], file['filename'], position + 1, comment_body)


if __name__ == "__main__":
    repo = os.getenv('GITHUB_REPOSITORY')
    pr_number = os.getenv('GITHUB_PR_NUMBER')
    token = os.getenv('GITHUB_TOKEN')

    review_pull_request(repo, pr_number)
