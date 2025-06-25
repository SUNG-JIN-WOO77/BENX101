# Copyright (C) 2025 by Alexa_Help @ Github, < https://github.com/TheTeamAlexa >
# Subscribe On YT < Jankari Ki Duniya >. All rights reserved. © Alexa © Yukki.

"""
TheTeamAlexa is a project of Telegram bots with variety of purposes.
Copyright (c) 2021 ~ Present Team Alexa <https://github.com/TheTeamAlexa>

This program is free software: you can redistribute it and can modify
as you want or you can collabe if you have new ideas.
"""


import asyncio
import os
import shlex
from typing import Tuple

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

import config
from ..logging import LOGGER


def install_req(cmd: str) -> Tuple[str, str, int, int]:
    async def install_requirements():
        args = shlex.split(cmd)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", "replace").strip(),
            stderr.decode("utf-8", "replace").strip(),
            process.returncode,
            process.pid,
        )

    return asyncio.get_event_loop().run_until_complete(install_requirements())


def git():
    REPO_LINK = config.UPSTREAM_REPO

    # Format the repo URL if token is present
    if config.GIT_TOKEN:
        GIT_USERNAME = REPO_LINK.split("com/")[1].split("/")[0]
        TEMP_REPO = REPO_LINK.split("https://")[1]
        UPSTREAM_REPO = f"https://{GIT_USERNAME}:{config.GIT_TOKEN}@{TEMP_REPO}"
    else:
        UPSTREAM_REPO = config.UPSTREAM_REPO

    # Skip git operations if no .git directory exists (common in Railway/Heroku)
    if not os.path.exists(".git"):
        LOGGER(__name__).info("No .git directory found. Skipping git sync.")
        return

    try:
        repo = Repo()
        LOGGER(__name__).info("Git Client Found [VPS DEPLOYER]")
    except (GitCommandError, InvalidGitRepositoryError):
        LOGGER(__name__).warning("Invalid Git repository. Skipping git sync.")
        return

    try:
        origin = repo.remote("origin")
    except ValueError:
        origin = repo.create_remote("origin", UPSTREAM_REPO)

    try:
        origin.fetch()
        repo.create_head(
            config.UPSTREAM_BRANCH,
            origin.refs[config.UPSTREAM_BRANCH],
        )
        repo.heads[config.UPSTREAM_BRANCH].set_tracking_branch(
            origin.refs[config.UPSTREAM_BRANCH]
        )
        repo.heads[config.UPSTREAM_BRANCH].checkout(True)
        origin.pull(config.UPSTREAM_BRANCH)
        install_req("pip3 install --no-cache-dir -r requirements.txt")
        LOGGER(__name__).info(f"Fetched Updates from: {REPO_LINK}")
    except GitCommandError as e:
        LOGGER(__name__).warning(f"Git fetch/pull error: {e}")
