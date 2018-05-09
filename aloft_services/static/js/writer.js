var writing_start_time = Date.now();
var last_load_stats = {
    'words': 0,
    'characters': 0
};

var last_keystroke_time = Date.now();
var currently_writing = false;
var anything_added = false;

const writing_stop_autosave_time = 15; // seconds
const always_autosave_time = 300; // seconds

async function save_data() {
    var filename = $('#filename').val();
    if(!filename) return;

    var data = writing_data();

    var resp = await fetch(
        '/writing/latest/'+filename,
        { method: 'POST', body: data }
    );

    const decoder = new TextDecoder("utf-8");
    var r = await resp.body.getReader().read();
    var data = decoder.decode(r.value);

    $(".rendered").html(data);

    load_history(filename);
    current = false;
}

function writing_data() {
    var d = $('#writing-data').val();
    if(!d) return '';
    return d;
}

/* get number of characters in text area */
function charcount() {
    return writing_data().length;
}

/* get number of words in text area */
function wordcount() {
    var matches = writing_data().match(/\w\w+/g);
    if(!matches) return 0;
    return matches.length;
}

/* update word counter displays */
function update_counts() {
    $('#wordcount').text(wordcount().toString());
    $('#charcount').text(charcount().toString());
}

function keypress_callback() {
    update_counts();
    last_keystroke_time = Date.now();
    currently_writing = true;
    anything_added = true;
}

/* because JS apparently does not supply sane and simple number formatting methods? */
function number_to_2digits(v) {
    if(v < 10) return '0'+v.toString();
    return v.toString();
}

/* update time counter displays */
function update_time() {
    var now = Date.now();

    var elapsed = Math.floor((now - writing_start_time) / 1000);

    var elapsed_hrs = Math.floor(elapsed / 3600);
    var elapsed_mins = Math.floor((elapsed % 3600) / 60);
    var elapsed_secs = Math.floor(elapsed % 60);

    var time_str = number_to_2digits(elapsed_mins)+':'+number_to_2digits(elapsed_secs);
    if(elapsed_hrs > 0) time_str = number_to_2digits(elapsed_hrs)+':'+time_str;

    $("#elapsed-time").text(time_str);

    var words_added = wordcount() - last_load_stats['words'];
    var chars_added = charcount() - last_load_stats['characters'];

    $('#words-added').text(words_added.toString());

    var avg_words = (words_added / (elapsed / 60)).toPrecision(3);
    var avg_chars = (chars_added / (elapsed / 60)).toPrecision(3);

    $("#avg-wpm").text(avg_words.toString());
    $("#avg-cpm").text(avg_chars.toString());

    if(currently_writing && anything_added) {
        var write_stop_elapsed = Math.floor((now - last_keystroke_time) / 1000);
        var time_to_ws_autosave = writing_stop_autosave_time - write_stop_elapsed;
        if(write_stop_elapsed >= writing_stop_autosave_time) {
            save_data();
            last_keystroke_time = now;
            currently_writing = false;
        }

        var width_pct = Math.floor((time_to_ws_autosave / writing_stop_autosave_time).toPrecision(2) * 100);
        $('.autosave-timer, .autosave-timer-bar').show();
        $('#writing-stop-timer').width(width_pct.toString()+'%').attr('aria-valuenow', width_pct.toString()).text(
            Math.floor(time_to_ws_autosave).toString()+' seconds to autosave...'
        );
    } else {
        $('#writing-stop-timer').width('0%');
        $('.autosave-timer, .autosave-timer-bar').hide();
    }
}

/* load a file/version of a file from the server */
async function load_writing(filename, version) {
    const decoder = new TextDecoder("utf-8");

    var when = 'latest/'
    if(version != undefined) {
        when = 'past/'+version.toString()+'/';
    }

    var resp = await fetch('/writing/raw/'+when+filename);
    var data = await resp.body.getReader().read();
    data = decoder.decode(data.value);

    $('#writing-data').val(data);

    var resp2 = await fetch('/writing/'+when+filename);
    var data2 = await resp2.body.getReader().read();
    data2 = decoder.decode(data2.value);

    $(".rendered").html(data2);

    update_counts();
    last_load_stats = {
        'words': wordcount(),
        'characters': charcount()
    }

    anything_added = false;
}

/* callback for the version load buttons */
async function load_version_callback(filename, version) {
    $('#history-select-'+version.toString()).addClass('btn-striped');
    $('.history-select-btn').removeClass('active');
    $('#history-select-'+version.toString()).addClass('active');

    await load_writing(filename, version);
    $('#history-select-'+version.toString()).removeClass('btn-striped');
}

/* load a file's history */
async function load_history(filename) {
    var resp = await fetch('/writing/info/'+filename);
    var history = (await resp.json()).reverse();

    $('.history-select').empty();
    for(let tag of history) {
        console.log("Found tag: "+tag.tag+" with version "+tag.version.toString());
        let commit_date = new Date(tag.committed);
        let version = parseInt(tag.version, 10);

        $('<a></a>')
            .attr('id', 'history-select-'+version.toString())
            .text('Version '+version.toString()+': '+commit_date.toLocaleString())
            .addClass('list-group-item list-group-item-action history-select-btn')
            .click(load_version_callback.bind(this, filename, version))
            .appendTo('.history-select');
    }
}

/* Saves content in text area */
async function save_callback(ev) {
    ev.preventDefault();

    save_data();
}

/* Loads content into text area */
async function load_callback(ev) {
    ev.preventDefault();

    var filename = $('#filename').val();
    await load_writing(filename);
    await load_history(filename);
}

$(function() {
    $("#load-button").click(load_callback);
    $("#save-button").click(save_callback);

    $('#writing-data').keypress(keypress_callback);
    update_counts();

    writing_start_time = Date.now();

    setInterval(update_time, 250);
})
