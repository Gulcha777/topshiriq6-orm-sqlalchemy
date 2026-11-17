"""SQL so'rovlarni ushlab turuvchi va N+1 belgisini aniqlovchi yordamchi vositalar."""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from sqlalchemy import Engine, event


@dataclass
class QueryCounter:
    """with QueryCounter(engine) as qc: ...  ->  qc.count, qc.statements"""

    engine: Engine
    statements: list[tuple[str, object]] = field(default_factory=list)

    def _on_execute(self, conn, cursor, statement, parameters, context, executemany):
        self.statements.append((statement, parameters))

    def __enter__(self) -> "QueryCounter":
        self.statements.clear()
        event.listen(self.engine, "before_cursor_execute", self._on_execute)
        return self

    def __exit__(self, *exc) -> None:
        event.remove(self.engine, "before_cursor_execute", self._on_execute)

    @property
    def count(self) -> int:
        return len(self.statements)


def normalize(sql: str) -> str:
    """Bo'sh joylarni siqib, so'rov 'shablon'ini hosil qiladi."""
    return re.sub(r"\s+", " ", sql).strip()


def detect_n_plus_one(statements, threshold: int = 5) -> list[tuple[str, int]]:
    """Bir xil SQL shablon `threshold` martadan ko'p takrorlansa, N+1 belgisi deb hisoblaydi."""
    counts = Counter(normalize(sql) for sql, _ in statements)
    suspicious = [(sql, n) for sql, n in counts.items() if n >= threshold]
    return sorted(suspicious, key=lambda x: -x[1])


def format_log(statements) -> str:
    """SQL log'ni o'qish uchun qulay matn ko'rinishida qaytaradi."""
    lines = []
    for i, (sql, params) in enumerate(statements, 1):
        lines.append(f"[{i}] {normalize(sql)}")
        lines.append(f"    parametrlar: {params}")
    return "\n".join(lines) + "\n"
