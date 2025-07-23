import os
import sys
import git
import subprocess
import time

def main():
    # Path to the repository
    repo_path = os.path.dirname(os.path.abspath(__file__))
    repo_url = "https://github.com/juanzitos252/Mate2"

    # Fetch the latest changes from the remote repository
    try:
        repo = git.Repo(repo_path)
        origin = repo.remotes.origin
        origin.set_url(repo_url)
    except git.exc.InvalidGitRepositoryError:
        repo = git.Repo.clone_from(repo_url, repo_path)
        origin = repo.remotes.origin

    origin.fetch()

    # Check if there are new commits
    if repo.head.commit != origin.refs.main.commit:
        print("Nova versão encontrada, atualizando...")

        # Close the main application
        # This is a placeholder, we'll need to find a way to close the pywebview app
        # For now, we'll assume it's closed and just replace the files

        # Pull the latest changes
        origin.pull()

        # Restart the application
        subprocess.Popen([sys.executable, 'pywebview_main.py'])
        sys.exit()
    else:
        print("Nenhuma atualização encontrada.")

if __name__ == '__main__':
    main()
