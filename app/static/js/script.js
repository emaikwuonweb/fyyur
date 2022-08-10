window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

btn = document.getElementById('del-btn')
btn.addEventListener('click', function(e) {
  id = parseInt(e.target.getAttribute('data-id'))
  fetch(`/venues/${id}`, {
    method: "DELETE",
    body: JSON.stringify({venue_id: id}),
    headers: {'Content-Type': 'application/json'}
  }).then(res => res.json()).then(data => {
    if(data.success) window.location = '/'
  })
})