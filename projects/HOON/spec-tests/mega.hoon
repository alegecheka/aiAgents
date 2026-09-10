{{{<!--
  HOON mega stress document — simulates a real-world galactic outpost config.
  Tests large nested structures, realistic data, and sustained parser performance.
-->
  outpost: {
    id: "OP-7";
    name: "Galactic Outpost Seven";
    version: 42;
    coordinates: {
      galaxy: "Andromeda";
      system: "Kepler-442";
      position: { x: 12345.678; y: -9876.543; z: 0.0 };
      hexSector: 0xABCD;
      negHex: -0x10
    };
    crew: [
      { id: 1; name: "Ada Lovelace"; role: "commander"; active: true; clearance: 0xFF; bio: """Ada leads the outpost with precision.
Ex-Military, 12 years experience.
Speaks "English" and "Русский" fluently.""" },
      { id: 2; name: "Ken Thompson"; role: "engineer"; active: true; clearance: 0x7F; bio: "naïve café — systems expert" },
      { id: 3; name: "Grace Hopper"; role: "scientist"; active: false; clearance: 0x0A; bio: """Grace studies exo-biology.
Findings: "life is resilient" — see report.""" }
    ];
    modules: [
      {
        name: "habitat";
        status: "operational";
        capacity: 12;
        temperature: 22.5;
        sensors: [ { type: "thermal"; value: 22.5; unit: "C" }, { type: "oxygen"; value: 0.21e2; unit: "%" } ];
        logs: """
[2026-01-01] Habitat initialized.
[2026-01-02] Life support nominal.
[2026-01-03] Crew rotation: Ada on duty.
"""
      },
      {
        name: "lab";
        status: "degraded";
        capacity: 4;
        temperature: 18.0;
        sensors: [ { type: "radiation"; value: 0.003; unit: "Sv" } ];
        logs: """Lab note: sample #42 contains "unknown" compound.
Action: quarantine.
Backslashes \\ preserved literally."""
      },
      {
        name: "hangar";
        status: "offline";
        capacity: 6;
        temperature: -5.5;
        sensors: [];
        logs: """""";
        notes: { empty: {}; arrayEmpty: [] }
      }
    ];
    inventory: {
      food: { units: 1500; expiry: "2026-12-31"; tags: ["perishable", "essential",] };
      fuel: { units: 0x3E8; type: "hydrogen"; level: 0.85 };
      spareParts: [ "wrench", "panel", "circuit", "panel" ];
      manifest: [
        { sku: "A-1"; qty: 10; price: 9.99 },
        { sku: "B-2"; qty: 0; price: 0.0 }
      ]
    };
    settings: {
      autoPilot: true;
      alertThreshold: 0.75;
      backup: null;
      retries: 3;
      deep: {
        l1: { l2: { l3: { l4: { l5: { secret: "deep value" } } } } }
      }
    };
    <!-- comments can appear anywhere: between fields, inside arrays, after values -->
    timeline: [
      "launch", <!-- first event -->
      "orbit",
      "landing"
    ];
    quotedKeys: {
      "mission-critical": true;
      "123": "numeric key";
      "key with spaces": "works";
      "unicode-✓": "check"
    };
    emptySections: {
      emptyObj: {};
      emptyArr: [];
      emptyText: """
""";
      nestedEmpty: { a: { b: {} } }
    }
  };
  metadata: {
    generated: "2026-09-11";
    author: "aiAgent";
    notes: """This mega document tests:
- 3 crew members with bio text blocks
- 3 modules with nested sensor arrays
- inventory with mixed types
- deep nesting 5 levels
- empty structures
- quoted keys with special chars
- hex and float numbers
- comments everywhere
"""
  }
}}}
