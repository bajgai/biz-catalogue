#!/usr/bin/env python3
"""Fail closed before publishing files or history to this public repository.

This is a deliberately small local gate, supplemented by Gitleaks in CI.
It cannot determine whether arbitrary prose or source code is proprietary.
"""

import argparse
import hashlib
import json
import os
from pathlib import PurePosixPath
import re
import subprocess
import sys

POLICY = ".public-repo-policy.json"
MAX_BYTES = 256 * 1024
OID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
DENIED_DIRS = {
    "private", "data", "datasets", "exports", "export", "backups", "backup",
    "dumps", "dump", "secrets", "credentials", "local", ".scratch", ".agent",
    ".agents", ".claude", ".codex", ".cursor", ".opencode", ".pi", ".git",
    "node_modules", ".venv", "venv", "__pycache__",
}
DENIED_SUFFIXES = {
    ".db", ".sqlite", ".sqlite3", ".sql", ".dump", ".bak", ".backup",
    ".csv", ".tsv", ".jsonl", ".ndjson", ".parquet", ".avro", ".orc",
    ".arrow", ".feather", ".xls", ".xlsx", ".xlsm", ".ods", ".numbers",
    ".zip", ".gz", ".tgz", ".7z", ".rar", ".tar", ".bz2", ".xz",
    ".pem", ".key", ".p12", ".pfx", ".crt", ".cer", ".jks", ".keystore",
    ".pdf", ".doc", ".docx", ".pages", ".rdb", ".mdb", ".accdb",
}
JSON_MANIFESTS = {POLICY, "package.json", "package-lock.json", "tsconfig.json",
                  "jsconfig.json", "deno.json", "biome.json"}
