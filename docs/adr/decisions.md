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

## ADR-005: 成果物と処理状態をディレクトリで分離

**Status**: Accepted

**Context**: 要約（人間が読む成果物）と、hash 等の処理制御用データは性質が異なる。混在させると成果物が汚れる。

**Decision**: 成果物は `entries/`、処理状態は `state/` に分離する。要約は frontmatter 付き Markdown（`entries/<source>/<period>/asb-<period>-summary.md`）、処理状態は JSON（`state/<source>/asb-<period>-meta.json`）とする。

**Consequences**:
- `entries/` を成果物専用に保てる。
- frontmatter には要約の属性（source_url, period, detected_at）のみを書き、hash は書かない。

---

## ADR-006: 処理状態を meta.json で管理

**Status**: Accepted

**Context**: hash 単体ではなく、リトライ回数・エラー・処理結果を含む「処理状態」を記録する必要がある（§5 の自律ループ制御に対応）。

**Decision**: `state/<source>/asb-<period>-meta.json` に処理状態を持つ。項目は `content_hash` / `detected_at` / `retry_count` / `last_error` / `status`。period 単位でファイルを分割し、1ファイルへの集約はしない。

**Consequences**:
- 巡回対象が増えてもファイルが肥大化しない。
- retry / error は自律ループ実装時に本格利用する（現状は枠のみ）。

---

## ADR-007: 変化検知は main タグの hash で行う

**Status**: Accepted

**Context**: URL Context では要約用にページ本文が手元に残らない。差分検知には別途取得が必要。CVE テーブルは main の外にあるが、更新印（Versions テーブル・Last updated）は main 内にある。

**Decision**: `requests` で main タグを取得し、その sha256 を content_hash とする。前回 hash と比較し、変化があるときのみ要約（URL Context）を実行する。

**Consequences**:
- 変化検知（安価）と要約（変化時のみ）で処理が分離し、無駄な API 呼び出しを避ける。
- main 外の CVE テーブルの変更は、更新印（main 内）経由で間接検知する。

---

## ADR-008: エラーは捕捉して meta に記録し、hash でリトライ制御

**Status**: Accepted

**Context**: 要約時に外部 API のエラー（例: 503 混雑）が発生しうる。クラッシュさせず、次回に再試行できる状態を残す必要がある。

**Decision**: 要約呼び出しを try-except で捕捉する。成功時は `status: success` と content_hash を記録。失敗時は `status: error`・`last_error` を記録し、content_hash は空にする。

**Consequences**:
- エラーでクラッシュしない。
- error 時は hash が空になるため、次回巡回で「変化あり」と判定され自動的に再試行される。

---

## ADR-009: 要約の出力形式を固定

**Status**: Accepted

**Context**: 同一プロンプトでも LLM の出力は揺らぎ、概要のみの薄い要約になることがある。

**Decision**: プロンプトで出力形式を固定する。`# 全体像` / `# 重要な脆弱性` / `# 傾向` の見出し構造を必須とし、Critical と攻撃兆候ありは全件を個別記載、High 全件の羅列は不要とする。プロンプトはソース別に外部ファイル（`prompts/<source>/summary.md`）で管理する。

**Consequences**:
- 出力構造が安定し、蓄積データの品質が揃う。
- プロンプト調整がソース単位で独立して行える。

---

## ADR-010: 503 混雑時は lite モデルにフォールバック

**Status**: Accepted

**Context**: 主モデル（gemini-flash-latest）が 503（混雑）で全リトライ失敗することが頻発する。要約失敗のまま終えるより、品質が多少落ちても要約を得たい。

**Decision**: flash-latest で max_retry 回リトライし全滅した場合、gemini-flash-lite-latest で再試行する。実際に使ったモデルを meta の `model_used` に記録する。ADR-002（モデル固定）の例外ではなく、主モデルが使えない時の非常用フォールバックと位置づける。

**Consequences**:
- 混雑時でも要約を得られる。
- `model_used` により、lite で生成された（品質が落ちうる）要約を後から特定・再生成できる。

---

## ADR-011: cron は月初 1 週間の毎日実行

**Status**: Accepted

**Context**: Bulletin は月初に初版、数日後に改訂される（ADR-003）。月 1 回では改訂を拾えず、毎日では過剰。

**Decision**: `schedule: "0 0 1-7 * *"`（UTC0時=JST朝9時、毎月1〜7日）で実行する。変化がなければ hash 判定でスキップされるため、実際に要約が走るのは初版公開日と改訂日のみ。手動実行（workflow_dispatch）も併用する。

**Consequences**:
- 初版と改訂の両方を低コストで拾える。
- 巡回先（source.android.com）への負荷も月初の低頻度に留まり良識的。

---

## ADR-012: 対象 period は今月＋前月

**Status**: Accepted

**Context**: 前月の改訂が月末〜翌月頭に来る場合、「今月のみ」を対象にすると見逃す。

**Decision**: 実行時引数があればその月のみ、なければ `recent_periods()` で今月と前月の両方を処理する。meta の `update_count`（要約成功時 +1）と `model_used` を追加。

**Consequences**:
- 月替わり時も前月の遅い改訂を拾える。変化なければスキップされコスト増なし。
- `update_count` は人間が「前の版に戻す」判断の入口になる（詳細は Git 履歴で辿る）。

---

## ADR-013: frontmatter は行頭から生成する

**Status**: Accepted

**Context**: Python の三重引用符文字列を関数内でインデントして書くと、その空白が frontmatter に混入し YAML が壊れる（`could not find expected ':'`）。

**Decision**: frontmatter を組み立てる `f"""..."""` の中身は、関数のインデントに関わらず行頭（インデント 0）から記述する。値は `source_name` 等の変数を用いる。

**Consequences**:
- 生成される Markdown の frontmatter が正しい YAML になる。

---

## TBD（未決定）

- 最初の1ソース以外の巡回対象（behavior-changes 等）
- 使用するLLM APIモデルの確定（現在は Gemini Flash 系で検証中）
- データ粒度（月単位 か CVE単位 か）
- 自律レビューループ（P7b：生成→レビュー→再生成）の実装
- content_hash の精度（main の hash では main 外テーブル単独変更を直接検知できない）
- ソース識別子とディレクトリ配置の統一（source を最上位にするか）
- ローカルLLM移行時の URL Context 相当の取得手段
- クラウド移行時のアーキテクチャ
- Ph2: RAG 質問応答の実装（ローカル構成）
