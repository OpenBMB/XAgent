<div align= "center">
    <h1> <img src="assets/readme/xagent_logo.png" height=40 align="texttop">XAgent</h1>
</div>

<div align="center">

[![Twitter](https://img.shields.io/twitter/follow/XAgent?style=social)](https://twitter.com/XAgentTeam) [![Discord](https://img.shields.io/badge/XAgent-Discord-purple?style=flat)](https://discord.gg/zncs5aQkWZ) [![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://opensource.org/license/apache-2-0/) ![Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)

</div>

<p align="center">
    <a href="README.md">English</a> •
    <a href="README_ZH.md">中文</a> •
    <a>日本語</a>
</p>

<p align="center">
  <a href="#Quickstart">チュートリアル</a> •
  <a href="https://www.youtube.com/watch?v=QGkpd-tsFPA">デモ</a> •
  <a href="https://blog.x-agent.net/blog/xagent/">ブログ</a> •
  <a href="https://xagent-doc.readthedocs.io/en/latest/">ドキュメント</a> •
  <a href="#Citation">引用</a>
</p>

## 📖 はじめに

XAgent は、オープンソースの実験的な大規模言語モデル（LLM）駆動自律エージェントであり、様々なタスクを自動的に解決することができる。
これは幅広いタスクに適用できる汎用エージェントとして設計されています。XAgent はまだ初期段階にあり、私たちはその改良に励んでいます。

🏆 私たちの目標は、与えられたタスクを解決できる超知的エージェントを作ることです!

フルタイムでもパートタイムなど、多様な形でのコラボレーションを歓迎します。エージェントのフロンティアに興味があり、私たちと一緒に真の自律型エージェントを実現したい方は、xagentteam@gmail.com までご連絡ください。

<div align="center">
    <img src="assets/readme/overview.png" alt="Overview of Xagent" width="700"/>
    <br/>
    <figcaption>XAgent の概要。</figcaption>
</div>

### <img src="assets/readme/xagent_logo.png" height=30 align="texttop"> XAgent

XAgentは以下の機能を備えています:
- **自律性**: XAgentは人間が関与することなく、さまざまなタスクを自動的に解決することができます。
- **安全性**: XAgent は安全に動作するように設計されています。すべてのアクションは docker コンテナ内で制約されています。とにかく実行しましょう!
- **拡張性**: XAgent は拡張できるように設計されています。エージェントの能力を向上させる新しいツールや、新しいエージェントを簡単に追加することができます！
- **GUI**: XAgent は、ユーザがエージェントと対話するためのフレンドリーな GUI を提供します。また、コマンドラインインタフェースを使用してエージェントと対話することもできます。
- **人間との協調**: XAgent は、あなたと協力してタスクに取り組むことができます。XAgentは、外出先で複雑なタスクを解決する際に、あなたのガイダンスに従うことができるだけでなく、困難に遭遇したときにあなたの支援を求めることもできます。

XAgent は次の 3 つの部分で構成されています:
- **🤖 Dispatcher** は、タスクを動的にインスタンス化し、さまざまなエージェントにディスパッチします。これにより、新しいエージェントを追加したり、エージェントの能力を向上させたりすることができます。
- **🧐 Planner** は、タスクの計画を作成し、修正する役割を担う。タスクをサブタスクに分割し、マイルストーンを生成することで、エージェントは段階的にタスクを解決することができます。
- **🦾 Actor** は、目標を達成し、サブタスクを完了させるためのアクションを実行する責任を負います。アクターはサブタスクを解決するためにさまざまなツールを利用し、人間と協力してタスクを解決することもできます。

<div align="center">
    <img src="assets/readme/workflow.png" alt="XAgentのワークフロー" width="700"/>
    <br/>
    <figcaption>XAgentのワークフロー図。</figcaption>
</div>

### 🧰 ToolServer

ToolServer は、タスクを解決するための強力で安全なツールを XAgent に提供するサーバです。これは、XAgent が実行するための安全な環境を提供する docker コンテナです。
現在、ToolServer は以下のツールを提供しています:
- **📝 ファイルエディタ** は、ファイルの書き込み、読み込み、変更を行うためのテキスト編集ツールを提供します。
- **📘 Python ノートブック** は、Python コードを実行してアイデアを検証したり、図を描いたりできるインタラクティブな Python ノートブックです。
- **🌏 Web ブラウザ** は、ウェブページを検索したり閲覧したりするための web ブラウザです。
- **🖥️ シェル** は bash シェルツールを提供し、あらゆるシェルコマンドを実行できます。
- **🧩 Rapid API** は、Rapid API から API を取得して呼び出すためのツールを提供しており、XAgent が使用できる幅広い API を提供しています。Rapid API コレクションの詳細については、[ToolBench](https://github.com/OpenBMB/ToolBench) を参照してください。
さらに、ToolServer に新しいツールを簡単に追加して、XAgent の能力を強化することもできます。

<div><a id="クイックスタート"></a></div>

## ✨ クイックスタート

### 🛠️ ToolServer の構築とセットアップ

ToolServer は、XAgent の動作が行われる場所です。これは、XAgent が実行するための安全な環境を提供する Docker コンテナになります。
そのため、まず `docker` と `docker-compose` をインストールする必要があります。
次に、ToolServerイメージを構築する必要があります。 ToolServer`ディレクトリでは、私たちのサービスのイメージを構築する2つの方法があります：
以下のコマンドを実行することで、docker hubからイメージを取得し、dockerネットワークを構築することができます：
```bash
docker compose up
```
あるいは、以下のコマンドを実行してローカルソースからイメージを構築することもできます：
バッシュ
```bash
docker compose build
docker compose up
```
これによりツールサーバーのイメージが構築され、ツールサーバーのコンテナが起動します。
コンテナをバックグラウンドで実行したい場合は、`docker compose up -d` を使用してください。
ToolServer の詳細については、[こちら](ToolServer/README.md)を参照してください。

ToolServer が更新された場合、イメージを再構築する必要があります:
```bash
docker compose pull
```
Or
```bash
docker compose build
```

### 🎮 XAgent のセットアップと実行

ToolServer のセットアップが完了したら、XAgent の実行を開始します。
- インストール要件 (Python >= 3.10 が必要)
```bash
pip install -r requirements.txt
```

- XAgent の設定

1. XAgent を実行する前に、`assets/config.yml` で XAgent を設定する必要があります。
2. `assets/config.yml` には、OpenAI API にアクセスするための OpenAI キーが最低 1 つ用意されている。
XAgent を実行するには、`gpt-4-32k` を使用することを強く推奨しています。
いずれの場合も、バックアップモデルとして少なくとも 1 つの `gpt-3.5-turbo-16k` API キーを提供する必要があります。
`gpt-3.5-turbo` を使用して XAgent を実行することは、コンテキストの長さが最小になるため、テストも推奨もしません
; その上で XAgent を実行しようとしてはいけません。
3. `XAgentServer` の設定ファイルのパスを変更したい場合は、`.env` ファイルの `CONFIG_FILE` の値を変更してから docker コンテナを再起動します。


- XAgent の実行
```bash
python run.py --task "put your task here" --config-file "assets/config.yml"
```
1. 引数 `--upload-files` を使って、XAgent に送信したい初期ファイルを選択することができます。

2. XAgent のローカルワークスペースは `local_workspace` にあり、実行中のプロセスを通じて XAgent が生成するすべてのファイルを見つけることができます。

3. 実行後、`ToolServerNode` 内の `workspace` 全体が `running_records` にコピーされます。

4. さらに、`running_records` には、タスクのステータス、LLM の入出力ペア、使用したツールなど、すべての中間ステップの情報を見ることができます。

5. config で `record_dir` を設定（デフォルトは `Null`）するだけで、レコードからロードして以前の実行を再現することができる。レコードは XAgent のコードバージョンに関連付けられたシステムレベルの記録です。すべての実行設定、クエリ、コードの実行状態（エラーを含む）、サーバの動作が記録されます。

6. 私たちは記録からすべての機密情報（API キーを含む）を削除しましたので、他の人と安全に共有することができます。近い将来、実行中の人間の貢献を強調する、より詳細な共有オプションを導入する予定です。



- GUI で XAgent を実行する
コンテナ XAgent-Server は、nginxとポート 5173 でリッスンしているウェブサーバーと共に起動しています。
Web UI を使用して XAgent とやり取りするには、http://localhost:5173 を訪れることができます。
デフォルトのユーザー名とパスワードはそれぞれ guest と xagent です。
GUI デモの詳細については、[こちら](XAgentServer/README.md) を参照してください。

<div><a id="デモ"></a></div>

## 🎬 デモ

ここでは、XAgent によるタスクの解決事例も紹介する:
[XAgent Official Website](https://www.x-agent.net/) では、ライブデモをご覧いただけます。また、XAgent を使用したビデオデモやショーケースもこちらでご覧いただけます:
![Demo](assets/readme/demo.gif)

### ケース 1. データ分析: デュアルループメカニズムの有効性の実証

まず、複雑なデータ分析においてユーザーを支援するケースから始める。ここでは、ユーザがデータ解析の支援を求めて `iris.zip` ファイルを XAgent に送信した。(1)データの検査と理解、(2)システムの Python 環境に関連するデータ分析ライブラリがあるかどうかの検証、(3)データ処理と分析のためのデータ分析コードの作成、(4)Python コードの実行結果に基づく分析レポートのコンパイル。
以下は、XAgent が作成した図である。
![Data Statics by XAgent](assets/readme/statistics.png)


### ケース 2. レコメンデーション: 人間とエージェントのインタラクションの新しいパラダイム

人間の支援を積極的に求め、問題解決に協力するユニークな機能を備えた XAgent は、人間とエージェントの協力の境界を再定義し続けています。下のスクリーンショットに示されているように、あるユーザが XAgent に、親睦を深める集まりに最適なレストランを紹介するよう助けを求めたが、具体的な情報を提供することができなかった。提供された情報が不十分であることを認識した XAgent は、AskForHumanHelp ツールを使用して、人間の介入を促し、ユーザの好みの場所、予算の制約、料理の好み、食事の制限を引き出した。この貴重なフィードバックをもとに、XAgent はシームレスにカスタマイズされたお勧めのレストランを生成し、ユーザーとその友人にパーソナライズされた満足のいく体験を提供しました。

![Illustration of Ask for Human Help of XAgent](assets/readme/ask_for_human_help.png)

### ケース 3. トレーニングモデル: 洗練されたツールユーザー

XAgent は、平凡なタスクに取り組むだけでなく、モデルのトレーニングのような複雑なタスクにおいても貴重な支援となります。ここでは、あるユーザが映画のレビューを分析し、特定の映画を取り巻く世論の感情を評価したいというシナリオを示します。これに対して XAgent は、IMDB データセットをダウンロードしてプロセスを迅速に開始し、ディープラーニングのパワーを活用して最先端の BERT モデルをトレーニングします（以下のスクリーンショットを参照）。XAgent は、この訓練された BERT モデルによって、映画レビューの複雑なニュアンスをシームレスにナビゲートし、さまざまな映画に対する一般の認識に関する洞察に満ちた予測を提供します。

![bert_1](assets/readme/bert_1.png)
![bert_2](assets/readme/bert_2.png)
![bert_3](assets/readme/bert_3.png)

### 📊 評価

XAgent の性能を評価するために、人間の嗜好評価を実施しました。評価のために [50 以上の実世界の複雑なタスク](assets/tasks.yml)を用意し、5 つのクラスに分類します: これらは、「検索とレポート」「コーディングと開発」「データ分析」「数学」「生活支援」の 5 つのクラスに分類されます。
XAgent と [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) の結果を比較したところ、XAgent が AutoGPT に完勝しました。
全ての実行結果は近日公開予定です。

![HumanPrefer](assets/readme/agent_comparison.png)

人間の嗜好の点で、AutoGPT よりも XAgent の方が大幅に優れていることを報告します。

また、以下のベンチマークで XAgent を評価しました:
![Benchmarks](assets/readme/eval_on_dataset.png)


<div><a id="ブログ"></a></div>

## 🖌️ ブログ

ブログは[こちら](https://blog.x-agent.net/)でご覧いただけます!

<div><a id="引用"></a></div>

## 🌟 貢献者の皆さんへ

このプロジェクトに貢献してくれた皆さん、心から感謝します。皆さんの努力が、このプロジェクトの成長と繁栄を支えています。どんな貢献も、大きくても小さくても、非常に価値があります。

![貢献者](https://contrib.rocks/image?repo=OpenBMB/XAgent)

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=openbmb/xagent&type=Date)](https://star-history.com/##openbmb/xagent&Date)

## 引用

もし私たちのリポジトリが役に立つとお感じになりましたら、ぜひ引用をご検討ください:
```angular2
@misc{xagent2023,
      title={XAgent: An Autonomous Agent for Complex Task Solving},
      author={XAgent Team},
      year={2023},
}
```