SECRET_PATTERNS = [
    ("private-key", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----")),
    ("aws-key", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})\b")),
    ("provider-secret", re.compile(r"\bsk-(?:proj-|ant-[A-Za-z0-9-]*-)?[A-Za-z0-9_-]{20,}\b")),
    ("stripe-secret", re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{15,}\b")),
    ("google-key", re.compile(r"\bAIza[A-Za-z0-9_-]{35}\b")),
    ("google-client-secret", re.compile(r"\bGOCSPX-[A-Za-z0-9_-]{20,}\b")),
    ("supabase-secret", re.compile(r"\bsb_secret_[A-Za-z0-9_-]{20,}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("service-account", re.compile(r'''["']type["']\s*:\s*["']service_account["']''')),
    ("credential-url", re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s/@:]+:[^\s/@]+@", re.I)),
]
KEY_NAME = r"(?:[A-Za-z0-9]+[_-])*(?:api[_-]?key|password|passwd|secret|token|authorization|connection[_-]?string)(?:[_-][A-Za-z0-9]+)*"
QUOTED_CREDENTIAL = re.compile(
    r'''(?<![\w-])["']?(?:''' + KEY_NAME + r''')["']?\s*[:=]\s*(["'])([^\r\n]*?)\1''', re.I
)
BARE_CREDENTIAL = re.compile(
    r"^[ \t]*(?:export[ \t]+)?(?:" + KEY_NAME + r")[ \t]*[:=][ \t]*([^\r\n]*)$", re.I | re.M
)


class GuardError(Exception):
    pass


def git(*args):
    env = dict(os.environ, GIT_NO_REPLACE_OBJECTS="1", GIT_OPTIONAL_LOCKS="0")
    result = subprocess.run(["git", *args], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env, check=False)
    if result.returncode:
        # Git errors can contain a secret supplied as a ref or filename.
        raise GuardError("Git operation failed; inspect repository state locally")
    return result.stdout


def placeholder(value):
    return (not value or bool(re.fullmatch(r"(?:YOUR|EXAMPLE)_[A-Z0-9_]+", value))
            or bool(re.fullmatch(r"\$\{[A-Za-z_][A-Za-z0-9_]*\}", value))
            or bool(re.fullmatch(r"\$\{\{\s*(?:secrets|github|env|vars)\.[A-Za-z_][A-Za-z0-9_]*\s*\}\}", value)))


def content_categories(raw, path=""):
    if len(raw) > MAX_BYTES:
        return {"oversized-file"}
    if b"\x00" in raw:
        return {"binary-file"}
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        return {"non-utf8-file"}
    found = {name for name, pattern in SECRET_PATTERNS if pattern.search(content)}
    for match in QUOTED_CREDENTIAL.finditer(content):
        if not placeholder(match.group(2)):
            found.add("hardcoded-credential")
    for match in BARE_CREDENTIAL.finditer(content):
        value = match.group(1).strip().split(" #", 1)[0]
        if value.startswith(("'", '"')):
            continue  # The quoted detector handles literal values.
        name = PurePosixPath(path).name.casefold()
        strict_config = name.startswith(".env") or name.endswith((".yaml", ".yml", ".toml", ".ini", ".conf"))
        expression = any(c in value for c in "()[]{};,")
        if not placeholder(value) and (strict_config or not expression):
            found.add("hardcoded-credential")
    return found


def path_categories(path, mode, allowed):
    found = set()
    if content_categories(path.encode("utf-8", errors="surrogateescape")):
        found.add("credential-or-invalid-content-in-path")
    if path not in allowed:
        found.add("path-not-approved")
    pure = PurePosixPath(path)
    parts = tuple(part.casefold() for part in pure.parts)
    name = parts[-1] if parts else ""
    if any(part in DENIED_DIRS for part in parts[:-1]):
        found.add("private-or-local-directory")
    if name.startswith(".env") and name != ".env.example":
        found.add("environment-file")
    if (any(suffix in DENIED_SUFFIXES for suffix in PurePosixPath(name).suffixes)
            or re.search(r"\.(?:db|sqlite3?)-(?:wal|shm|journal)$", name)
            or name in {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", ".netrc", ".npmrc", ".pypirc", ".gitleaksignore"}):
        found.add("sensitive-data-or-key-file")
    if name.endswith(".json") and name not in JSON_MANIFESTS and not re.fullmatch(r"tsconfig\.[a-z0-9_-]+\.json", name):
        found.add("non-manifest-json-data")
    if mode not in {"100644", "100755"}:
        found.add("symlink-submodule-or-special-file")
    if (not path or pure.is_absolute() or ".." in pure.parts
            or "\\" in path or any(ord(char) < 32 for char in path)):
        found.add("unsafe-path")
    return found


def load_policy(raw):
    if len(raw) > MAX_BYTES:
        raise GuardError("Public policy exceeds size limit")
    try:
        policy = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise GuardError("Public policy is not valid UTF-8 JSON") from None
    if (not isinstance(policy, dict) or set(policy) != {"version", "public_paths"}
            or type(policy["version"]) is not int or policy["version"] != 1
            or not isinstance(policy["public_paths"], list)
            or not all(isinstance(path, str) and path for path in policy["public_paths"])):
        raise GuardError("Public policy must contain version 1 and an exact public_paths list")
    paths = policy["public_paths"]
    if len(paths) != len(set(paths)) or POLICY not in paths:
        raise GuardError("Public policy has duplicate paths or does not approve itself")
    for path in paths:
        if any(char in path for char in "*?[") or path_categories(path, "100644", set(paths)):
            raise GuardError("Public policy contains an unsafe or prohibited path")
    return set(paths)


class Guard:
    def __init__(self, allowed):
        self.allowed = allowed
        self.findings = set()
        self.blobs = {}

    def check_content(self, path, raw):
        for category in content_categories(raw, path):
            self.findings.add((path, category))

    def check_entry(self, path, mode, oid):
        for category in path_categories(path, mode, self.allowed):
            self.findings.add((path, category))
        if mode not in {"100644", "100755"}:
            return
        cache_key = (oid, PurePosixPath(path).name)
        if cache_key not in self.blobs:
            size = int(git("cat-file", "-s", oid))
            self.blobs[cache_key] = ({"oversized-file"} if size > MAX_BYTES
                                    else content_categories(git("cat-file", "blob", oid), path))
        for category in self.blobs[cache_key]:
            self.findings.add((path, category))

    def check_tree(self, tree):
        for record in git("ls-tree", "-rz", "--full-tree", tree).split(b"\0"):
            if record:
                metadata, name = record.split(b"\t", 1)
                mode, _, oid = metadata.decode("ascii").split()
                path = name.decode("utf-8", errors="surrogateescape")
                self.check_entry(path, mode, oid)

    def history(self, refs):
        if git("rev-parse", "--is-shallow-repository").strip() != b"false":
            raise GuardError("History scan requires a complete clone (fetch-depth: 0)")
        if not refs:
            refs = git("for-each-ref", "--format=%(refname)").decode().splitlines()
            try:
                refs.append(git("rev-parse", "--verify", "HEAD").decode().strip())
            except GuardError:
                pass  # An unborn repository has no HEAD.
        policies = {}
        tags = set()
        for ref in refs:
            if not ref or ref.startswith("-"):
                raise GuardError("Invalid history reference")
            if content_categories(ref.encode()):
                raise GuardError("Credential detected in history reference name")
            oid = git("rev-parse", "--verify", "--end-of-options", ref).decode().strip()
            if not OID.fullmatch(oid):
                raise GuardError("Invalid resolved object identifier")
            while True:
                kind = git("cat-file", "-t", oid).strip()
                if kind == b"commit":
                    record = git("ls-tree", "-z", oid, "--", POLICY).rstrip(b"\0")
                    if not record:
                        raise GuardError("Every published tip must contain a public policy")
                    metadata, _ = record.split(b"\t", 1)
                    mode, kind, policy_oid = metadata.decode("ascii").split()
                    if mode != "100644" or kind != "blob":
                        raise GuardError("Published tip policy must be a regular file")
                    if int(git("cat-file", "-s", policy_oid)) > MAX_BYTES:
                        raise GuardError("Public policy exceeds size limit")
                    allowed = frozenset(load_policy(git("cat-file", "blob", policy_oid)))
                    policies.setdefault(allowed, []).append(oid)
                    break
                if kind != b"tag":
                    raise GuardError("Public refs must resolve to commits, not standalone trees or blobs")
                if oid in tags:
                    break
                tags.add(oid)
                raw = git("cat-file", "tag", oid)
                headers, _, _ = raw.partition(b"\n\n")
                self.check_content("<tag-metadata-and-message>", raw)
                oid = headers.splitlines()[0].removeprefix(b"object ").decode("ascii")
                if not OID.fullmatch(oid):
                    raise GuardError("Invalid annotated tag target")
        for allowed, commits in policies.items():
            self.allowed = allowed
            trees = set()
            for commit in git("rev-list", *sorted(set(commits)), "--").splitlines():
                raw = git("cat-file", "commit", commit.decode())
                headers, _, _ = raw.partition(b"\n\n")
                self.check_content("<commit-metadata-and-message>", raw)
                tree = headers.splitlines()[0].removeprefix(b"tree ").decode("ascii")
                if not OID.fullmatch(tree):
                    raise GuardError("Invalid commit tree")
                if tree not in trees:
                    trees.add(tree)
                    self.check_tree(tree)

    def report(self):
        for path, category in sorted(self.findings):
            encoded_path = path.encode("utf-8", errors="surrogateescape")
            shown_path = ("<redacted-path-" + hashlib.sha256(encoded_path).hexdigest()[:12] + ">"
                          if content_categories(encoded_path) else path)
            print(f"BLOCKED {json.dumps(shown_path, ensure_ascii=True)}: {category}", file=sys.stderr)
        if self.findings:
            print("Public repository guard failed. No secret values are printed.", file=sys.stderr)
            return 1
        print("Public repository guard passed.")
        return 0


def staged():
    entries = []
    policy_oid = None
    for record in git("ls-files", "--stage", "-z").split(b"\0"):
        if record:
            metadata, name = record.split(b"\t", 1)
            mode, oid, stage = metadata.decode("ascii").split()
            if stage != "0":
                raise GuardError("Unmerged index entries must be resolved before publication")
            path = name.decode("utf-8", errors="surrogateescape")
            entries.append((path, mode, oid))
            if path == POLICY and mode == "100644":
                policy_oid = oid
    if policy_oid is None:
        raise GuardError("Stage a regular public policy file before committing")
    if int(git("cat-file", "-s", policy_oid)) > MAX_BYTES:
        raise GuardError("Public policy exceeds size limit")
    guard = Guard(load_policy(git("cat-file", "blob", policy_oid)))
    for entry in entries:
        guard.check_entry(*entry)
    return guard.report()


def push_refs():
    refs = []
    for line in sys.stdin:
        fields = line.split()
        if len(fields) != 4:
            raise GuardError("Malformed pre-push input")
        local_ref, local_oid, remote_ref, remote_oid = fields
        if content_categories(local_ref.encode()) or content_categories(remote_ref.encode()):
            raise GuardError("Credential detected in outgoing reference name")
        if (not OID.fullmatch(local_oid) or not OID.fullmatch(remote_oid)
                or len(local_oid) != len(remote_oid)
                or not remote_ref.startswith("refs/")
                or local_ref.startswith("-")):
            raise GuardError("Invalid pre-push reference input")
        if set(local_oid) != {"0"}:
            refs.append(local_oid)
    return refs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--staged", action="store_true", help="scan the entire staged snapshot (default)")
    modes.add_argument("--history", nargs="*", metavar="REF", help="scan complete histories; default all refs and HEAD")
    modes.add_argument("--pre-push", action="store_true", help="read Git pre-push hook input from stdin")
    args = parser.parse_args()
    try:
        root = git("rev-parse", "--show-toplevel").decode().strip()
        os.chdir(root)
        if args.history is None and not args.pre_push:
            return staged()
        guard = Guard(set())
        refs = push_refs() if args.pre_push else args.history
        if args.pre_push and not refs:
            return guard.report()  # Deletions or a no-op push contain no new objects.
        guard.history(refs)
        return guard.report()
    except (GuardError, OSError, ValueError, UnicodeError) as error:
        message = str(error) if isinstance(error, GuardError) else "Unable to complete the public repository scan"
        print(f"BLOCKED: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
