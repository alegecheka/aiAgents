{{{<!--
  comment before root
-->
  a: 1; <!-- after field -->
  b: <!-- before value --> 2;
  c: [1, <!-- inside array --> 2];
  d: { x: 1 <!-- inside object --> };
  e: """
inside text <!-- not a comment -->
""" <!-- then real comment -->
  <!-- trailing comment -->
}}}