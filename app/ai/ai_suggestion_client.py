import abc
from typing import Any, Dict, List
import re


class AISuggestionClient(abc.ABC):
    """
    外部AIプロバイダとのやり取りを抽象化した基底クラス
    各プロバイダはこのクラスを継承して実装する
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    def build_prompt_for_task_name(self, task_info):
        return (
            "以下のタスク情報に基づき、「目標（ゴール）」として適切なタイトルを1つ提案してください。\n\n"
            "【目的】\n"
            "このタイトルは業務上の目標（ゴール）として使われるため、次の観点をできる限り含めてください。\n"
            "ただし、情報が不足している場合は省略して構いません。\n\n"
            "【目標としての条件（SMART）】\n"
            "- Specific（具体的）：誰が見ても明確に理解できる\n"
            "- Measurable（測定可能）：成果や進捗が測定できる表現を含む（例：件数、期日など）\n"
            "- Achievable（達成可能）：現実的に実行可能と感じられる\n"
            "- Relevant（関連性）：業務や組織の目的と一致している内容\n"
            "\n"
            "【出力形式】\n"
            "必ず次のタグで囲んだ形式で出力してください：\n\n"
            "<task_title>ここに目標タイトルを記載</task_title>\n\n"
            "【タスク情報】\n"
            f"タイトル: {task_info.get('title')}\n"
            f"説明: {task_info.get('description')}\n"
            f"カテゴリ: {task_info.get('category')}\n"
            f"期限: {task_info.get('deadline')}"
        )


    def build_prompt_for_objectives(self, task_info):
        if not isinstance(task_info, dict):
            raise ValueError("task_info must be a dictionary")
        return (
            "以下のタスク情報に基づき、達成のために必要な目的（オブジェクティブ）を提案してください。\n\n"
            "【出力条件】\n"
            "- 各目的（objective）には以下の3項目を含めてください：\n"
            "  - 目的内容（text）：その目的が具体的に何かを簡潔に記載\n"
            "  - 担当者（assignee）：明確に特定できる場合のみ記載。**不明な場合は空欄にしてください。**\n"
            "  - 期限（due_date）：具体的な日付（例：2025-06-01）が明示されている場合のみ記載。**不明・曖昧な場合は空欄にしてください。**\n"
            "- 出力形式は以下のXML風タグ形式に厳密に従ってください：\n\n"
            "<objective>\n"
            "  <text>目的の内容</text>\n"
            "  <assignee>担当者名（不明な場合は空欄）</assignee>\n"
            "  <due_date>yyyy-mm-dd（不明な場合は空欄）</due_date>\n"
            "</objective>\n\n"
            "【タスク情報】\n"
            f"タイトル: {task_info.get('title')}\n"
            f"説明: {task_info.get('description')}\n"
            f"カテゴリ: {task_info.get('category')}\n"
            f"期限: {task_info.get('deadline')}\n"
        )


    @abc.abstractmethod
    def call_api(self, prompt: str) -> str:
        """
        外部AI APIへの問い合わせ処理
        """
        pass

    def suggest_task_name(self, task_info: Dict[str, Any]) -> Dict[str, str]:
        """
        タスク情報から提案されたタスク名を返す（同期処理）
        """
        prompt = self.build_prompt_for_task_name(task_info)
        response = self.call_api(prompt)
        title = self.extract_task_title(response)

        return {
            "title": title,
            "prompt": prompt,
            "raw_data": response
        }

    def generate_objectives(self, task_info: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self.build_prompt_for_objectives(task_info)
        raw_response = self.call_api(prompt)  # ← str を想定
        objectives = self._parse_objectives(raw_response)

        return {
            "objectives": objectives,
            "raw_data": raw_response,
            "prompt": prompt
        }
   
    def extract_task_title(self, text: str) -> str:
        match = re.search(r"<task_title>(.*?)</task_title>", text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _parse_objectives(self, raw_response: str) -> List[Dict[str, str]]:
        pattern = r"<objective>.*?<text>(.*?)</text>.*?<assignee>(.*?)</assignee>.*?<due_date>(.*?)</due_date>.*?</objective>"
        matches = re.findall(pattern, raw_response, re.DOTALL)

        return [
            {
                "text": text.strip(),
                "assignee": assignee.strip(),
                "due_date": due_date.strip()
            }
            for text, assignee, due_date in matches
            if text.strip()
        ]