from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Optional

from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.util import ClassNotFound
from textual.widgets import Markdown

from .git_status_sidebar import Hunk


@dataclass(slots=True)
class DiffMarkdownConfig:
    """Configuration for how a diff hunk should be rendered."""

    repo_root: Path
    wrap: bool = False
    prefer_diff_language: bool = False
    code_block_theme: str = "monokai"
    show_headers: bool = False


class DiffMarkdown(Markdown):
    """Markdown widget specialised for unified diff hunks with syntax highlighting.

    The widget converts hunk headers and line payloads into a fenced Markdown block.
    It attempts to strike a balance between diff semantics (+/- context) and
    per-language syntax highlighting by dynamically picking an appropriate lexer.
    """

    DEFAULT_CSS = """
    DiffMarkdown {
        background: transparent;
        border: none;
    }
    """

    def __init__(
        self,
        file_path: str,
        hunks: Iterable[Hunk],
        *,
        config: Optional[DiffMarkdownConfig] = None,
    ) -> None:
        self._file_path = file_path
        self._config = config or DiffMarkdownConfig(repo_root=Path.cwd())
        self._hunks_cache = list(hunks)
        markdown_text = self._build_markdown(self._hunks_cache)
        super().__init__(markdown_text)
        if hasattr(self, "inline_code_theme"):
            self.inline_code_theme = self._config.code_block_theme

    def _build_markdown(self, hunks: List[Hunk]) -> str:
        """Construct the Markdown payload that encodes diff and syntax info."""
        header_lines: List[str] = ["<!-- Tentacle DiffMarkdown -->"]

        if not hunks:
            return "\n".join(header_lines + ["_No changes to display._"])

        language = self._detect_language()
        fence_language = "diff" if self._config.prefer_diff_language else language or "diff"

        for hunk in hunks:
            if self._config.show_headers:
                header_lines.append(f"### `{hunk.header or 'File contents'}`")
            header_lines.append(self._render_hunk_block(hunk, fence_language))

        return "\n\n".join(header_lines)

    def _render_hunk_block(self, hunk: Hunk, fence_language: str) -> str:
        """Render a single hunk of diff lines inside a fenced Markdown block."""
        fence_lines: List[str] = [f"```{fence_language}"]
        for line in hunk.lines:
            fence_lines.append(self._normalise_line(line))
        fence_lines.append("```")
        return "\n".join(fence_lines)

    def _normalise_line(self, line: str) -> str:
        """Ensure markdown is well-formed while preserving diff semantics."""
        if not line:
            return ""

        escaped = line.replace("```", "`\u200b``")
        return escaped

    def _detect_language(self) -> Optional[str]:
        """Best-effort inference of the target language for syntax highlighting."""
        file_path = self._file_path
        full_path = self._config.repo_root / file_path

        try:
            lexer = _get_cached_lexer(str(full_path))
            return lexer.aliases[0] if lexer.aliases else lexer.name.lower()
        except ClassNotFound:
            pass
        except FileNotFoundError:
            pass

        sample = self._collect_sample()
        if not sample:
            return None

        try:
            lexer = guess_lexer(sample)
            return lexer.aliases[0] if lexer.aliases else lexer.name.lower()
        except ClassNotFound:
            return None

    def _collect_sample(self) -> str:
        """Gather a short sample of code from the hunks to feed into pygments."""
        snippets: List[str] = []
        for hunk in self._hunks_cache:
            for line in hunk.lines:
                if line and line[:1] in {"+", "-", " "}:
                    snippets.append(line[1:])
                else:
                    snippets.append(line)
                if len("\n".join(snippets)) > 2048:
                    break
            if len("\n".join(snippets)) > 2048:
                break
        return "\n".join(snippets)


@lru_cache(maxsize=128)
def _get_cached_lexer(file_path: str):
    return get_lexer_for_filename(file_path)
