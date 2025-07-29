// https://colorbrewer2.org/#type=qualitative&scheme=Set1&n=9
const AIRCRAFT_COLORS = [
    '#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33',
    '#a65628', '#f781bf', '#999999',
];

class ApplicationContext {
    constructor(map) {
        this.time = Date.now() / 1000;
        this.map = map;
        this.stream = new AircraftStream();
        this.data = new AircraftData();
        this.selection = new AircraftSelection();
        this.timer = null;
    }
}

class AircraftStream {
    #data;
    #pos;
    #limit;

    constructor() {
        this.#data = new Array();
        this.#pos = [0, 0];
        this.#limit = 60 * 60;  // keep 1h of data in the stream
    }

    add(item) {
        const time = Math.floor(item[0]);
        const k = this.#data.length == 0 ? 0 : time - this.start_time();

        if (this.#data.length <= k)
            for (let i = this.#data.length; i <= k; i++)
                this.#data.push(new Array());

        this.#data[k].push(item);

        const dk = this.#data.length - this.#limit;
        const pk = this.#pos[0];
        if (dk > 0 && pk >= dk) {  // TODO: user might trigger OOM via seek method
            this.#data.splice(0, dk);
            this.#pos = [pk - dk, this.#pos[1]];
        }
    }

    read(time=null) {
        const result = new Array();
        const [j, k] = this.#pos;
        const dn = this.#data.length - 1;

        // time is null => real-time: return data till end
        // time is not null => timeline: return data up-to the time
        const n = (time == null) ? dn : Math.max(Math.min(dn, Math.floor(time) - this.start_time() - 1), 0);

        result.push(...this.#data[j].slice(k));
        for (let i = j + 1; i <= n; i++)
            result.push(...this.#data[i]);
        this.#pos = [n, this.#data[n].length];
        return result;
    }

    seek(time) {
        const start = Math.max(0, Math.floor(time) - this.start_time());
        this.#pos = [start, 0];
    }

    start_time() {
        return Math.floor(this.#data[0][0][0]);
    }
    
    end_time() {
        return Math.ceil(nth_last(nth_last(this.#data, 1), 1)[0]);
    };

    size() {
        return this.#data.length;
    }
}

class AircraftData {
    #data;

    constructor() {
        this.#data = new Map();
        this.last_time = Date.now() / 1000;
    }

    add(icao, time, callsign, position, altitude) {
        let bearing = 0;
        let track;

        if (this.#data.has(icao)) {
            // add new position only if it has changed
            track = this.#data.get(icao)['position'];
            const last = nth_last(track, 1);
            if (last[0] != position[0] || last[1] != position[1])
                track.push(position)
        }
        else
            track = [position];

        if (track.length >= 2)
            bearing = geo_bearing(nth_last(track, 2), nth_last(track, 1));

        // re-insert to keep most recent entries at the end
        this.#data.delete(icao);
        this.#data.set(icao, {
            time: time,
            callsign: callsign,
            position: track,
            altitude: altitude,
            bearing: bearing,
            selection_color: AIRCRAFT_COLORS[icao % AIRCRAFT_COLORS.length],
        });
        this.last_time = time;
    }

    get(icao) {
        return this.#data.get(icao);
    }

    contains(icao) {
        return this.#data.has(icao);
    }

    // remove stale aircraft data
    clean(cutoff) {
        // remove stale aircraft data
        const to_drop = Array.from(
            take_while(this.#data.entries(), v => v[1]['time'] < cutoff)
                .map(v => v[0])
        );
        to_drop.forEach(icao => {
            this.#data.delete(icao);
        });
        return to_drop;
    }

    size() {
        return this.#data.size;
    }

    items() {
        return this.#data.entries();
    }

    reset() {
        this.#data.clear();
    }
}

class AircraftSelection {
    #selected;

    constructor() {
        this.#selected = new Set();
    }

    is_selected(icao) {
        return this.#selected.has(icao);
    }

    set(icao) {
        this.#selected.add(icao);
    }

    unset(icao) {
        this.#selected.delete(icao);
    }

    items() {
        return [...this.#selected];
    }

    size() {
        return this.#selected.size;
    }
}

$(document).ready(function() {
    // update height of information panel after window resize, so whole
    // application fits into the window
    $(window).on('resize', function() {
        $('.panel-info').height($(window).height());
        $('#panel-info-aircraft').height('100%');
    });

    const map = new maplibregl.Map({
        container: 'map',
        style: 'https://tiles.openfreemap.org/styles/positron',
        center: [-6.27, 53.421389],
        zoom: 11,
        rollEnabled: false,
        attributionControl: false,
    });
    const ctx = new ApplicationContext(map);
    const nav_ctrl = new maplibregl.NavigationControl({showCompass: false});
    const attr_ctrl = new maplibregl.AttributionControl();
    map.addControl(nav_ctrl, 'top-right');
    map.addControl(attr_ctrl, 'top-left');
    map.addControl(new TimelineControl(), 'bottom-left');
    
    // disable rotation until we figure out how to use it to our advantage
    map.dragRotate.disable();
    map.keyboard.disableRotation();
    map.touchZoomRotate.disableRotation();

    map.on('load', async () => {
        image = await map.loadImage('plane-16x16.png');
        map.addImage('plane', image.data);

        map.addSource(
            'aircraft-route',
            {
                'type': 'geojson',
                'attribution': '<a href="https://gitlab.com/sq1090/sq1090/">Sq1090</a>',
                'data': {'type': 'LineString', 'coordinates': []},
            }
        );
        map.addLayer({
            'id': 'aircraft-route',
            'source': 'aircraft-route',
            'type': 'line',
            'paint': {
                'line-width': 2,
                'line-opacity': 0.75,
                'line-dasharray': [2, 2],
                'line-color': ['get', 'selection-color'],
            },
        });

        map.addSource(
            'aircraft',
            {
                'type': 'geojson',
                'attribution': '<a href="https://gitlab.com/sq1090/sq1090/">Sq1090</a>',
                'data': {'type': 'Point', 'coordinates': []},
            }
        );
        map.addLayer({
            'id': 'aircraft-select',
            'source': 'aircraft',
            'type': 'circle',
            'filter': ['boolean', ['get', 'selected']],
            'paint': {
                'circle-radius': 14,
                'circle-opacity': 0.4,
                'circle-color': ['get', 'selection-color'],
            },
        });
        map.addLayer({
            'id': 'aircraft',
            'source': 'aircraft',
            'type': 'symbol',
            'layout': {
                'icon-image': 'plane',
                'icon-allow-overlap': true,
                'icon-size': 1,
                'icon-rotate': ['number', ['get', 'bearing']],
                'text-field': ['get', 'callsign'],
                'text-allow-overlap': true,
                'text-font': ['Noto Sans Regular'],  // see positron definition
                'text-size': 10,
                'text-anchor': 'top',
                'text-offset': [0, 1.25],
            },
            'paint': {
                'text-opacity': [
                    'case',
                    ['boolean', ['feature-state', 'selected'], false],
                    1,
                    0.75,
                ],
            }
        });
    });

    map.on('click', 'aircraft', (e) => {
        e.features.forEach((feat) => {
            selection_add(ctx, feat['properties']['icao']);
        });
    });

    map.on('mouseenter', 'aircraft', () => {
        map.getCanvas().style.cursor = 'pointer'
    });
    map.on('mouseleave', 'aircraft', () => {
        map.getCanvas().style.cursor = ''
    });

    ctx.timer = window.setInterval(app_update_real_time, 1000, ctx);

    var ev_src = new EventSource('/aircraft', {retry: 5000});
    ev_src.onmessage = function (event) {
        const data = jQuery.parseJSON(event.data);
        ctx.stream.add(data);
    };
    ev_src.onopen = function (event) {
        $('.card #sq1090-conn').hide('fast');
    };
    ev_src.onerror = function (event) {
        $('.card #sq1090-conn').show('fast');
    };

    $('#timeline-slider').on('change', function (event) {
        if (ctx.timer != null)
            window.clearInterval(ctx.timer);
        ctx.data.reset();
        ctx.time = $(this).val();
        ctx.stream.seek(ctx.time);
        ctx.timer = window.setInterval(app_update_timeline, 100, ctx);
    });
});

function app_update(ctx, time, real_time=true) {
    let stream;

    const source = ctx.map.getSource('aircraft');
    const source_route = ctx.map.getSource('aircraft-route');
    if (!source || !source_route)
        return;

    ctx.time = time;

    stream = ctx.stream.read(real_time ? null : ctx.time);
    stream.forEach(data => {
        const time = data[0];
        const icao = data[1];
        const callsign = data[2].replace(/_+$/, '');
        const position = [data[3], data[4]];
        const altitude = data[5];
        ctx.data.add(icao, time, callsign, position, altitude);
    });

    ctx.data.clean(ctx.time - 60);
    update_aircraft_features(source, ctx);
    update_aircraft_route_features(source_route, ctx);

    pcard_info_update(ctx);
    ctx.selection.items().filter(icao => ctx.data.contains(icao)).forEach(icao => pcard_aircraft_update(ctx, icao));
    ctx.selection.items().filter(icao => !ctx.data.contains(icao)).forEach(icao => pcard_aircraft_update_missing(ctx, icao));
    timeline_update(ctx);
}

function app_update_real_time(ctx) {
    app_update(ctx, Date.now() / 1000);
}

function app_update_timeline(ctx) {
    $('#timeline-slider').val(ctx.time);
    app_update(ctx, ctx.time, false);
    ctx.time++;
    timeline_end(ctx);
}

function pcard_info_update(ctx) {
    const time = ctx.time;
    const td = time - ctx.data.last_time;
    const selected = ctx.selection.items().filter(icao => ctx.data.contains(icao)).length;
    const total = ctx.data.size();
    $('#panel-info-time td').text(time_str(time));
    $('#panel-info-time-delta td').text(td.toFixed(1));
    $('#panel-info-aircrafts td').text(selected + ' / ' + total);
}

function pcard_aircraft_update(ctx, icao) {
    const data = ctx.data.get(icao);
    const callsign = data['callsign'];
    const position = nth_last(data['position'], 1);
    const altitude = data['altitude'];
    const bearing = data['bearing'];
    const td = Math.round(ctx.time - data['time']);
    const progress = Math.round((1 - td / 60.0) * 100);
    const lv_label = 'Liveness: ' + td + ' sec.';
    const panel = $('#panel-info-aircraft');
    const card_id = 'aircraft-' + icao2str(icao);
    const jq_card_id = '#' + card_id;
    const card_exists = $('#' + card_id).length > 0;
    const height = panel.height();

    if (!card_exists)
        panel.append(
            '<div id="' + card_id + '" class="card border-secondary mb-2">'
            + '</div>'
        );

    $(jq_card_id).css('opacity', 1.0);
    $(jq_card_id).html(
        '<div class="card-header d-flex justify-content-between p-2">'
        + callsign
        + '<button type="button" class="btn-close" aria-label="Close"></button>'
        + '</div>'
        + '<div class="card-body p-2"><table>'
        + '<tr><td>icao:</td><td>' + icao2str(icao) + '</td></tr>'
        + '<tr><td>position:</td><td>' + position[0].toFixed(6) +'<br/>' + position[1].toFixed(6) + '</td></tr>'
        + '<tr><td>altitude:</td><td>' + altitude.toFixed(1) +'&nbsp;m.</td></tr>'
        + '<tr><td>bearing:</td><td>' + Math.round(bearing) +'&deg;</td></tr>'
        + '</table>'
        + '<div class="progress" role="progressbar" aria-label="' + lv_label + '" aria-valuenow="' + td + '" aria-valuemin="0" aria-valuemax="60"><div class="progress-bar" style="width: ' + progress + '%"></div></div>'
        + '</div>'
    );
    // preserve the 100% height
    panel.height(height);

    $(jq_card_id + ' > div > button.btn-close').on('click', function() {
        selection_clear(ctx, icao);
    });
    $(jq_card_id + ' > div.card-header').css('background-color', data['selection_color'] + '66');
}

function pcard_aircraft_update_missing(ctx, icao) {
    $('#aircraft-' + icao2str(icao)).css('opacity', 0.25);
}

function pcard_aircraft_clear(icao) {
    $('#aircraft-' + icao2str(icao)).remove();
}

function selection_add(ctx, icao) {
    selection_update(ctx, icao, true);
    pcard_aircraft_update(ctx, icao);
    pcard_info_update(ctx);
}

function selection_clear(ctx, icao) {
    selection_update(ctx, icao, false);
    pcard_aircraft_clear(icao);
    pcard_info_update(ctx);
}

function selection_update(ctx, icao, state) {
    const source = ctx.map.getSource('aircraft');

    if (state)
        ctx.selection.set(icao);
    else
        ctx.selection.unset(icao);

    ctx.map.setFeatureState({source: 'aircraft', id: icao}, {selected: state});
    source.updateData({
        update: [{
            id: icao,
            addOrUpdateProperties: [{key: 'selected', value: state}],
        }],
    });
}

function update_aircraft_features(source, ctx) {
    const features = ctx.data.items().map((v) => {
        const icao = v[0];
        const data = v[1];
        return {
            type: 'Feature',
            id: icao,
            geometry: {
                'type': 'Point',
                'coordinates': nth_last(data['position'], 1),
            },
            properties: {
                'icao': icao,
                'callsign': data['callsign'],
                'bearing': data['bearing'],
                'selected': ctx.selection.is_selected(icao),
                'selection-color': data['selection_color'],
            },
        };
    });
    source.setData({
        'type': 'FeatureCollection',
        'features': Array.from(features),
    });
}

function update_aircraft_route_features(source, ctx) {
    const features = ctx.data.items()
        .filter(v => ctx.selection.is_selected(v[0]))
        .map((v) => {
            const icao = v[0];
            const data = v[1];
            return {
                type: 'Feature',
                id: icao,
                geometry: {
                    'type': 'LineString',
                    'coordinates': data['position'],
                },
                properties: {
                    'icao': icao,
                    'selection-color': data['selection_color'],
                },
            };
        }
    );
    source.setData({
        'type': 'FeatureCollection',
        'features': Array.from(features),
    });
}

function icao2str(icao) {
    return '0x' + icao.toString(16);
}

function radians(deg) {
    return deg * (Math.PI / 180);
}

// from https://www.movable-type.co.uk/scripts/latlong.html
function geo_bearing(p1, p2) {
    const lon1 = radians(p1[0]);
    const lat1 = radians(p1[1]);
    const lon2 = radians(p2[0]);
    const lat2 = radians(p2[1]);
    const y = Math.sin(lon2 - lon1) * Math.cos(lat2);
    const x = Math.cos(lat1) * Math.sin(lat2)
        - Math.sin(lat1) * Math.cos(lat2) * Math.cos(lon2 - lon1);
    const theta = Math.atan2(y, x);
    return (theta * 180 / Math.PI + 360) % 360;
}

function* take_while(items, fn) {
    for (let item of items) {
        if (fn(item))
            yield item;
        else
            break;
    }
}

function nth_last(items, k) {
    return items[items.length - k];
}

function time_str(time, resolution='second') {
    const t = new Date(time * 1000).toISOString();
    let result;
    if (resolution == 'second')
        result = t.substring(11, 19);
    else if (resolution == 'minute')
        result = t.substring(11, 16);
    else
        throw 'Invalid resolution: ' + resolution;
    return result;
};

// vim: sw=4:et:ai
