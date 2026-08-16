# 決定記録（ADR）

各決定は Status / Context / Decision / Consequences で記述する。

---

## ADR-001: 取得方式に URL Context を採用

**Status**: Accepted

**Context**: 対象ページ（Android Security Bulletin）のCVE詳細テーブルは静的HTMLに含まれず、`requests` では取得できない。HTMLパース（`soup.find` 等）はページ構造に依存する。

**Decision**: Gemini API の URL Context ツールを使い、URLを渡してGemini側にページ取得と本文抽出を任せる。`requests` / `BeautifulSoup` は使わない。

**Consequences**:
- 取得と抽出のコードが不要になる。
- 取得の成否が Gemini（Google）側に依存する。
- ローカルLLM移行時は URL Context 相当の取得手段を別途用意する必要がある（TBD）。

---

## ADR-002: LLMモデルは固定運用

**Status**: Accepted

**Context**: モデルを変えると要約の粒度・文体・情報の取捨が変わり、蓄積データの一貫性が崩れる。

**Decision**: 使用モデルを固定し、`config.yaml` で管理する。変更は意識的な判断とし、その際は再生成を前提とする。

**Consequences**:
- 蓄積データの品質が揃う。
- 503（混雑）はモデル変更でなくリトライで対処する。

---

## ADR-003: 差分対象は「初版→改訂」の更新

**Status**: Accepted

**Context**: Bulletin は初版公開時は概要のみで、CVE詳細テーブルは含まれない。公開後にAOSPリンク付きで改訂され、CVE詳細が追加される。

**Decision**: この「初版→改訂」による同一URLの内容変化を、hash差分検知の対象とする。動作テストはCVE詳細が既に入っている月で行う。

**Consequences**:
- 初版のみの月はCVEが要約に出ない（正常）。
- 差分検知の意義がこの更新構造にある。

---

## ADR-004: 質問応答（RAG）はローカル構成

**Status**: Accepted

**Context**: 外部クラウドを使うと管理対象が増える。ローカルLLMを採る場合、質問応答も同じマシンに同居できる。

**Decision**: 質問応答は外部クラウドを使わずローカルで実装する。

**Consequences**:
- クラウド移行は将来の別検討（TBD）。

---

## TBD（未決定）

- 最初の1ソース以外の巡回対象（behavior-changes 等）
- 使用するLLM APIモデルの確定（現在は Gemini Flash 系で検証中）
- データスキーマ（frontmatter項目・粒度：1変更=1ファイル か CVE単位 か）
- 要約の出力形式（全CVE羅列 か 要点要約 か、両方保持か）
- P7b（品質検証レビュー）を導入するか
- ローカルLLM移行時の URL Context 相当の取得手段
- クラウド移行時のアーキテクチャ
