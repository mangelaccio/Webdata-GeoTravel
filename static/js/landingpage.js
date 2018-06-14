//document.getElementById("demo").innerHTML = x;
var width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
var height = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
// backwards compatible to IE8
var image = "{{ url_for('images/background'+(Math.floor(8*Math.random())+1)+'.png') }}"
document.getElementById('bg').src=image;
