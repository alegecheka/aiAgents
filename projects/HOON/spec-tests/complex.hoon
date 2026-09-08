{{{<!-- ============================================================
     HOON complexity test subject.
     Exercises every v0.1 feature: comments, quoted keys, text
     blocks, numbers, nesting, arrays, unicode escapes, empties.
     ============================================================ -->
  name: "scribe-agent";
  version: 1;                 <!-- integer -->
  release: 2.5;               <!-- float -->
  enabled: true;              <!-- boolean -->
  fallback: null;             <!-- null -->
  maxInputBytes: 1048576;
  "version tags": ["core", "reader", "writer"];
  label: "caf\u00e9 \u4F60\u597D";   <!-- \u escapes -->
  rawText: "naïve – ✓ ok";          <!-- raw utf-8 -->

  mixed: [
    "x", <!-- comments may sit between array elements -->
    1,
    false,
    null,
    { deep: { n: -42 } }
  ];
  matrix: [[1, 2], [3, [4, 5]]];
  bigInt: -9223372036854775807;
  avogadro: 6.022e23;
  tiny: -0.5;
  quarter: 0.25;
  zero: 0;

  description: """
The scribe agent reads a subject document and summarizes it.
It handles "quotes", backslashes \ and trailing spaces freely.
\""" a literal three-quote run.
  Two leading spaces are kept on this line.
""";

  pipeline: {
    stages: [
      {
        name: "tokenize";
        params: {
          maxTokens: 4096;
          filter: { stopWords: ["the", "and"] }
        };
        output: { kind: "stream"; channels: ["text", "meta"] }
      },
      {
        name: "summarize";
        params: {
          model: "hoon-mini";
          temperature: 0.2;
          topK: 40;
          hexTest: 0x2A;
          negHex: -0xFF
        };
        empty: { <!-- deliberately empty --> };
        tags: []
      }
    ];
    hooks: {
      onStart: { run: "bash"; args: ["mkdir", "-p", "/tmp/scribe"] };
      onFinish: null
    }
  };

  ui: {
    "panel width": 40;
    layout: {
      type: "split";
      direction: "horizontal"
    };
    "2-levels": true
  }
}}}
