window.scene = {
    "size": [1920, 1080],
    "audio": "ha_kihul1.mp3",
    "main": {
        "name": "layers/background-wet.png",
        "anchor": [0, 0],
        "position": [0, 0],
        "z": 1,
        "events": [
            {"key": "1", "effect": {"type": "scale", "scale": 0.55, "duration": 0.5}},
            {"key": "1", "effect": {"type": "translate", "offset": [-2200, 0], "duration": 0.2}},

            {"key": "2", "effect": {"type": "translate", "offset": [160, -960], "duration": 15.0, "rewind": 0.2}},

            {"key": "3", "effect": {"type": "scale", "scale": 0.8, "duration": 11.0, "rewind": 0.2}},
            {"key": "3", "effect": {"type": "translate", "offset": [1140, 496], "duration": 11.0, "rewind": 0.2}},

            {"key": "5", "effect": {"type": "scale", "scale": 2.25, "duration": 12.0, "rewind": 3.0}},
            {"key": "5", "effect": {"type": "translate", "offset": [70, -1300], "duration": 12.0, "rewind": 3.0}},

            {"key": "7", "effect": {"type": "translate", "offset": [700, 250], "duration": 7.4, "rewind": 0.2}},

            {"key": "f", "effect": {"type": "scale", "scale": 0.35, "duration": 0.5}},
            {"key": "f", "effect": {"type": "translate", "offset": [0, 0], "duration": 0.5}},

            {"key": "g", "effect": {"type": "scale", "scale": 2.0, "duration": 15.0}},
            {"key": "g", "effect": {"type": "translate", "offset": [-400, -1100], "duration": 15.0}},

            {"key": "`", "effect": {"type": "scale", "scale": 0.34, "duration": 0.5}},
            {"key": "`", "effect": {"type": "translate", "offset": [0, 0], "duration": 0.5}}
        ],
        "children": [
            {
                "name": "layers/fog1.png",
                "anchor": [0, 0],
                "position": [0, 0],
                "z": 10000,
                "events": [
                    {"key": "a", "effect": {"type": "translate", "offset": [-2879, 0], "duration": 43, "rewind": 0.1}}
                ],
                "children": []
            },
            {
                "name": "layers/fog2.png",
                "anchor": [0, 0],
                "position": [-2879, 0],
                "z": 10001,
                "events": [
                    {"key": "a", "effect": {"type": "translate", "offset": [2880, 0], "duration": 43, "rewind": 0.1}}
                ],
                "children": []
            },
            {
                "name": "layers/steam.png",
                "anchor": [0, 0],
                "position": [1540, 1800],
                "z": 900,
                "events": [
                    {"key": "x", "effect": {"type": "translate", "offset": [-273, -1150], "duration": 36.0, "rewind": 0.1}},
                    {"key": "x", "effect": {"type": "scale", "scale": 2.0, "duration": 36.0, "rewind": 0.1}},
                    {"key": "v", "effect": {"type": "translate", "offset": [-24, 0], "duration": 1.0}},
                    {"key": "o", "effect": {"type": "opacity", "opacity": 0.0, "duration": 3.0}}
                ],
                "children": [
                ]
            },
            {
                "name": "layers/foreground-wet.png",
                "anchor": [0, 0],
                "position": [0, 0],
                "z": 1000,
                "events": [
                ],
                "children": [
                ]
            },
            {
                "name": "layers/foreground-dry.png",
                "anchor": [0, 0],
                "position": [0, 0],
                "z": 0,
                "events": [
                    {"key": "p", "effect": {"type": "opacity", "opacity": 0.0, "duration": 0.1, "rewind": 5.0}}
                ],
                "children": [
                ]
            },
            {
                "name": "layers/tree.png",
                "anchor": [2832, 0],
                "position": [5759, 0],
                "z": 2000,
                "events": [
                ],
                "children": [
                    {
                        "name": "layers/static-leaves.png",
                        "anchor": [2767, 0],
                        "position": [2832, 0],
                        "z": 3000,
                        "events": [],
                        "children": []
                    },
                    {
                        "name": "layers/leaf1.png",
                        "anchor": [188, 5],
                        "position": [303, 551],
                        "z": 3100,
                        "events": [
                            {"key": "9", "effect": {"type": "translate", "offset": [-410, 1700], "duration": 8.0, "rewind": 0.1}},
                            {"key": "m", "effect": {"type": "translate", "offset": [-240, 0], "duration": 2.5, "rewind": 3.5}},
                            {"key": "m", "effect": {"type": "rotate", "angle": 50, "duration": 2.5}},
                            {"key": "n", "effect": {"type": "rotate", "angle": 10, "duration": 0.5}}
                        ],
                        "children": []
                    },
                    {
                        "name": "layers/leaf2.png",
                        "anchor": [218, 129],
                        "position": [590, 942],
                        "z": 3100,
                        "events": [
                            {"key": "8", "effect": {"type": "translate", "offset": [-370, 1460], "duration": 8.4, "rewind": 0.1}},
                            {"key": "b", "effect": {"type": "translate", "offset": [340, 0], "duration": 3.0, "rewind": 4.4}},
                            {"key": "b", "effect": {"type": "rotate", "angle": -30, "duration": 3.0, "rewind": 4.4}},
                            {"key": "j", "effect": {"type": "rotate", "angle": -10, "duration": 0.6}}
                        ],
                        "children": []
                    }
                ]
            }
        ]
    }
}

