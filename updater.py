import os
import sys
import git
import subprocess
import time

def main():
    # Path to the repository
    repo_path = os.path.dirname(os.path.abspath(__file__))
    repo_url = "https://github.com/juanzitos252/Mate2"

    try:
        # Try to open the repository
        repo = git.Repo(repo_path)
    except git.exc.InvalidGitRepositoryError:
        # If it's not a git repository, check if the directory is empty
        if not os.listdir(repo_path):
            # If it's empty, clone the repository
            repo = git.Repo.clone_from(repo_url, repo_path)
        else:
            # If it's not empty, initialize a new repository and fetch the code
            repo = git.Repo.init(repo_path)
            origin = repo.create_remote('origin', repo_url)
            origin.fetch()
            repo.git.reset('--hard', 'origin/main')

    # Fetch the latest changes from the remote repository
    origin = repo.remotes.origin
    origin.set_url(repo_url)
    origin.fetch()

    # Check if there are new commits
    if repo.head.commit != origin.refs.main.commit:
        print("Nova versão encontrada, atualizando...")

        # Close the main application
        # This is a placeholder, we'll need to find a way to close the pywebview app
        # For now, we'll assume it's closed and just replace the files

        # Stash local changes
        if repo.is_dirty(untracked_files=True):
            print("Stashing local changes...")
            repo.git.stash()

        # Pull the latest changes
        origin.pull()

        # Apply stashed changes
        try:
            print("Applying stashed changes...")
            repo.git.stash('pop')
        except git.exc.GitCommandError as e:
            if "No stash entries found" in str(e):
                print("No stashed changes to apply.")
            else:
                raise e

        # Restart the application
        subprocess.Popen([sys.executable, 'pywebview_main.py'])
        sys.exit()
    else:
        print("Nenhuma atualização encontrada.")

if __name__ == '__main__':
    main()
