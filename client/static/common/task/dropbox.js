$(function () {$("#import-dropbox-button").click(function () {                      // DROPBOX

            var client = new Dropbox.Client({
                key: "jgkzlyd03c5dww1",
                rememberUser: true
            });

            var dropboxGetInfo = function(client) {
                client.getAccountInfo(function(error, accountInfo) {
                  if (error) {
                    return showError(error);
                  }
                  console.log(accountInfo);                     // !!!! ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ
                });

                var path = "/";
                var nextPath = path;
                var entr = [];

                var readDir = function(path) {
                  return new Promise(function(resolve, reject) {
                    client.readdir(path, function(error, entries) {
                      if (error) {
                        return reject(error);
                      }
                      if (entries) {
                        return Promise.all(entries.map(function(item, i, arr) {
                          entr.push(path + entries[i]);
                          nextPath = path;
                          nextPath += item + '/';
                          return readDir(nextPath);
                        })).then(resolve)
                        .catch(reject);
                      } else {
                        return resolve();
                      }
                    });
                  }) 
                };



                readDir(nextPath).then(function() {
                  console.log(entr);                     // !!!! ВОТ ЭТО МАССИВ С ФАЙЛАМИ
                })
                .catch(function(err) {
                  console.log(err);
                });
            }

          
                dropboxGetInfo();
               
        });
});
