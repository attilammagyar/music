(function () {
    function $(id) { return document.getElementById(id); }

    function readFile(input, target, callback)
    {
        var file = input.files[0];

        if (file) {
            var reader = new FileReader();
            reader.onload = function(e) { target.setAttribute("src", e.target.result); }
            reader.readAsDataURL(file);
            callback();
        }
    }

    function time()
    {
        return Date.now() / 1000.0;
    }

    function keyToEventId(key)
    {
        return "event_" + String(key);
    }

    function getEvent(key)
    {
        var evt_id = keyToEventId(key);

        return events.hasOwnProperty(evt_id) ? events[evt_id] : null;
    }

    function loadSprite(parent_sprite, sprite)
    {
        var img = new Image(),
            id = sprites.length,
            children = [],
            // dbg_a = document.createElement("div"),
            evt, evt_id, effect_def, i, replace, dbg;

        if (sprite["position"].length !== 2) {
            return;
        }

        sprites.push({
            "image": img,
            // "dbg_a": dbg_a,
            "replace": null,
            "anchor": sprite["anchor"],
            "position": sprite["position"],
            "offset": [0, 0],
            "z": sprite["z"],
            "size": [0, 0],
            "center": [0, 0],
            "parent": parent_sprite,
            "rotate": 0,
            "scale": 1.0,
            "opacity": 1.0,
            "children": children
        });
        img.onload = function () {
            var s = sprites[id];

            s["size"] = [img.naturalWidth, img.naturalHeight];
            s["center"] = vscale(1.0 / 2.0, s["size"]);

            render();
        };
        img.src = sprite["name"];
        canvas.appendChild(img);
        // canvas.appendChild(dbg_a);

        for (i = 0; i < sprite["events"].length; ++i) {
            evt = sprite["events"][i];
            evt_id = keyToEventId(evt["key"]);

            if (!events.hasOwnProperty(evt_id)) {
                events[evt_id] = {
                    "state": "inactive",
                    "effects": []
                };
            }

            effect_def = evt["effect"];

            if (effect_def["type"] === "replace") {
                replace = new Image();
                replace.src = effect_def["img"];
                replace.style.position = "absolute";
                replace.style.left = "2000vw";
                canvas.appendChild(replace);
            } else {
                replace = null;
            }

            events[evt_id]["effects"].push(
                {
                    "def": effect_def,
                    "sprite": id,
                    "param": 0,
                    "replace": replace
                }
            );
        }

        for (i = 0; i < sprite["children"].length; ++i) {
            children.push(loadSprite(id, sprite["children"][i]));
        }

        return id;
    }

    function loadScene(scene)
    {
        loadSprite(null, scene["main"]);
        audio.src = scene["audio"];
    }

    function convert(pos)
    {
        var w = canvas_size[0],
            h = canvas_size[1],
            x = pos[0],
            y = pos[1];

        return [64.0 * x / w, 36.0 * y / h];
    }

    function vscale(scalar, vector)
    {
        return [scalar * vector[0], scalar * vector[1]];
    }

    function vsum(a, b)
    {
        return [a[0] + b[0], a[1] + b[1]];
    }

    function vdiff(a, b)
    {
        return [a[0] - b[0], a[1] - b[1]];
    }

    function rotate(point, origin, degrees)
    {
        var rad = (degrees * Math.PI) / 180,
            sin = Math.sin(rad),
            cos = Math.cos(rad),
            x, y;

        point = vdiff(point, origin);
        x = point[0];
        y = point[1];

        return vsum(origin, [x * cos - y * sin, x * sin + y * cos]);
    }

    function computeCenterRotationScaleOpacityOnScreen(sprite)
    {
        var center, rotation, scale, opacity,
            parent_sprite, parent_center, parent_rotation, parent_scale, parent_opacity,
            tmp;

        scale = sprite["scale"];
        opacity = sprite["opacity"];

        center = vsum(
            sprite["position"],
            vscale(scale, vdiff(sprite["center"], sprite["anchor"]))
        );

        rotation = sprite["rotate"];
        center = rotate(center, sprite["position"], rotation);
        center = vsum(center, vscale(sprite["scale"], sprite["offset"]));

        parent_sprite = sprite["parent"];

        if (parent_sprite !== null) {
            parent_sprite = sprites[parent_sprite];

            tmp = computeCenterRotationScaleOpacityOnScreen(parent_sprite);
            parent_center = tmp[0];
            parent_rotation = tmp[1];
            parent_scale = tmp[2];
            parent_opacity = tmp[3];
            center = vscale(parent_scale, center);
            center = vsum(parent_center, vdiff(center, vscale(parent_scale, parent_sprite["center"])));
            center = rotate(center, parent_center, parent_rotation);

            scale *= parent_scale;
            opacity *= parent_opacity;
            rotation += parent_rotation;
        }

        return [center, rotation, scale, opacity];
    }

    function render()
    {
        var i, l, sprite, img, size, topleft, style, anchor, center, rotation, scale, opacity, tmp;

        for (i = 0, l = sprites.length; i < l; ++i) {
            sprite = sprites[i];
            img = sprite["image"];
            style = img.style;
            tmp = computeCenterRotationScaleOpacityOnScreen(sprite);
            center = tmp[0];
            rotation = tmp[1];
            scale = tmp[2];
            opacity = tmp[3];

            if (sprite["replace"] !== null) {
                style.left = "2000vw";
                img = sprite["replace"];
                style = img.style;
            }

            size = [img.naturalWidth, img.naturalHeight];
            size = vscale(scale, size);
            topleft = convert(vdiff(center, vscale(1.0 / 2.0, size)));
            size = convert(size);

            style.position = "absolute";
            style.left = String(topleft[0]) + "vw";
            style.top = String(topleft[1]) + "vw";
            style.width = String(size[0]) + "vw";
            style.height = String(size[1]) + "vw";
            style.zIndex = sprite["z"];
            style.transform = "rotate(" + String(rotation) + "deg)";
            style.opacity = opacity;

            // sprite["dbg_a"].style.background = "#0000a0";
            // sprite["dbg_a"].style.position = "absolute";
            // sprite["dbg_a"].style.left = String(convert(center)[0]) + "vw";
            // sprite["dbg_a"].style.top = String(convert(center)[1]) + "vw";
            // sprite["dbg_a"].style.width = "5px";
            // sprite["dbg_a"].style.height = "5px";
            // sprite["dbg_a"].style.zIndex = "2000";
        }
    }

    function ease(t)
    {
        return t * t * (3 - 2 * t);
    }

    function animate()
    {
        var now = time(),
            done = true,
            delta, key, evt, state, param, effects, effect, duration, i, l, rewind_done, sprite, rec_ts, eased_param;

        if (previous_frame === null) {
            previous_frame = now;
        }

        if (playing) {
            timestamp.value = String(Math.floor((now - rec_started + rec_offset) * 1000) / 1000);
        }

        delta = now - previous_frame;
        param = 0;

        for (i = 0, l = sprites.length; i < l; ++i) {
            sprite = sprites[i];
            sprite["scale"] = 1.0;
            sprite["opacity"] = 1.0;
            sprite["rotate"] = 0.0;
            sprite["offset"] = [0.0, 0.0];
        }

        for (key in events) {
            if (!events.hasOwnProperty(key))
                continue;

            evt = events[key];
            state = evt["state"];

            if (state === "inactive")
                continue;

            effects = evt["effects"];
            rewind_done = true;

            for (i = 0, l = effects.length; i < l; ++i) {
                effect = effects[i];
                effect_def = effect["def"];

                if (effect_def.hasOwnProperty("duration")) {
                    param = effect["param"];

                    if (state === "started") {
                        duration = effect_def["duration"];

                        if (duration < 0.0001) {
                            param = 1;
                        } else {
                            param = Math.min(1, param + delta / duration);
                        }

                        if (param < 1) {
                            done = false;
                        }
                    } else {
                        duration = effect_def.hasOwnProperty("rewind")
                            ? effect_def["rewind"]
                            : effect_def["duration"];

                        if (duration < 0.0001) {
                            param = 0;
                        } else {
                            param = Math.max(0, param - delta / duration);
                        }

                        if (param > 0) {
                            done = false;
                            rewind_done = false;
                        }
                    }

                    effect["param"] = param;
                }

                sprite = sprites[effect["sprite"]];

                switch (effect_def["type"]) {
                    case "scale":
                        eased_param = ease(param);
                        sprite["scale"] *= eased_param * effect_def["scale"] + 1.0 - eased_param;
                        break;
                    case "opacity":
                        eased_param = ease(param);
                        sprite["opacity"] *= eased_param * effect_def["opacity"] + 1.0 - eased_param;
                        break;
                    case "rotate":
                        sprite["rotate"] += ease(param) * effect_def["angle"];
                        break;
                    case "translate":
                        sprite["offset"] = vsum(sprite["offset"], vscale(ease(param), effect_def["offset"]));
                        break;
                    case "replace":
                        if (state === "started") {
                            if (sprite["replace"] !== null) {
                                sprite["replace"].style.left = "2000vw";
                            }
                            sprite["replace"] = effect["replace"];
                        } else if (sprite["replace"] === effect["replace"]) {
                            sprite["replace"] = null;
                            effect["replace"].style.left = "2000vw";
                        }
                        break;
                }
            }

            if (state === "rewinding" && rewind_done) {
                evt["state"] = "inactive";
            }
        }

        render();

        if (done && (!playing)) {
            previous_frame = null;
        } else {
            previous_frame = now;
            rec_ts = now - rec_started + rec_offset;

            if (playing) {
                for (l = queued_events.length; (l > 0) && (queued_events[--l]["time"] <= rec_ts);) {
                    evt = queued_events.pop();

                    if (evt["type"] === "down") {
                        startEvent(evt["key"]);
                    } else {
                        rewindEvent(evt["key"]);
                    }
                }
            }

            requestAnimationFrame(animate);
        }
    }

    function rewindEvent(key)
    {
        var evt = getEvent(key);

        if (evt === null || evt["state"] !== "started")
            return false;

        evt["state"] = "rewinding";

        return true;
    }

    function startEvent(key)
    {
        var evt = getEvent(key);

        if (evt === null || evt["state"] === "started")
            return false;

        evt["state"] = "started";

        return true;
    }

    function recordEvent(evt_type, key)
    {
        var now;

        if (!recording) {
            return;
        }

        now = time();
        rec_events.push(
            {
                "type": evt_type,
                "key": key,
                "time": now - rec_started + rec_offset
            }
        );
    }

    function handleKeyUp(e)
    {
        var key = e["key"];

        if (!rewindEvent(key)) {
            return;
        }

        recordEvent("up", key);
        requestAnimationFrame(animate);
    }

    function handleKeyDown(e)
    {
        var key = e["key"],
            now;

        if (!startEvent(key)) {
            return;
        }

        recordEvent("down", key);
        requestAnimationFrame(animate);
    }

    function resetEffects()
    {
        var key, evt, i, l, sprite;

        for (key in events) {
            if (!events.hasOwnProperty(key))
                continue;

            evt = events[key];
            evt["state"] = "inactive";
            effects = evt["effects"];

            for (i = 0, l = effects.length; i < l; ++i) {
                effect = effects[i];

                if (effect.hasOwnProperty("param")) {
                    effect["param"] = 0;
                }
                if (effect["replace"] !== null) {
                    effect["replace"].style.left = "2000vw";
                }
            }
        }

        for (i = 0, l = sprites.length; i < l; ++i) {
            sprite = sprites[i];
            sprite["replace"] = null;
            sprite["rotate"] = 0;
            sprite["offset"] = [0, 0];
        }
    }

    function dumpEvents()
    {
        events_dump.value = (
            JSON.stringify(event_layers)
            .replace(/\{/g, "\n  {")
            .replace(/\],/g, "],\n")
        );
    }

    function stopPlaying()
    {
        if (playing && recording) {
            mergeRecordedEventsIntoSelectedLayer(time() - rec_started + rec_offset);
        }

        resetEffects();
        render();
        recording = false;
        playing = false;
        updatePlaybackButton();
        audio.pause();
        audio.currentTime = 0;
        dumpEvents();
    }

    function startPlaying()
    {
        var ex;

        if (events_dump.value) {
            try {
                event_layers = JSON.parse(events_dump.value);
            } catch (ex) {
                alert("Error: " + String(ex));
                return;
            }
        }

        resetEffects();
        render();
        play.innerHTML = "Stop";
        selected_layer = layer_selector.value;
        queued_events = queueEvents(record.checked);
        rec_offset = Number(timestamp.value);
        rec_events = [];
        audio.currentTime = rec_offset;
        rec_started = time();
        recording = record.checked;
        playing = true;
        audio.play();
        requestAnimationFrame(animate);
    }

    function togglePlayback()
    {
        if (playing) {
            stopPlaying();
        } else {
            startPlaying();
        }
    }

    function mergeRecordedEventsIntoSelectedLayer(rec_stopped)
    {
        var evts = [],
            layer = event_layers[selected_layer],
            evt, i, l;

        sortEventsDesc(layer);

        for (i = layer.length - 1; (i >= 0) && (layer[i]["time"] < rec_offset); --i) {
            evts.push(layer.pop());
        }

        for (i = 0, l = rec_events.length; i < l; ++i) {
            evts.push(rec_events[i]);
        }

        rec_events = [];

        for (i = layer.length - 1; (i >= 0) && (layer[i]["time"] <= rec_stopped); --i) {
            layer.pop();
        }

        for (i = layer.length - 1; i >= 0; --i) {
            evts.push(layer.pop());
        }

        sortEventsAsc(evts);
        event_layers[selected_layer] = evts;
    }

    function sortEventsAsc(evts)
    {
        evts.sort(function (a, b) { return a["time"] - b["time"]; });
    }

    function sortEventsDesc(evts)
    {
        evts.sort(function (a, b) { return b["time"] - a["time"]; });
    }

    function queueEvents(for_recording)
    {
        var q = [],
            layer, layer_id, i, j, l;

        for (i = 0; i < number_of_layers; ++i) {
            layer_id = "layer-" + String(i + 1);

            if (for_recording && layer_id === selected_layer) {
                continue;
            }

            layer = event_layers[layer_id];

            for (j = 0, l = layer.length; j < l; ++j) {
                q.push(layer[j]);
            }
        }

        sortEventsDesc(q);

        return q;
    }

    function updatePlaybackButton()
    {
        play.innerHTML = record.checked ? "Record" : "Play";
    }

    var body = document.getElementsByTagName("body")[0],
        record = $("record"),
        play = $("play"),
        recording = false,
        playing = false,
        rec_started = 0,
        rec_offset = 0,
        rec_events = [],
        canvas = $("canvas"),
        audio = $("audio"),
        layer_selector = $("layer"),
        selected_layer = null,
        scene = window.scene,
        timestamp = $("timestamp"),
        sprites = [],
        canvas_size = window.scene["size"],
        events = {},
        event_layers = {},
        number_of_layers = 20,
        queued_events = null,
        events_dump = $("events"),
        previous_frame = null;

    function main()
    {
        var i, l, option, layer_id;

        for (i = 0; i < number_of_layers; ++i) {
            layer_id = "layer-" + String(i + 1);
            option = document.createElement("option");
            option.value = layer_id;
            option.innerHTML = String(i + 1);
            layer_selector.appendChild(option);
            event_layers[layer_id] = [];
        }

        dumpEvents();

        $("form").onsubmit = function () { return false; }
        play.onclick = togglePlayback;
        record.onchange = updatePlaybackButton;

        updatePlaybackButton();

        body.onkeyup = handleKeyUp;
        body.onkeydown = handleKeyDown;

        loadScene(scene);

        animate();
    }

    main();
})();
