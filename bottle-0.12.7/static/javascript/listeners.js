// GLOBAL VARIABLES
var last_page_num = 0


$('#searchForm').submit(function(ev) {
  ev.preventDefault(); // to stop the form from submitting
  var words = $('#searchForm :input[name=words]').val();
  triggerNewSearch(words);
});

$('#wrapper').on("click", ".pin-btn", function(ev) {
  ev.preventDefault(); // to stop the form from submitting
  var pinurl = $(this).attr('value');
  console.log('pinurl: '+pinurl);
  triggerNewPin(pinurl);
});

function triggerNewPin(pinurl){
  $.post("/pinurl", {pinurl: pinurl}, function(data){
    console.log("HELLO!!");
    console.log(data);
    if(data.statusCode == "false"){
      console.log('false');
      $('#pinForm').hide();
    }
    else
      alert('Try Pinning again');
  }, "json");
}

$(window).scroll(function() {
  if($(window).scrollTop() + $(window).height() == $(document).height()) {

    if ( (last_page_num >= 1) && ($('#no-results').val() == undefined) ){
      last_page_num+=1; // increase page number
      search($('#curent_words').val(), last_page_num, function(data){
        $("#results").append(data);
      });
    }
  }
});


$("#results").on({
  mouseenter: function() {
    var href = $(this).attr('href');
    $("#preview-box iframe").attr('src', href);
    $("#preview-box").show();
  },
  mouseleave: function() {
    $("#preview-box").hide();
  }
}, '.url-link');


$("#wrapper").on("click", "#recommended-words-btn", function() {
  var words = $(this).html();
  $('#searchForm :input[name=words]').val(words);
  triggerNewSearch(words);
});

function triggerNewSearch(words){
  $('#curent_words').val(words);
  last_page_num = 1; // after a fresh search, set page number to 1
  search(words, 1, function(data){
    $("#results").html(data);
    setupRecommendedWords();
  });
}


function search(words, page_num, cb){
  $.post( "/search", {words: words, page_num: page_num}, function(data){
    cb(data);
  }, "html");
}


function setupRecommendedWords(){
  val = $('#recommended-words').html();
  if (val == ""){
    $('#recommended-words-box').hide();
  }else{
    $('#recommended-words-box button').html(val);
    $('#recommended-words-box').show();
  }
}

