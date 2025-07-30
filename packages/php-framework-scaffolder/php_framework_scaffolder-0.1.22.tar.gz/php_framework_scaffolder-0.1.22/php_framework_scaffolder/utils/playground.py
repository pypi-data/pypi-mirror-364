from pathlib import Path
import tempfile
import uuid
import git

def create_playground(git_repository: Path):
    folder = Path(tempfile.mkdtemp(), "SpecPHP", uuid.uuid4())
    git.Repo.clone_from(git_repository, folder / "src")
    return folder