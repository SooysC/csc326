// GLOBAL VARIABLES
var last_page_num = 0

$('#searchForm').submit(function(ev) {
  ev.preventDefault(); // to stop the form from submitting
  var words = $('#searchForm :input[name=words]').val();
  $('#curent_words').val(words);
  last_page_num = 1; // after a fresh search, set page number to 1
  search(words, 1, function(data){
    $("#results").html(data);
  });
});


$(window).scroll(function() {
  if($(window).scrollTop() + $(window).height() == $(document).height()) {

    if ( (last_page_num >= 1) && ($('#no_results').val() == undefined) ){
      last_page_num+=1; // increase page number
      search($('#curent_words').val(), last_page_num, function(data){
        $("#results").append(data);
      });
    }
  }
});


//$("#results").on({
  //'mouseenter', 'a', function() {
  //console.log("hello");
  //var href = $(this).attr('href');
  //console.log(href);
//});


$("#results").on({
  mouseenter: function () {
    var href = $(this).attr('href');
    $("#preview-box iframe").attr('src', href,
      $("#preview-box").show()
    );
  },
  mouseleave: function () {
    $("#preview-box").hide()
  }
}, '.url-link');


function search(words, page_num, cb){
  $.post( "/search", { words: words, page_num: page_num}, function(data){
    cb(data)
  }, "html");
}

