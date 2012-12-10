var interval = 1000 * 60 * 5; //5 Minutes
function update() {
    $.getJSON('/update', function(data) {
        if (data.amount != 0){
            var html = '';

            for (var i = 0; i < data.amount; i++){
                html += '<li class="wrap-event '+ data.events[i].service + '"><div>' + data.events[i].html +'</div></li>';
            };
            $('#brook').prepend(html);
            $('.timestamp').timeago();
        };
    });
};

$(document).ready(function() {
    $('.timestamp').timeago()
    setInterval(update, interval)
});