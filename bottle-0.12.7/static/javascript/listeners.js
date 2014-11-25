
$('#searchForm').submit(function(ev) {
    ev.preventDefault(); // to stop the form from submitting
    var words = $('#searchForm :input[name=words]').val()
    search(words);
});


function search(words){
  $.post( "/search", { words: words}, function( data ) {
    $("#results").html(data);
  }, "html");
}