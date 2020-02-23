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

/*delete venue*/ 
const deleteBtns = document.querySelectorAll('.venue_delete_button');
for (let i = 0; i < deleteBtns.length; i++) {
    const btn = deleteBtns[i];
    btn.onclick = function(e) {
        const venueID = e.target.dataset['id'];
        fetch('/venues/'+venueID,{
            method: 'DELETE'
        })
        .then(function() {
            const item = e.target.parentElement;
            item.remove();
        })
    }
}