import logging
import os
import requests
import zipfile
import shutil
from io import BytesIO
import tempfile

logger = logging.getLogger(__name__)

class SyncLink:
    def __init__(self, githubRepo: str = None, repoFolder: str = None, syncDir: str = None):
        self.githubRepo = githubRepo
        self.repoFolder = repoFolder
        self.syncDir = syncDir
        if not self.githubRepo:
            raise ValueError("GitHub repo must be specified e.g., 'TristanMcBrideSr/Sync'")
        if not self.repoFolder:
            raise ValueError("Repo folder must be specified e.g., 'your/path/Sync'")
        if not self.syncDir:
            raise ValueError("Sync dir must be specified e.g., '/your/path/sync'")


    def syncNewFiles(self, srcDir, dstDir, syncList=None, override=False):
        onlyFiles = None
        if syncList:
            normalized = set()
            for name in syncList:
                name = name.lower()
                normalized.add(name)
                if not name.endswith(".py"):
                    normalized.add(f"{name}.py")
            onlyFiles = normalized

        for root, dirs, files in os.walk(srcDir):
            relRoot = os.path.relpath(root, srcDir)
            targetRoot = os.path.join(dstDir, relRoot) if relRoot != '.' else dstDir
            os.makedirs(targetRoot, exist_ok=True)
            for file in files:
                if onlyFiles and file.lower() not in onlyFiles:
                    continue
                srcFile = os.path.join(root, file)
                dstFile = os.path.join(targetRoot, file)
                if os.path.exists(dstFile):
                    if override:
                        shutil.copy2(srcFile, dstFile)
                        logger.info(f"Overridden {dstFile} with {srcFile}")
                    else:
                        logger.info(f"File {dstFile} already exists locally. Skipping (preserving local).")
                    continue
                shutil.copy2(srcFile, dstFile)
                logger.info(f"Copied {srcFile} to {dstFile}")

    def startSync(self, **kwargs):
        """
        Syncs files from a GitHub repo zip to local directory.

        Kwargs:
            syncDir: str, local directory to sync to (overrides class default)
            syncList: list of files to sync (default: all)
            override: bool, if True always overwrite local (default: False)
            githubToken: str, GitHub token for private repos (default: None)
            branch: str, Git branch (default: 'master')
        """
        dstDir   = kwargs.get('syncDir') or self.syncDir
        syncList = kwargs.get('syncList')
        override = kwargs.get('override', False)
        ghToken  = kwargs.get('githubToken')
        branch   = kwargs.get('branch', 'master')

        logger.info(f"Starting {self.repoFolder} connection...")
        zipUrl = f"https://github.com/{self.githubRepo}/archive/refs/heads/{branch}.zip"
        logger.info("Starting sync...")
        logger.info(f"Downloading {zipUrl} ...")
        headers = {"User-Agent": "Mozilla/5.0"}
        if ghToken:
            headers["Authorization"] = f"Bearer {ghToken}"

        try:
            r = requests.get(zipUrl, headers=headers)
            r.raise_for_status()
            tempDir = tempfile.mkdtemp()
            try:
                z = zipfile.ZipFile(BytesIO(r.content))
                z.extractall(tempDir)
                extractedRoot = os.path.join(tempDir, os.listdir(tempDir)[0])
                skillsSrc = os.path.join(extractedRoot, self.repoFolder)

                if not os.path.exists(skillsSrc):
                    logger.error(f"Can't find {self.repoFolder} in the repo!")
                    raise FileNotFoundError(f"Can't find {self.repoFolder} in the repo!")

                os.makedirs(dstDir, exist_ok=True)
                self.syncNewFiles(skillsSrc, dstDir, syncList, override)
                logger.info("Sync complete.")
                return True
            finally:
                shutil.rmtree(tempDir)
        except Exception as e:
            logger.error(f"Sync failed: {e}", exc_info=True)
            return False
