"""飞书 Sheets API 读取器"""

from __future__ import annotations

import time
from typing import Any

import httpx

from ..models import NPCData
from .base import BaseReader

_FEISHU_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
_FEISHU_SHEET_URL = (
    "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{token}/values/{sheet_id}"
)


class FeishuReader(BaseReader):
    """通过飞书开放平台 Sheets API 在线读取 NPC 性格设计表"""

    def __init__(self, app_id: str, app_secret: str) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        self._token: str | None = None
        self._token_expires: float = 0

    # ------------------------------------------------------------------
    # Token 管理
    # ------------------------------------------------------------------

    async def _ensure_token(self, client: httpx.AsyncClient) -> str:
        if self._token and time.time() < self._token_expires:
            return self._token

        resp = await client.post(
            _FEISHU_TOKEN_URL,
            json={"app_id": self.app_id, "app_secret": self.app_secret},
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["tenant_access_token"]
        # 提前 60 秒过期，保留安全余量
        self._token_expires = time.time() + data.get("expire", 7200) - 60
        return self._token  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # 列映射
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_columns(header: list[str]) -> dict[str, int]:
        """自动识别关键列位置（支持中英文表头）"""
        mapping: dict[str, list[str]] = {
            "name": ["npc名称", "name", "npc_name", "名称", "npc"],
            "personality_tags": ["性格标签", "personality_tags", "personality", "标签"],
            "behavior_preferences": ["行为偏好", "behavior_preferences", "behavior", "偏好"],
            "design_intent": ["设计意图", "design_intent", "intent", "意图"],
        }
        lower_header = [h.strip().lower() for h in header]
        result: dict[str, int] = {}
        for field, candidates in mapping.items():
            for c in candidates:
                if c in lower_header:
                    result[field] = lower_header.index(c)
                    break
        return result

    # ------------------------------------------------------------------
    # 主方法
    # ------------------------------------------------------------------

    async def read(
        self,
        *,
        spreadsheet_token: str = "",
        sheet_id: str = "",
        **kwargs: Any,
    ) -> list[NPCData]:
        """读取飞书电子表格并返回 NPCData 列表"""
        if not spreadsheet_token or not sheet_id:
            raise ValueError("必须提供 spreadsheet_token 和 sheet_id 参数")

        async with httpx.AsyncClient(timeout=30) as client:
            token = await self._ensure_token(client)
            url = _FEISHU_SHEET_URL.format(token=spreadsheet_token, sheet_id=sheet_id)
            resp = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
            )
            resp.raise_for_status()
            data = resp.json()

        rows: list[list[Any]] = data.get("data", {}).get("valueRange", {}).get("values", [])
        if len(rows) < 2:
            return []

        header = [str(c) for c in rows[0]]
        col_map = self._detect_columns(header)

        npcs: list[NPCData] = []
        for row in rows[1:]:
            def _cell(field: str) -> Any:
                idx = col_map.get(field)
                if idx is None or idx >= len(row):
                    return None
                return row[idx]

            name = _cell("name")
            if not name:
                continue

            def _split_tags(raw: Any) -> list[str]:
                if isinstance(raw, list):
                    return [str(t).strip() for t in raw if str(t).strip()]
                if isinstance(raw, str):
                    for sep in ["、", ",", "，", ";", "；"]:
                        if sep in raw:
                            return [t.strip() for t in raw.split(sep) if t.strip()]
                    return [raw.strip()] if raw.strip() else []
                return []

            npcs.append(
                NPCData(
                    name=str(name).strip(),
                    personality_tags=_split_tags(_cell("personality_tags")),
                    behavior_preferences=_split_tags(_cell("behavior_preferences")),
                    design_intent=str(_cell("design_intent") or ""),
                )
            )
        return npcs
