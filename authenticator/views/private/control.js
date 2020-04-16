let record;

$(document).ready(function(){
  getKerb().then(showGreeting);
  $('#username-box').keyup(function(event) {
    if (event.keyCode === 13) {
      $('#btn-submit').click();
    }
  });
  refresh();
});

function refresh() {
  getRecord().then(function(result) {
    if (typeof(result) == 'object') { // successfuly found record
      record = result;
      showError('');
      showExistingRegistration(true);
    } else {
      if (result == 404) { // could not find record
        showError('');
        showNewRegistration(true);
      } else { // something else went wrong
        showError("Something went wrong on the server");
      }
    }
  });
}

function insertMCUsername(username) {
  $('#mc-username').text(username);
}

function showElement(selector, show) {
  if (show) {
    $(selector).show();
  } else {
    $(selector).hide();
  }
}

function showNewRegistration(show) {
  showSubmissionForm(show);
  showElement('#new-registration', show);
}

function showExistingRegistration(show) {
  insertMCUsername(record.username);
  showNewRegistration(false);
  showElement('#existing-registration', show);
}

function showSubmissionForm(show) {
  const selector = '#submission-form';
  showElement(selector, show);
  $('#username-box').focus();
}

function showGreeting(kerb) {
  const selector = '#greeting';
  $(selector).text('Hello ' + kerb);
  showElement(selector, true); // always greet the user :)
}

function highlightInput() {
  const selector = '#username-box';

  $(selector).val('');
  $(selector).focus();
  //$(selector).on("click", () => {
  //  $(this).select();
  //});
}

function showError(msg) {
  const selector = '#error-container';
  $(selector).text(msg);
}

function getKerb() {
  return fetch('/users/get_kerb')
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.log(data);
      return data['kerberos'];
      //showGreeting(data['kerberos']);
    });
}

/*
 * Returns a promise that upon fulfillment, indicates whether username is
 * a valid Minecraft username
 */
function checkUsername(username) {
  return fetch('/users/check_username', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({username})
  })
    .then((response) => {
      return response.json();
    })
    .then ((data) => {
      return data.status;
    })
    .catch((err) => {
      showError("Server error while trying to check username");
    });
}

function addRecord(username) {
  return fetch('/users/add_record', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({username})
  })
    .then((response) =>{
      const statusCode = response.status;
      if (statusCode != 200) {
        if (statusCode == 400) {
          showError("This MC username is already in the system");
        } else {
          showError("Server error");
        }
      } else {
        refresh();
        //showExistingRegistration(true);
      }
    });
}

function submitUsername() {
  const inputSelector = "#username-box";
  const username = $(inputSelector).val();
  if (username.length < 3 || username.length > 16) {
    showError("Minecraft usernames must be between 3 and 16 characters");
    return
  }
  checkUsername(username).then(function(status) {
    if (status) {
      addRecord(username);
    } else {
      showError("Invalid username");
      highlightInput();
    }
  });
}

/*
 * Gets user record from server, returns either the record object or a status 
 * code number if an error occurs
 */
function getRecord() {
  return fetch('/users/find_record')
    .then((response) => {
      const statusCode = response.status;
      console.log(statusCode);
      if (statusCode != 200) {
        return {status: statusCode};
      }
      else {
        return {res: response.json(), status:statusCode};
      }
    })
    .then((data) => {
      if (data.status != 200) {
        return data.status;
      }
      return data.res; // json promise obj
    })
    .then((result) =>{
      console.log(result);
      return result;
    });
}
