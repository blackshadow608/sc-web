  $(function(){
         var CLIENT_ID = '568857370517-3o2p62a82f1s6pkm3eq1s30kga9ull45.apps.googleusercontent.com';

      var SCOPES = ['https://www.googleapis.com/auth/tasks.readonly'];

      /**
       * Check if current user has authorized this application.
       */
      function checkAuth() {
        gapi.auth.authorize(
          {
            'client_id': CLIENT_ID,
            'scope': SCOPES.join(' '),
            'immediate': true
          }, handleAuthResult);
      }

      $('#import-google-tasks-button').click(function (e) {handleAuthClick(e);});

      /**
       * Handle response from authorization server.
       *
       * @param {Object} authResult Authorization result.
       */
      function handleAuthResult(authResult) {
        var authorizeDiv = document.getElementById('authorize-div');
        if (authResult && !authResult.error) {
          // Hide auth UI, then load client library.
          authorizeDiv.style.display = 'none';
          loadTasksApi();
        } else {
          // Show auth UI, allowing the user to initiate authorization by
          // clicking authorize button.
          authorizeDiv.style.display = 'inline';
        }
      }

      /**
       * Initiate auth flow in response to user clicking authorize button.
       *
       * @param {Event} event Button click event.
       */
      function handleAuthClick(event) {
        gapi.auth.authorize(
          {client_id: CLIENT_ID, scope: SCOPES, immediate: false},
          handleAuthResult);
        return false;
      }

      /**
       * Load Google Tasks API client library.
       */
      function loadTasksApi() {
        gapi.client.load('tasks', 'v1', listTaskLists);
      }

      /**
       * Print task lists.
       */
      function listTaskLists() {
        var request = gapi.client.tasks.tasklists.list({
            'maxResults': 10
          });

          request.execute(function(resp) {
            appendPre('Task Lists:');
            var taskLists = resp.items;
            if (taskLists && taskLists.length > 0) {
              for (var i = 0; i < taskLists.length; i++) {
                var taskList = taskLists[i];
                appendPre(taskList.title + ' (' + taskList.id + ')');
              }
            } else {
              appendPre('No task lists found.');
            }
          });
      }

      /**
       * Append a pre element to the body containing the given message
       * as its text node.
       *
       * @param {string} message Text to be placed in pre element.
       */
      function appendPre(message) {
        console.log(message);
      }
  });// Your Client ID can be retrieved from your project in the Google
      // Developer Console, https://console.developers.google.com
 