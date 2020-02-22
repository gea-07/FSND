if (document.getElementById('new_venue_form') != null)
{
    document.getElementById('new_venue_form').onsubmit = function(e) {
        e.preventDefault()
        console.log(document.getElementById('genres'))
        fetch('/venues/create', {
            method: 'POST',
            body: JSON.stringify({
            "name": document.getElementById('name').value,
            "city": document.getElementById('city').value,
            "state": document.getElementById('state').value,
            "address": document.getElementById('address').value,
            "phone": document.getElementById('phone').value,
            "facebook_link": document.getElementById('facebook_link').value,
            "website": document.getElementById('website').value,
            "seeking_talent": true,
            "seeking_description": document.getElementById('seeking_description').value,
            "genres": document.getElementById('genres').value,
            "image_link": document.getElementById('image_link').value,
            }),
            headers: {
            'Content-Type': 'application/json'
            }
        })
    }
}