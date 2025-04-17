#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AutoCommit
"""

import os
import random
import datetime
import subprocess
import json
import tempfile
from tabnanny import check


def main():
    print("Auto Commit Start...")
    config = load_config()
    valid_repos = check_repositories(config)

    if not valid_repos:
        print("No valid repo, check config.json")
        # Hunk 1
        #

        return

    for repo_path in valid_repos:
        git_status_results = git_status(repo_path)
        # Hunk 2
        #

        for result in git_status_results:

            if result[0] == "M ":
                # File is modified and staged (changes added to the index)
                if result[1].endswith('.py'):
                    total_diff, first_patch = get_staged_first_patch(repo_path, result[1])

                    git_restore_staged_file(repo_path, result[1])

                    git_apply_patch(repo_path, first_patch)

                    git_stash_push(repo_path, keep_index=True)
                    git_commit(repo_path, result[1], "First patch test.")
                    git_stash_pop(repo_path)

                    git_apply_patch(repo_path, total_diff)

            elif result[0] == " M":
                # File is modified but not staged (changes in working directory only)
                pass
            elif result[0] == "MM":
                # File is modified, some changes are staged and others are not staged
                if result[1].endswith('.py'):
                    total_diff, first_patch = get_staged_first_patch(repo_path, result[1])

                    git_restore_staged_file(repo_path, result[1])

                    git_apply_patch(repo_path, first_patch)

                    git_stash_push(repo_path, keep_index=True)
                    git_commit(repo_path, result[1], "First patch test.")
                    git_stash_pop(repo_path)

                    git_apply_patch(repo_path, total_diff)
            elif result[0] == "A ":
                # New file added to staging area
                pass
            elif result[0] == "R ":
                # File has been renamed in the staging area
                pass
            elif result[0] == "D ":
                # File is deleted in staging area
                pass
            elif result[0] == "C ":
                # File has been copied in staging area
                pass
            elif result[0] == "??":
                # Untracked file (not under version control yet)
                pass
            elif result[0] == "UU":
                # File has merge conflicts (both modified during merge)
                pass


def load_config(config_path="config.json"):
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            print("Config loaded")
            return config


    except FileNotFoundError:
        print(f"Config not found: {config_path}")

        default_config = {
            "repositories": [],
            "work_hours": {
                "start": "09:00",
                "end": "18:00"
            },
            "commits_per_day": {
                "min": 3,
                "max": 8
            }
        }
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
            print(f"Create default config: {config_path}")
            return config


def is_valid_git_repo(repo_path):
    git_dir = os.path.join(repo_path, ".git")
    return os.path.exists(git_dir) and os.path.isdir(git_dir)


def check_repositories(config):
    valid_repos = []
    for repo_path in config["repositories"]:
        if is_valid_git_repo(repo_path):
            print(f"Valid git repo: {repo_path}")
            valid_repos.append(repo_path)
        else:
            print(f"Invalid git repo: {repo_path}")

    return valid_repos


def git_status(repo_path):
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        result = result.stdout.strip('\n').split('\n')
        result = [[r[:2], r[3:]] for r in result]
        return result
    except subprocess.SubprocessError as e:
        print(f"Error in has_uncommitted_changes: {e}")
        return None


def git_add(repo_path, file_path):
    try:
        subprocess.run(
            ["git", "-C", repo_path, "add", file_path],
            check=True
        )
        print(f"Added to staging: {file_path}")
        return True
    except subprocess.SubprocessError as e:
        print(f"Error in git_add: {e}")
        return False


def git_commit(repo_path, file_path, message):
    try:
        command_args = ["git", "-C", repo_path, "commit"]
        if file_path:
            command_args.append(file_path)

        command_args.append(["-m", message])

        subprocess.run(
            command_args,
            check=True
        )
        print(f"Committed with message: {message}")
        return True
    except subprocess.SubprocessError as e:
        print(f"Error in git_commit: {e}")
        return False


def git_diff_staged(repo_path, file_path):
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "diff", "--staged", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.SubprocessError as e:
        print(f"Error in git_diff_cached: {e}")
        return None
    # hunk 3


def git_add_patch(repo_path, patch_content):
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(patch_content)
            temp_path = temp_file.name

        subprocess.run(
            ["git", "-C", repo_path, "apply", "--staged", temp_path],
            check=True
        )

        os.unlink(temp_path)
        return True
    except subprocess.SubprocessError as e:
        print(f"Error in git_add_patch: {e}")
        return False


def get_staged_first_patch(repo_path, python_files):
    diff_output = git_diff_staged(repo_path, python_files)
    diff_lines = diff_output.split("\n")
    is_first_hunk = True
    for i in range(len(diff_lines)):
        line = diff_lines[i]
        if line.startswith("@@"):
            if is_first_hunk:
                # TODO: Create Msg
                is_first_hunk = False
                pass
            else:
                diff_lines = diff_lines[:i]
                break

    return diff_output, "\n".join(diff_lines) + "\n"


def git_apply_patch(repo_path, patch_content):
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(patch_content)
            temp_path = temp_file.name

        subprocess.run(
            ["git", "-C", repo_path, "apply", "--cached", temp_path],
            check=True
        )
        os.unlink(temp_path)
        return True

    except subprocess.SubprocessError as e:
        print(f"Error in git_add_patch: {e}")
        return False


def git_restore_staged_file(repo_path, file_path):
    try:
        subprocess.run(
            ["git", "-C", repo_path, "restore", "--staged", file_path],
            check=True
        )
        print(f"Restored staged file: {file_path}")
        return True
    except subprocess.SubprocessError as e:
        print(f"Error in git_restore: {e}")
        return False


def git_stash_push(repo_path, keep_index=False):
    try:
        command_args = ["git", "-C", repo_path, "stash", "push"]
        if keep_index:
            command_args.append("--keep-index")

        subprocess.run(
            command_args,
            check=True
        )
        print("Saved working directory and index state WIP")
        return True

    except subprocess.SubprocessError as e:
        print(f"Error in git_stash_push: {e}")
        return False


def git_stash_pop(repo_path):
    try:
        command_args = ["git", "-C", repo_path, "stash", "pop"]

        subprocess.run(
            command_args,
            check=True
        )
        print("Git stash popped")
        return True

    except subprocess.SubprocessError as e:
        print(f"Error in git_stash_push: {e}")
        return False


if __name__ == "__main__":
    main()
