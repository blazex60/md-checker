<!--
MDチェッカー動作テスト用 Markdown
ポイント：
- 外側のコードブロックは「````」(4本)なので、中に「```」(3本)のフェンスがあっても途切れません。
- あえてlintで引っかかりやすい要素（末尾スペース、見出し飛び、未定義参照など）を混ぜています。
-->

# タイトル: MD Checker Test Document

## 1. 基本テキストと強調

通常の文章です。**太字**、*斜体*、***太字+斜体***、~~取り消し線~~、`inline code` を含みます。  
↑この行末は「2スペース + 改行」で改行になるはずです。

次の行は意図的に末尾スペースがあります。    
（多くのチェッカーは末尾スペースを警告します）

---

## 2. 見出し階層（意図的に飛ばす）

#### 見出しレベル4（レベル3を飛ばしている）

> 引用です。
> 複数行の引用もあります。
>
> - 引用内のリスト
> - 2つ目

---

## 3. リスト（入れ子・混在）

- 箇条書き1
- 箇条書き2
  - 入れ子1
  - 入れ子2
    - さらに入れ子
- 箇条書き3

1. 番号付き1
2. 番号付き2
   1. 番号付き入れ子1
   2. 番号付き入れ子2
3. 番号付き3

- [ ] タスク未完了
- [x] タスク完了
- [ ] タスク未完了（リンク付き）: [OpenAI](https://openai.com)

---

## 4. コードブロック（言語指定あり/なし）

### 4.1 言語指定あり（Python）

```python
def hello(name: str) -> str:
    # TODO: Replace with real logic
    return f"Hello, {name}!"

print(hello("md-checker"))
```

### 4.2 言語指定なし

```
$ echo "no language fence"
no language fence
```

---

## 5. リンク（正常 / 壊れ / 参照形式）

- 正常リンク: https://example.com
- Markdownリンク: [Example Domain](https://example.com)
- 壊れリンク（存在しないURL例）: [Broken](https://example.invalid/this-should-fail)
- ローカル相対リンク（存在しない想定）: [Missing file](./no_such_file.md)

参照形式リンク:
- [ref-link-1][ref1]
- [ref-link-2][ref2]
- 未定義参照（エラーになりがち）: [undefined-ref][nope]

[ref1]: https://example.com "Example Title"
[ref2]: https://openai.com

---

## 6. 画像（ダミー / 参照形式）

![Alt text](./images/does_not_exist.png "Missing image file")

![Ref image][img1]

[img1]: https://via.placeholder.com/150 "Placeholder"

---

## 7. テーブル（整形揺れ・揃え）

| Col A | Col B | Col C |
|:-----|:-----:|------:|
| left | center | right |
| 1 | 2 | 3 |
| 長いテキスト | 短い | 999999 |

（チェッカーによってはテーブルの整形を要求します）

---

## 8. 定義リスト風（処理系により非対応の場合あり）

Term 1
: Definition 1

Term 2
: Definition 2

---

## 9. HTML混在（許可/禁止のチェック用）

<div>
  <strong>HTML block</strong> inside Markdown.
</div>

---

## 10. エスケープと記号

- バックスラッシュでエスケープ: \*これは斜体にならない\*
- そのままのアスタリスク: *これは斜体になる*
- 角括弧: <tag-like> はHTML扱いになる場合あり

---

## 11. 長い行（行長制限テスト）

この行は意図的にかなり長くしています。MDリンタによっては一定文字数（例: 80/100/120）を超える行を警告する設定があるため、その動作を確認するためのサンプルです。AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

---

## 12. 水平線パターン（バリエーション）

***
___

---

## 13. 空セクション（空見出しの警告用）

## 空のセクション

---

## 14. 末尾に余計な空行テスト


（この上に空行が複数あります）
