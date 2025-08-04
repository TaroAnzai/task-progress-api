
---

## ✅ Enum運用方針（i18n対応・数値保存ベース）

本プロジェクトでは、`Enum` 型を使用する項目（ステータス、ロール、アクセス権など）において、**多言語対応（i18n）とデータの一貫性を両立するため**、以下の方針で統一します。

---

### 🎯 目的

* **DBは数値で軽量に保存**
* **APIは文字列（Enum名）で入出力**
* **UI表示はフロントで翻訳（i18n）により柔軟に切り替え可能**

---

### 🧱 Enum 定義ルール（Python）

* すべてのEnumは `IntEnum` を使用
* 値は数値（`1`, `2`, ...）で定義
* 表示用ラベルや多言語翻訳は含めない（フロントで処理）

```python
from enum import IntEnum

class TaskAccessLevelEnum(IntEnum):
    VIEW = 1
    EDIT = 2
    FULL = 3
    OWNER = 4
```

---

### 🗄 モデル定義（SQLAlchemy）

* `IntEnum` は `TypeDecorator`（例: `IntEnumType`）を使用し、数値でDB保存
* 例：

```python
access_level = db.Column(IntEnumType(TaskAccessLevelEnum), nullable=False)
```

---

### 📤 API出力（GET）

* Enumの **名前（例: `"VIEW"`）を文字列で返す**
* 表示用の文言（"閲覧"など）は返さない（フロントで翻訳）

```json
{
  "access_level": "VIEW"
}
```

---

### 📥 API入力（POST / PUT）

* `"VIEW"` のような文字列（Enum名）で受け取る
* バリデーションには `marshmallow_enum.EnumField(by_value=False)` を使用

```python
from marshmallow_enum import EnumField

class TaskAccessSchema(Schema):
    access_level = EnumField(TaskAccessLevelEnum, by_value=False, required=True)
```

---

### 🌍 フロントエンドでの翻訳（i18n）

* APIから受け取ったEnum名をもとに翻訳辞書でラベルを取得

例（i18next）：

```json
// ja.json
{
  "TaskAccessLevelEnum": {
    "VIEW": "閲覧",
    "EDIT": "編集",
    "FULL": "全権限",
    "OWNER": "管理者"
  }
}
```

```ts
t(`TaskAccessLevelEnum.${access_level}`); // => "閲覧"
```

---

