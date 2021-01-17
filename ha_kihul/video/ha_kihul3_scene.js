window.scene = {
    "size": [1920, 1080],
    "audio": "ha_kihul3.mp3",
    "main": {
        "name": "layers/poop_in_jail_scream_in_bag.png",
        "anchor": [0, 0],
        "position": [-1104, -621],
        "z": 5,
        "events": [
            {"key": "0", "effect": {"type": "scale", "scale": 0.4651, "duration": 0.1}},
            {"key": "0", "effect": {"type": "translate", "offset": [2374, 1335], "duration": 0.1}},

            {"key": "9", "effect": {"type": "scale", "scale": 1.1, "duration": 7.0}},
            {"key": "9", "effect": {"type": "translate", "offset": [-370, -300], "duration": 7.0}}
        ],
        "children": [
            {
                "name": "layers/poop_in_jail_rage_in_bag.png",
                "anchor": [0, 0],
                "position": [0, 0],
                "z": 10,
                "events": [
                    {"key": "5", "effect": {"type": "opacity", "opacity": 0.0, "duration": 0.2}}
                ],
                "children": []
            },
            {
                "name": "layers/poop_in_jail_angry_in_bag.png",
                "anchor": [0, 0],
                "position": [0, 0],
                "z": 20,
                "events": [
                    {"key": "4", "effect": {"type": "opacity", "opacity": 0.0, "duration": 0.2}},
                    {"key": "b", "effect": {"type": "replace", "img": "layers/poop_in_jail_angry_in_bag_rotated1.png"}},
                    {"key": "n", "effect": {"type": "replace", "img": "layers/poop_in_jail_angry_in_bag_rotated2.png"}}
                ],
                "children": []
            },
            {
                "name": "layers/poop_in_jail_angry.png",
                "anchor": [0, 0],
                "position": [0, 0],
                "z": 30,
                "events": [
                    {"key": "3", "effect": {"type": "opacity", "opacity": 0.0, "duration": 1.2}}
                ],
                "children": []
            },
            {
                "name": "layers/poop_in_jail_sad.png",
                "anchor": [0, 0],
                "position": [0, 0],
                "z": 40,
                "events": [
                    {"key": "2", "effect": {"type": "opacity", "opacity": 0.0, "duration": 1.2}}
                ],
                "children": []
            },
            {
                "name": "layers/poop_in_jail.png",
                "anchor": [0, 0],
                "position": [0, 0],
                "z": 50,
                "events": [
                    {"key": "1", "effect": {"type": "opacity", "opacity": 0.0, "duration": 4.0}}
                ],
                "children": []
            }
        ]
    }
}


