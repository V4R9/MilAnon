"""EML parser — parses .eml files into ExtractedDocument using Python's email stdlib."""

from __future__ import annotations

import email
import email.header
import email.message
import email.utils
import html
import re
from pathlib import Path

from milanon.domain.entities import DocumentFormat, ExtractedDocument

_HEADER_FIELDS = ("From", "To", "Cc", "Bcc", "Subject", "Date")
_INLINE_IMAGE_TYPES = ("image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff")


class EmlParser:
    """Parses RFC 2822 .eml files into ExtractedDocument.

    Handles:
    - Content-Transfer-Encoding: quoted-printable and base64 (via get_payload(decode=True))
    - multipart/alternative: prefers text/plain over text/html
    - multipart/mixed: extracts text parts, skips file attachments
    - Nested multipart (forwarded/replied emails)
    - RFC 2047 encoded header values (=?charset?B|Q?text?=)
    """

    def parse(self, path: Path) -> ExtractedDocument:
        """Parse an .eml file and return its extracted content."""
        raw = path.read_bytes()
        msg = email.message_from_bytes(raw)

        headers = self._extract_headers(msg)
        display_names = self._extract_display_names(msg)
        if display_names:
            headers["display_names"] = display_names
        body, image_count = self._extract_body(msg)
        text_content = self._build_text_content(headers, body)

        return ExtractedDocument(
            source_path=str(path),
            format=DocumentFormat.EML,
            text_content=text_content,
            metadata=headers,
            embedded_image_count=image_count,
        )

    def supported_extensions(self) -> list[str]:
        """Return file extensions this parser handles."""
        return [".eml"]

    def _extract_display_names(self, msg: email.message.Message) -> list[str]:
        """Extract person display names from From/To/Cc/Bcc headers.

        Uses email.utils.getaddresses() to parse RFC 2822 address fields.
        Only includes names that look like person names (contain a space,
        i.e. firstname + lastname). Single-word names (likely company names
        like "Swisscom") are excluded.
        """
        names: list[str] = []
        for field in ("from", "to", "cc", "bcc"):
            raw = msg.get(field)
            if not raw:
                continue
            decoded = self._decode_header_value(raw)
            for display_name, addr in email.utils.getaddresses([decoded]):
                display_name = display_name.strip()
                if (
                    display_name and display_name != addr
                    and " " in display_name and display_name not in names
                ):
                    names.append(display_name)
        return names

    def _extract_headers(self, msg: email.message.Message) -> dict:
        """Extract and decode standard RFC 2822 header fields."""
        result: dict[str, str] = {}
        for field in _HEADER_FIELDS:
            raw_value = msg.get(field)
            if raw_value:
                result[field.lower()] = self._decode_header_value(raw_value)
        return result

    def _decode_header_value(self, raw_value: str) -> str:
        """Decode RFC 2047 encoded header values (=?charset?B|Q?text?=)."""
        parts: list[str] = []
        for chunk, charset in email.header.decode_header(raw_value):
            if isinstance(chunk, bytes):
                # Fall back to utf-8 for unknown/missing charset labels
                effective_charset = charset or "utf-8"
                if effective_charset.lower() in ("unknown-8bit", "unknown"):
                    effective_charset = "utf-8"
                parts.append(chunk.decode(effective_charset, errors="replace"))
            else:
                parts.append(str(chunk))
        return "".join(parts)

    def _extract_body(self, msg: email.message.Message) -> tuple[str, int]:
        """Extract body text and count inline images. Returns (body_text, image_count)."""
        if msg.is_multipart():
            return self._extract_from_multipart(msg)
        return self._decode_part(msg), 0

    def _extract_from_multipart(
        self, msg: email.message.Message
    ) -> tuple[str, int]:
        """Walk multipart message, prefer text/plain, count inline images."""
        plain_parts: list[str] = []
        html_parts: list[str] = []
        image_count = 0

        for part in msg.walk():
            if part.is_multipart():
                continue

            content_type = part.get_content_type()
            disposition = (part.get_content_disposition() or "").lower()

            if content_type in _INLINE_IMAGE_TYPES:
                image_count += 1
                continue

            if disposition == "attachment":
                continue

            if content_type == "text/plain":
                plain_parts.append(self._decode_part(part))
            elif content_type == "text/html":
                html_parts.append(self._decode_part(part))

        if plain_parts:
            return "\n".join(plain_parts), image_count
        if html_parts:
            return self._strip_html_tags("\n".join(html_parts)), image_count
        return "", image_count

    def _decode_part(self, part: email.message.Message) -> str:
        """Decode a MIME part's payload, handling transfer encodings and charset."""
        payload = part.get_payload(decode=True)
        if payload is None:
            # No CTE specified — payload is already a string
            raw = part.get_payload()
            return raw if isinstance(raw, str) else ""
        charset = part.get_content_charset() or "utf-8"
        return payload.decode(charset, errors="replace")

    @staticmethod
    def _strip_html_tags(html_text: str) -> str:
        """Strip HTML tags — used as fallback when no text/plain part exists."""
        text = re.sub(r"<[^>]+>", " ", html_text)
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _build_text_content(self, headers: dict, body: str) -> str:
        """Build full text by prepending decoded headers to body.

        Headers are included so that entity recognizers can detect
        names, addresses, and other PII from email header fields.
        """
        lines: list[str] = []
        for field in ("from", "to", "cc", "bcc", "subject", "date"):
            if field in headers:
                lines.append(f"{field.capitalize()}: {headers[field]}")
        if lines:
            lines.append("")  # blank separator between headers and body
        lines.append(body)
        return "\n".join(lines)
