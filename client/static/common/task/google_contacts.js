$(function () {
	$('#import-google-contacts-button').click(function (e) {console.log('work');auth();});
	function auth() {
        var config = {
          'client_id': '568857370517-3o2p62a82f1s6pkm3eq1s30kga9ull45.apps.googleusercontent.com',
          'scope': 'https://www.google.com/m8/feeds'
        };
        gapi.auth.authorize(config, function() {
          fetch(gapi.auth.getToken());
        });
      };
      function fetch(token) {
        $.ajax({
          url: 'https://www.google.com/m8/feeds/contacts/default/full?alt=json',
          dataType: 'jsonp',
          data: token
        }).done(function(data) {
            console.log(JSON.stringify(data));
          });
      };
});
