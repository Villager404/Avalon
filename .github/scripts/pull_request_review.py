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

def create_comment(file_path, range):
    return {
        'path': file_path,
        'body': 'lgtm',
        'start_line': range[0],
        'line': range[1],
        'start_side': 'RIGHT',
        'side': 'RIGHT'
    }

def parse_patch(patch):
    hunks = re.split(r'(@@ .*? @@)', patch)
    result = []

    for i in range(1, len(hunks), 2):
        header = hunks[i]
        content = hunks[i + 1]

        # Hunk header 분석
        header_info = re.match(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@', header)
        if header_info:
            start_line1 = int(header_info.group(1))
            count1 = int(header_info.group(2))
            start_line2 = int(header_info.group(3))
            count2 = int(header_info.group(4))

            hunk_info = {
                'header': header,
                'startLine1': start_line1,
                'count1': count1,
                'startLine2': start_line2,
                'count2': count2,
                'content': content
            }
            result.append(hunk_info)

    return result

def get_added_line_ranges(hunk):
    lines = hunk['content'].split('\n')
    added_ranges = []
    current_line = hunk['startLine2']
    range_start = None

    for line in lines:
        if line.startswith('+'):
            if range_start is None:
                range_start = current_line
            current_line += 1
        elif line.startswith(' '):
            if range_start is not None:
                added_ranges.append((range_start, current_line - 1))
                range_start = None
            current_line += 1
        elif line.startswith('-'):
            continue

    if range_start is not None:
        added_ranges.append((range_start, current_line - 1))

    return added_ranges

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
            added_ranges = get_added_line_ranges(parsed_hunk)
            print(added_ranges)
            for added_range in added_ranges:
                comment = create_comment(file['filename'], added_range)
                print(comment)
                comments.append(comment)

    print(comments)
    create_pull_request_reveiw(repo, pull_number, comments)

if __name__ == "__main__":
    repo = os.getenv('GITHUB_REPOSITORY')
    pr_number = os.getenv('GITHUB_PR_NUMBER')
    token = os.getenv('GITHUB_TOKEN')

    review_pull_request(repo, pr_number)
