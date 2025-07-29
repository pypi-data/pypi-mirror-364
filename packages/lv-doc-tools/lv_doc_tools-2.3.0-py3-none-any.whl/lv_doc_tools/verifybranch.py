"""
This script is used to verify if the correct branch is checked out while running the lv_doc_tool
"""

import subprocess
import sys

# asciidoctor-pdf -a pdf-themedir=../../../lv_doc_tools/src/lv_doc_tools --theme  ../../../lv_doc_tools/src/lv_doc_tools/RS_theme.yml hitachi-testing.adoc


def verify_and_update_branch(expected_branch):
    """
    This method verifies if the correct branch is checked out 
    
    """
    # Check if inside a Git repo
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            stdout=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        print("🚫 Not a Git repository. Skipping Git checks.")
        return

    # Get current branch
    current_branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    # Check for uncommitted changes
    uncommitted = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
    ).stdout.strip()

    if current_branch != expected_branch:
        print(
            f"⚠️  You are on branch '{current_branch}', but expected '{expected_branch}'."
        )

        if uncommitted:
            print("✋ Uncommitted changes detected!")
            print(
                "🧹 Please commit or stash changes manually before switching branches."
            )
            print("🛑 Exiting to prevent data loss.")
            sys.exit(1)
        else:
            print(" Switching branches and pulling latest changes...")
            # subprocess.run(["git", "fetch", "origin"], check=True)
            subprocess.run(["git", "checkout", expected_branch], check=True)
            subprocess.run(["git", "pull", "origin", expected_branch], check=True)
    else:
        if uncommitted:
            print(
                "✋ You are on the correct branch, but there are uncommitted changes."
            )
            print("🧹 Please commit or stash them before running the tool.")
            sys.exit(1)
        else:
            print(
                f"✅ On correct branch '{expected_branch}'. Pulling latest changes..."
            )
            subprocess.run(["git", "pull", "origin", expected_branch], check=True)
