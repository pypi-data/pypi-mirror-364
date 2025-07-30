import platform
import os
import subprocess
from datetime import datetime
from pathlib import Path

def run_git_command(path: str, args: list[str]) -> str:
    result = subprocess.run(
        ["git"] + args,
        cwd=path,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Git command failed: {result.stderr.strip()}")
    return result.stdout.strip()

def is_git_repo(path: str) -> bool:
    try:
        output = run_git_command(path, ["rev-parse", "--is-inside-work-tree"])
        return output == "true"
    
    except RuntimeError:
        return False
    
def open_repo(path: str) -> None:
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise ValueError(f"Path does not exist: {resolved}")
    
    system = platform.system()

    try:
        if system == "Windows":
            os.startfile(str(resolved))
        elif system == "Darwin":
            subprocess.run(["open", str(resolved)], check=True)
        elif system == "Linux":
            subprocess.run(["xdg-open", str(resolved)], check=True)
    except subprocess.CalledProcessError:
        raise RuntimeError(f"Failed to open repository at {resolved}")
    
def get_recent_commits(path: str, count: int = 5) -> str:
    try:
        output = run_git_command(path, ["log", f"-n{count}", "--pretty=format:%C(yellow)%h %Cgreen%ad %Creset%s", "--date=short"])
        return output or "[dim]No commits found.[/dim]"
    except Exception as e:
        raise RuntimeError(f"Failed to fetch commits: {e}")
    
def diff_repo(path: str) -> str:
    return run_git_command(path, ["diff"])

def get_last_commit_date(path: str) -> datetime:
    output = run_git_command(path, ["log", "-1", "--format=%cI"])
    return datetime.fromisoformat(output.strip())

def get_detailed_repo_info(path: str) -> dict:
    path_obj = Path(path).expanduser().resolve()
    info = {
        "path": str(path_obj),
        "branch": "",
        "uncommitted": 0,
        "unpushed": 0,
        "needs_pull": False,
        "last_commit_hash": "",
        "last_commit_msg": "",
        "last_commit_author": "",
        "last_commit_date": "",
    }

    try:
        info["branch"] = run_git_command(path, ["rev-parse", "--abbrev-ref", "HEAD"])

        uncommitted_output = run_git_command(path, ["status", "--porcelain"])
        info["uncommitted"] = len(uncommitted_output.splitlines()) if uncommitted_output else 0
        
        try:
            unpushed = run_git_command(path, ["rev-list", "--count", "@{u}..HEAD"])
            info["unpushed"] = int(unpushed)
        except RuntimeError:
            info["unpushed"] = 0

        try:
            needs_pull = run_git_command(path, ["rev-list", "--count", "HEAD..@{u}"])
            info["needs_pull"] = int(needs_pull) > 0
        except RuntimeError:
            info["needs_pull"] = False

        try:
            log = run_git_command(path, ["log", "-1", "--pretty=format:%H%n%s%n%an%n%ad", "--date=short"])
            if log:
                lines = log.splitlines()
                if len(lines) >= 4:
                    info["last_commit_hash"] = lines[0]
                    info["last_commit_msg"] = lines[1]
                    info["last_commit_author"] = lines[2]
                    info["last_commit_date"] = lines[3]
        except RuntimeError:
            info["last_commit_msg"] = "N/A"
    except RuntimeError as e:
        info["error"] = str(e)
    
    return info
                    

def fetch_repo(path: str) -> None:
    try:
        run_git_command(path, ["fetch"])
    except RuntimeError as e:
        error_msg = str(e)
        if "Repository not found" in error_msg:
            raise ValueError(f"[red]✗ Remote repository not found for '{Path(path).name}'[/red]")
        else:
            raise ValueError(f"[red]✗ Fetch failed for '{Path(path).name}':[/red] {error_msg}")

def get_repo_status(path: str) -> dict:
    path_obj = Path(path).expanduser().resolve()
    status = {
        "path": Path(path).expanduser().resolve(),
        "branch": "",
        "uncommitted": 0,
        "unpushed": 0,
        "needs_pull": False
    }

    try:
        status["branch"] = run_git_command(path, ["rev-parse", "--abbrev-ref", "HEAD"])
        uncommitted_output = run_git_command(path, ["status", "--porcelain"])
        status["uncommitted"] = len(uncommitted_output.splitlines()) if uncommitted_output else 0

        try:
            unpushed = run_git_command(path, ["rev-list", "--count", "@{u}..HEAD"])
            status["unpushed"] = int(unpushed)
        except RuntimeError:
            status["unpushed"] = 0
        
        try:
            needs_pull = run_git_command(path, ["rev-list", "--count", "HEAD..@{u}"])
            status["needs_pull"] = int(needs_pull) > 0
        except RuntimeError:
            status["needs_pull"] = False

    except RuntimeError as e:
        status["error"] = str(e)

    return status