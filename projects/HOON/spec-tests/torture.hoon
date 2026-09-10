{{{<!--
  HOON torture test — exercises every edge of v0.1
  Covers: numbers (dec/hex/float/exp), strings (escapes/unicode/utf8),
  text blocks (empty/indented/triple-escape), keys (bare/quoted/special),
  objects (empty/deep/trailing;), arrays (empty/trailing-comma/nested/mixed),
  comments everywhere, and deep nesting.
-->
  ints: {
    zero: 0;
    negZero: -0;
    one: 1;
    neg: -42;
    big: 9223372036854775807;
    hexZero: 0x0;
    hexSmall: 0x2A;
    hexLower: 0xabcdef;
    hexUpper: 0xABCDEF;
    hexMixed: 0X1a;
    negHex: -0xFF
  };
  floats: {
    zeroDot: 0.0;
    half: 0.5;
    negHalf: -0.5;
    pi: 3.14;
    large: 1e9;
    largeUpper: 1E9;
    withPlus: 1e+10;
    tiny: 1e-10;
    negExp: -2.5E-3;
    avogadro: 6.022e23
  };
  strings: {
    empty: "";
    simple: "hello";
    escapes: "quote:\" backslash:\\ newline:\n tab:\t cr:\r unicode:\u0041\u00E9\u20AC";
    utf8: "naïve café — ✓ 🎉";
    mixedEsc: "a\"b\\c"
  };
  texts: {
    empty: """
""";
    simple: """
Hello
World
""";
    indented: """
  two spaces kept
	tab kept
line with "quotes" and \ backslashes literal
""";
    withTriple: """
first line
second with \""" literal triple
third line
""";
    singleLine: """inline text""";
    unicodeText: """
naïve – café ✓
second line with emoji 🎉
"""
  };
  keys: {
    normal: 1;
    _private: 2;
    camelCase: 3;
    snake_case: 4;
    "kebab-case": 5;
    "my odd key": 6;
    "123numeric": 7;
    "-dashStart": 8;
    "key:with:colons": 9;
    "key;with;semi": 10;
    "sp ace": "spacey"
  };
  objects: {
    empty: {};
    emptySpaced: { <!-- comment inside empty --> };
    oneField: { a: 1 };
    trailingSemi: { x: 1; y: 2; };
    deep: {
      l1: {
        l2: {
          l3: {
            l4: {
              l5: { value: "depth 5" }
            }
          }
        }
      }
    };
    withComment: {
      a: 1; <!-- comment after field -->
      b: <!-- comment before value --> 2
    }
  };
  arrays: {
    empty: [];
    single: [1];
    trailingComma: [1, 2, 3,];
    nested: [[1, 2], [3, [4, 5]], []];
    mixed: ["str", 42, 3.14, true, false, null, { x: 1 }, [9, 8]];
    withComments: [1, <!-- between elements --> 2, 3];
    matrix3d: [[[1], [2]], [[3, 4]]];
    arrayOfObjects: [{ name: "a"; v: 0x1 }, { name: "b"; v: 0x2 }]
  };
  combos: {
    pipeline: [
      { name: "tokenize"; params: { maxTokens: 4096; stop: ["the", "and",] } },
      { name: "summarize"; hex: 0x2A; temp: 0.2 }
    ];
    hooks: { onStart: { run: "bash"; args: ["mkdir", "-p", "/tmp"] }; onFinish: null };
    emptyObjInArray: [{ empty: {} }, []]
  };
  specials: {
    boolTrue: true;
    boolFalse: false;
    nothing: null;
    arrayWithNulls: [null, null];
    soloText: """single"""
  }
}}}
