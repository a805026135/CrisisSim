"""文档处理模块：支持 PDF / TXT / DOCX 文件解析与分块"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DocumentChunk:
    content: str
    metadata: dict


CHUNK_SIZE = 500
CHUNK_OVERLAP = 80


class DocumentProcessor:
    """解析上传文件并切分为可索引的文本块"""

    @staticmethod
    def process(file_path: str | Path, filename: str | None = None) -> list[DocumentChunk]:
        path = Path(file_path)
        name = filename or path.name
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            text = DocumentProcessor._read_pdf(path)
        elif suffix == ".docx":
            text = DocumentProcessor._read_docx(path)
        elif suffix in (".txt", ".md", ".csv"):
            text = path.read_text(encoding="utf-8", errors="ignore")
        else:
            raise ValueError(f"不支持的文件格式: {suffix}")

        if not text.strip():
            return []

        return DocumentProcessor._split(text, source=name)

    @staticmethod
    def process_text(text: str, source: str = "manual_input") -> list[DocumentChunk]:
        """处理手动输入的文本"""
        if not text.strip():
            return []
        return DocumentProcessor._split(text, source=source)

    @staticmethod
    def _read_pdf(path: Path) -> str:
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            return "\n\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            return ""

    @staticmethod
    def _read_docx(path: Path) -> str:
        try:
            from docx import Document
            doc = Document(str(path))
            return "\n\n".join(para.text for para in doc.paragraphs if para.text.strip())
        except Exception:
            return ""

    @staticmethod
    def _split(text: str, source: str) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        start = 0
        while start < len(text):
            end = min(start + CHUNK_SIZE, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(DocumentChunk(
                    content=chunk_text,
                    metadata={"source": source, "chunk_id": len(chunks)},
                ))
            start += CHUNK_SIZE - CHUNK_OVERLAP
        return chunks
