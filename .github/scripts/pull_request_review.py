import os
from typing import *
import requests
import re

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
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    return headers

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

def create_pull_request_reveiw(repo, pull_number, comments):
    url = f'https://api.github.com/repos/{repo}/pulls/{pull_number}/reviews'
    data = {
        'body': 'Ollama review the code.',
        'event': 'COMMENT',
        'comments': comments
    }

    response = requests.post(url, headers=get_header(), json=data)
    response.raise_for_status()
    return response.json()

def create_comment(file_path: str, parsed_hunk):
    return {
        'path': file_path,
        'body': 'lgtm',
        'position': parsed_hunk['last_pos']
    }

def parse_patch(patch):
    hunks = re.split(r'(@@ .*? @@)', patch)
    result = []

    last_pos = 0
    for i in range(1, len(hunks), 2):
        header = hunks[i]
        content = hunks[i + 1]

        # Hunk header 분석
        header_info = re.match(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@', header)
        if header_info:
            removed_start_line = int(header_info.group(1))
            removed_line_count = int(header_info.group(2))
            added_start_line = int(header_info.group(3))
            added_start_count = int(header_info.group(4))
            last_pos += len(content.split('\n'))

            hunk_info = {
                'header': header,
                'removed_start_line': removed_start_line,
                'removed_line_count': removed_line_count,
                'added_start_line': added_start_line,
                'added_start_count': added_start_count,
                'content': content,
                'last_pos': last_pos
            }
            result.append(hunk_info)

    return result

def review_pull_request(repo, pull_number):
    pull_request = get_pull_request(repo, pull_number)

    # Check if the pull request message contains "#review"
    if "#review" not in pull_request.get('body', ''):
        print("Pull request does not contain the review trigger.")
        return

    files = get_pull_request_files(repo, pull_number)

    comments = []
    for file in files:
        print (file['patch'])
        parsed_patch = parse_patch(file['patch'])
        for parsed_hunk in parsed_patch:
            comment = create_comment(file['filename'], parsed_hunk)
            print(comment)

            comments.append(comment)

    print(comments)
    create_pull_request_reveiw(repo, pull_number, comments)

if __name__ == "__main__":
    repo = os.getenv('GITHUB_REPOSITORY')
    pr_number = os.getenv('GITHUB_PR_NUMBER')
    token = os.getenv('GITHUB_TOKEN')
    print(token[:3])
    print(token[3:])

    review_pull_request(repo, pr_number)
