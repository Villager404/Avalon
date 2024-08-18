import os
import requests
import re
import pathlib
import llama_review

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

def create_pull_request_reveiw(repo, pull_number, file_name, comments):
    url = f'https://api.github.com/repos/{repo}/pulls/{pull_number}/reviews'
    data = {
        'body': f'AI review the code about {file_name}.',
        'event': 'COMMENT',
        'comments': comments
    }

    response = requests.post(url, headers=get_header(), json=data)
    response.raise_for_status()
    return response.json()

def create_description_comment(file_path: str, parsed_hunk):
    review = llama_review.review_code_for_description(parsed_hunk['content'])

    return {
        'path': file_path,
        'body': review,
        'position': parsed_hunk['num_lines'] - 1
    }

def create_correctness_comment(file_path: str, parsed_hunk):
    review = llama_review.review_code_for_correctness(parsed_hunk['content'])

    return {
        'path': file_path,
        'body': review,
        'position': parsed_hunk['num_lines'] - 1
    }

def create_maintainability_comment(file_path: str, parsed_hunk):
    review = llama_review.review_code_for_maintainability(parsed_hunk['content'])

    return {
        'path': file_path,
        'body': review,
        'position': parsed_hunk['num_lines'] - 1
    }

def parse_patch(patch):
    hunks = re.split(r'(@@ .*? @@)', patch)
    result = []

    num_lines = 0
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
            num_lines += len(content.splitlines())

            hunk_info = {
                'header': header,
                'removed_start_line': removed_start_line,
                'removed_line_count': removed_line_count,
                'added_start_line': added_start_line,
                'added_start_count': added_start_count,
                'content': content,
                'num_lines': num_lines
            }
            result.append(hunk_info)

    return result

def is_target_language_file(file_name):
    dot_extension = pathlib.Path(file_name).suffix
    if (dot_extension == ".cs"  # C#
        or dot_extension == ".cpp"  # CPP
        or dot_extension == ".py"):  # Python
        return True
    return False

def review_pull_request(repo, pull_number):
    pull_request = get_pull_request(repo, pull_number)

    # Check if the pull request message contains "#review"
    if "#review" not in pull_request.get('body', ''):
        print("Pull request does not contain the review trigger.")
        return

    files = get_pull_request_files(repo, pull_number)


    for file in files:
        if not is_target_language_file(file['filename']):
            continue

        parsed_patch = parse_patch(file['patch'])
        comments = []
        for parsed_hunk in parsed_patch:
            comments.append(create_description_comment(file['filename'], parsed_hunk))
            comments.append(create_correctness_comment(file['filename'], parsed_hunk))
            comments.append(create_maintainability_comment(file['filename'], parsed_hunk))

        create_pull_request_reveiw(repo, pull_number, file['filename'], comments)

if __name__ == "__main__":
    repo = os.getenv('GITHUB_REPOSITORY')
    pr_number = os.getenv('GITHUB_PR_NUMBER')
    token = os.getenv('GITHUB_TOKEN')

    review_pull_request(repo, pr_number)
