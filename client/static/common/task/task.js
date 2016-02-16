/**
 * Created by root on 5.12.15.
 */
$(function () {
	
    var baseUrl = 'https://www.todoist.com/API/v6';

    $('#import-todo-button').click(function (e) {
        swal({
            title: "login",
            text: "Enter todoist Login",
            type: "input",
            showCancelButton: true,
            closeOnConfirm: false,
            animation: "slide-from-top",
            inputPlaceholder: "demeshko.alexander.v@gmail.com"
        }, function (login) {
            if (login === false) return false;
            if (login === "") {
                swal.showInputError("You need to write something!");
                return false
            }
            swal({
                title: "password",
                text: "Enter todoist Password",
                type: "input",
                showCancelButton: true,
                closeOnConfirm: false,
                animation: "slide-from-top",
                inputPlaceholder: "wdv11lol"
            }, function (password) {
                if (password === false) return false;
                if (password === "") {
                    swal.showInputError("You need to write something!");
                    return false
                }
                request(baseUrl + '/login?email=' + login + '&password=' + password, function (data) {
                    if (!JSON.parse(data)) alert("Auth failed");
                    var token = JSON.parse(data).api_token;
                    if (!token) alert("Auth failed");
                    else request(baseUrl + '/sync?seq_no=0&resource_types=["all"]&token=' + token, function (data) {
                        if (!JSON.parse(data)) {
                            alert("failed reriving data")
                            return;
                        }
                        var write = confirm("Write in Memory? (downloadJs on reject)");
                        if (write) {
                            convert(JSON.stringify(JSON.parse(data)), function (a) {
                                swal(a)
                            })
                        } else {
                            var downloadLink = document.createElement('a');
                            downloadLink.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(data));
                            downloadLink.setAttribute('download', 'todoist.json');
                            document.body.appendChild(downloadLink);
                            downloadLink.click();
                            document.body.removeChild(downloadLink);
                            $('#history-item-langs a')[1].click();
                        }
                    })
                });
                return true;
            });
        });
    });

    function request(url, callback) {
        $.ajax({
            url: '/todo',
            type: "POST",
            data: {
                url: url
            },
            success: function (data) {
                callback(data);
            }
        });
    }

    function convert(data, c) {
        $.ajax({
            url: '/write',
            type: "POST",
            data: {
                json: data,
                service: 'todoist'
            },
            success: function (data) {
                c(data);
            }
        });
    }

});
