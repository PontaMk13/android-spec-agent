---
source: android-security-bulletin
source_url: https://source.android.com/docs/security/bulletin/2026/2026-09-01
period: 2026-09
detected_at: 2026-10-01T20:18:12.811718
---

# 全体像
- 総件数: 147件
- 深刻度別の件数:
  - Critical: 28件
  - High: 119件
- コンポーネント別の件数内訳:
  - System: 73件
  - Framework: 40件
  - Imagination Technologies: 30件
  - MediaTek components: 23件
  - Qualcomm closed-source components: 12件
  - Kernel: 5件
  - Unisoc components: 8件
  - Android runtime: 1件
  - Setup Wizard: 1件
  - TV: 3件
  - Kernel components: 1件
  - Arm components: 7件
  - Tsingteng Micro: 1件
  - Qualcomm components: 5件
  *(注: 1つのCVEが複数箇所で言及される場合があるため、コンポーネントごとの総数と総件数には重複が含まれる場合があります)*

# 重要な脆弱性
- CVE-2026-28666（Framework / Critical）: 権限昇格（EoP）
- CVE-2026-55273（Framework / Critical）: 権限昇格（EoP）
- CVE-2026-49932（Framework / Critical）: サービス拒否（DoS）
- CVE-2026-28604（System / Critical）: リモートコード実行（RCE）
- CVE-2026-28618（System / Critical）: リモートコード実行（RCE）
- CVE-2026-28639（System / Critical）: リモートコード実行（RCE）
- CVE-2026-28662（System / Critical）: リモートコード実行（RCE）
- CVE-2026-49882（System / Critical）: リモートコード実行（RCE）
- CVE-2026-49884（System / Critical）: リモートコード実行（RCE）
- CVE-2026-49919（System / Critical）: リモートコード実行（RCE）
- CVE-2026-49921（System / Critical）: リモートコード実行（RCE）
- CVE-2026-27280（System / Critical）: 権限昇格（EoP）
- CVE-2026-28590（System / Critical）: 権限昇格（EoP）
- CVE-2026-33636（System / Critical）: 権限昇格（EoP）
- CVE-2026-45515（System / Critical）: 権限昇格（EoP）
- CVE-2026-45531（System / Critical）: 権限昇格（EoP）
- CVE-2026-49879（System / Critical）: 権限昇格（EoP）
- CVE-2026-49918（System / Critical）: 権限昇格（EoP）
- CVE-2026-49927（System / Critical）: 権限昇格（EoP）
- CVE-2026-55277（System / Critical）: 権限昇格（EoP）
- CVE-2026-55285（System / Critical）: 権限昇格（EoP）
- CVE-2026-58823（System / Critical）: 権限昇格（EoP）
- CVE-2026-28653（System / Critical）: サービス拒否（DoS）
- CVE-2026-49926（System / Critical）: サービス拒否（DoS）
- CVE-2026-55256（System / Critical）: サービス拒否（DoS）
- CVE-2026-31629（Kernel / Critical）: 権限昇格（EoP）
- CVE-2026-58846（Kernel / Critical）: 権限昇格（EoP）
- CVE-2026-58848（Kernel / Critical）: 権限昇格（EoP）
- CVE-2026-58941（Kernel / Critical）: 権限昇格（EoP）
- CVE-2026-52993（Kernel components / Critical）: リモートコード実行（RCE）
- CVE-2026-25289（Qualcomm closed-source components / Critical）: クローズドソースコンポーネントの脆弱性

*(※攻撃の兆候が確認されている旨の特記事項があるCVEはこの月報内には該当ありません)*

# 傾向
件数が多いコンポーネント領域の上位順（上位5領域）:
1. **System**: 73件
2. **Framework**: 40件
3. **Imagination Technologies**: 30件
4. **MediaTek components**: 23件
5. **Qualcomm closed-source components**: 12件

詳細な情報については、公式の [Android Security Bulletin—September 2026](https://source.android.com/docs/security/bulletin/2026/2026-09-01) を参照してください。
