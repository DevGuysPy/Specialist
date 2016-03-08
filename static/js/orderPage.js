function initOrderPage(activityId){
    initChat(activityId);

    var sendMessageInp = $('#send-message-input');

    sendMessageInp.on('focusin', function(){
        $(this).parent().find('i').css('color', '#37474f')
    });

    sendMessageInp.on('focusout', function(){
        $(this).parent().find('i').css('color', 'white')
    });

    var messageBox = $('.message-box');
    messageBox.perfectScrollbar({suppressScrollX:!0});
    messageBox.scrollTop(messageBox.prop("scrollHeight"));
}

function initChat(activityId){
    var messageBox = $('.message-box');
    var input = $('#send-message-input');

    function refreshMessages(data) {

        messageBox.append(
            $(
                '<div class="message">' +
                    '<div class="row no-margin">' +
                        '<div class="col m1">' +
                            '<img src="' + data.author.img + '" alt="" ' +
                            'class="sender-img circle">' +
                        '</div>' +
                        '<div class="col m11 no-padding">' +
                            '<div class="message-content row no-padding">' +
                                '<div class="col m11">' +
                                    '<div class="message-title">' +
                                        '<p class="no-margin">' + data.author.name + '</p>' +
                                    '</div>' +
                                    '<p class="message-text">' + data.message +'</p>' +
                                '</div>' +
                                '<div class="message-time col m1">' +
                                    '<p class="no-margin">' + data.time + '</p>' +
                                '</div>' +
                                '<div class="divider"></div>' +
                            '</div>' +
                        '</div>' +
                    '</div>' +
                '</div>'
            )
        );

        messageBox.animate(
            { scrollTop: messageBox.prop("scrollHeight") }, 1000);

        input.val('');

    }

    socket.on("message", function (message) {
        refreshMessages(message);
    });

    socket.on('connect', function() {
        socket.emit('join', {room: 'order_' + activityId + '_room'});
    });

    function sendMessage(){
        if (!(input.val().trim())){
            return null;
        }

        socket.emit('message',
            {'message': input.val(),
                'room': 'order_' + activityId + '_room' });
    }

    input.keypress(function (e) {
        if (e.which == 13) {
            sendMessage()
        }
    });

    $('#send-message-btn').on('click', function(){
        sendMessage();
    });

}


