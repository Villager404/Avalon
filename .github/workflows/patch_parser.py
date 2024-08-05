import re


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


def get_added_lines(hunk):
    lines = hunk['content'].split('\n')
    added_lines = []
    current_line = hunk['startLine2']

    for line in lines:
        if line.startswith('+'):
            added_lines.append((current_line, line[1:]))
            current_line += 1
        elif line.startswith(' '):
            current_line += 1

    return added_lines


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

# 예시 patch 데이터
input_patch = """@@ -132,7 +132,7 @@ module Test - line removed + line added  context line @@ -1000,7 +1000,7 @@ module AnotherTest - another line removed + another line added another context line"""

parsed_patch = parse_patch(input_patch)
for parsed_hunk in parsed_patch:
    print(parsed_hunk)
    added_lines = get_added_lines(parsed_hunk)
    added_ranges = get_added_line_ranges(parsed_hunk)
    print(added_ranges)
    for line_number, line_content in added_lines:
        print(f"Added line at {line_number}: {line_content}")