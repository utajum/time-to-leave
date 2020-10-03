import sys
import re

# Global settings
g_prefix_line = '-   '
g_begin_changes = '<!--- Begin changes - Do not remove -->'
g_end_changes = '<!--- End changes - Do not remove -->'
g_begin_users = '<!--- Begin users - Do not remove -->'
g_end_users = '<!--- End users - Do not remove -->'

def remove_prefix(text, prefix):
    return re.sub(r'^{0}'.format(re.escape(prefix)), '', text)

def clean_line(line):
    return remove_prefix(line.strip(), g_prefix_line)

def get_sorted_unique_entries(entries):
    entries = list(set(entries))
    entries.sort()
    return ['{}{}'.format(g_prefix_line, entry) for entry in entries]

def get_updated_file_content(current_changelog_lines, new_change, new_user):
    new_file_content = []
    is_sourcing_changes = False
    is_sourcing_users = False
    changes = [new_change]
    users = [new_user]

    for line in current_changelog_lines:
        line = clean_line(line)
        if line == g_end_changes:
            is_sourcing_changes = False
            new_file_content.extend(get_sorted_unique_entries(changes))

        if line == g_end_users:
            is_sourcing_users = False
            new_file_content.extend(get_sorted_unique_entries(users))

        if not is_sourcing_changes and not is_sourcing_users:
            new_file_content.append(line)

        if is_sourcing_changes:
            changes.append(line)

        if is_sourcing_users:
            users.append(line)

        if line == g_begin_changes:
            is_sourcing_changes = True

        if line == g_begin_users:
            is_sourcing_users = True

    return new_file_content

def update_changelog(changelog_filename, new_change, new_user):
    new_file_content = []
    with open(changelog_filename) as file_handler:
        lines = file_handler.readlines()
        new_file_content = get_updated_file_content(lines, new_change, new_user)

    with open(changelog_filename, "w") as file_handler:
        file_handler.write('\n'.join(new_file_content))

# Parses a comment that must follow the strict rule of being:
# \changelog-update
# Message: <some one line message here>
# User: <some user name here>
argv = sys.argv[1:]
changelog_filename = argv[0]
comment_body_filename = argv[1]

with open(comment_body_filename) as file_handler:
    lines = file_handler.readlines()
    message = remove_prefix(lines[1].strip(), "Message: ")
    user = remove_prefix(lines[2].strip(), "User: ")
    update_changelog(changelog_filename, message, user)
