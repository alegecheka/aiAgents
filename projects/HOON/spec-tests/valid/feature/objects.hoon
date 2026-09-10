{{{ 
  empty: {};
  emptySpaced: { <!-- comment inside empty --> };
  oneField: { a: 1 };
  trailingSemi: { x: 1; y: 2; };
  deep: {
    l1: {
      l2: {
        l3: { value: "deep" }
      }
    }
  };
  withComment: {
    a: 1; <!-- comment after field -->
    b: <!-- comment before value --> 2
  }
}}}