class TimelineControl {
    #map;
    #container;

    onAdd(map) {
        const container = $('<div></div>', {class: 'timeline-container'});
        const widget = $('<div></div>', {
            id: 'timeline',
            class: 'maplibregl-ctrl',
        });
        container.append(widget);

        const slider = $('<input type="range" id="timeline-slider" step="1" list="timeline-ticks">');
        widget.append(slider);

        const ticks = $('<datalist id="timeline-ticks"></datalist>');
        widget.append(ticks);

        this.#map = map;
        this.#container = container[0];
        return this.#container;
    }

    onRemove() {
        this.#container.parentNode.removeChild(this.#container);
        this.#map = undefined;
    }
}

function timeline_update(ctx) {
    const tml = $('#timeline-slider');
    const ticks = $('#timeline-ticks');
    const start = ctx.stream.start_time();
    const end = ctx.stream.end_time();
    const tml_res = 300;  // TODO: depends on screen width
    const tml_start = Math.floor(start / tml_res) * tml_res;
    const tml_end = Math.ceil(end / tml_res) * tml_res;

    tml.attr('min', tml_start);
    tml.attr('max', tml_end);
    tml.val(ctx.time);

    ticks.empty();
    for (let i = tml_start; i <= tml_end; i += tml_res)
        ticks.append(
            '<option value="' + i + '" label="' + time_str(i, 'minute') + '"></option>'
        );
}

function timeline_end(ctx) {
    if (ctx.time >= ctx.stream.end_time()) {
        window.clearInterval(ctx.timer);
        ctx.timer = window.setInterval(app_update_real_time, 1000, ctx);
    }
}
