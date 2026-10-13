"""Validate this repository with Python 3.11+ and PyYAML; no network required."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md", "LICENSE", ".gitignore", ".gitattributes",
    ".github/workflows/validate.yml", "scripts/validate.py",
    "git-governance/SKILL.md", "git-governance/LICENSE",
    "git-governance/references/GIT_GOVERNANCE.md",
    "git-governance/adapters/cursor/git-branch-policy.mdc",
)


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate keys rather than silently accepting the last value."""


def mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ValueError(f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    require(match, f"{path.name}: missing or unclosed frontmatter")
    data = yaml.load(match.group(1), Loader=UniqueLoader)
    require(isinstance(data, dict), f"{path.name}: YAML must be a mapping")
    return data


def check_document(path):
    text = path.read_text(encoding="utf-8")
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            chars, rest = marker.groups()
            if fence is None:
                require(chars[0] != "`" or "`" not in rest,
                        f"{path.name}:{number}: invalid fence")
                fence = (chars[0], len(chars))
            elif chars[0] == fence[0] and len(chars) >= fence[1] and not rest.strip():
                fence = None
            continue
        if fence is not None:
            continue
        targets = re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", line)
        ref = re.match(r"^ {0,3}\[[^\]]+\]:\s*(\S+)", line)
        if ref:
            targets.append(ref.group(1))
        for target in targets:
            target = target.split()[0].strip("<>")
            if urlsplit(target).scheme or target.startswith("#"):
                continue
            resolved = (path.parent / unquote(urlsplit(target).path)).resolve()
            require(resolved.is_relative_to(ROOT) and resolved.exists(),
                    f"{path.name}:{number}: missing or external local link {target}")
    require(fence is None, f"{path.name}: unclosed Markdown fence")
    require(not re.search(r"(?i)(?:\b[a-z]:[\\/]|/(?:Users|home)/[^\s/]+/|\\\\[^\s\\]+\\)", text),
            f"{path.name}: machine-specific absolute path")


def main():
    for name in REQUIRED:
        require((ROOT / name).is_file(), f"Missing required file: {name}")
    skill_path = ROOT / "git-governance/SKILL.md"
    skill = frontmatter(skill_path)
    name = skill.get("name")
    require(isinstance(name, str) and len(name) <= 64 and
            re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name), "Invalid skill name")
    require(name == skill_path.parent.name, "Skill name must match directory")
    for key, data in (("Skill", skill), ("Cursor", frontmatter(ROOT / REQUIRED[-1]))):
        description = data.get("description")
        require(isinstance(description, str) and 0 < len(description.strip()) <= 1024,
                f"{key}: invalid description")
    cursor_path = ROOT / REQUIRED[-1]
    require(frontmatter(cursor_path).get("alwaysApply") is True, "Cursor: alwaysApply must be true")
    cursor = cursor_path.read_text(encoding="utf-8")
    refs = re.findall(r"^@([^\s]+)$", cursor, re.M)
    require(len(refs) == 2, "Cursor must reference entrypoint and complete rules")
    mapped = []
    for ref in refs:
        prefix = ".agents/skills/"
        require(ref.startswith(prefix), f"Unexpected Cursor install path: {ref}")
        source = (ROOT / ref.removeprefix(prefix)).resolve()
        require(source.is_relative_to(ROOT) and source.is_file(), f"Missing Cursor target: {ref}")
        mapped.append(source)
    require(set(mapped) == {skill_path, ROOT / REQUIRED[-2]}, "Wrong Cursor targets")
    policy = frontmatter(ROOT / REQUIRED[-2])
    require(str(policy.get("version")) == skill.get("metadata", {}).get("version") == "3.0.0",
            "Skill and policy versions must be 3.0.0")
    require((ROOT / "LICENSE").read_bytes() == (ROOT / "git-governance/LICENSE").read_bytes(),
            "Packaged license differs from root license")
    docs = [ROOT / "README.md", *sorted((ROOT / "git-governance").rglob("*.md")), cursor_path]
    for path in docs:
        check_document(path)
    yaml.load((ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8"), Loader=UniqueLoader)
    print(f"PASS: {len(REQUIRED)} required files; YAML, metadata, fences, links, Cursor targets, paths and licenses")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, yaml.YAMLError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
