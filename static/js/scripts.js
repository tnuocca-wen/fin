document.getElementById('selection-form').addEventListener('submit', function(event) {
    event.preventDefault();
    formdata = new FormData(this);
    fetch(this.action, {
        method: 'POST',
        body: new FormData(this),
    })
    .then(response => response.json())
    .then(data => {
        if (data.errors) {
            // Handle form validation errors
            console.log(data.errors);
        } else {
            // Handle form submission success
            console.log(data.message);
        }
    })
    .catch(error => {
        // Handle any network or server errors
        console.log(formdata)
        console.error(error);
    });
});