<div hidden id="recommended-words">{{recommended_words}}</div>
          
%for index, (url, title) in enumerate(url_list):
  <div class="panel panel-info">

    <div class="panel-heading">
      <h3 class="panel-title">
        <a class="url-link" href="{{url}}" target="_blank">
          {{title}}
        </a>
      </h3>
    </div>
    <div class="panel-body">
      body..
      
      %if user_email != '':      
      <form id="pinForm" class="navbar-form navbar-left" method="post" action="pinurl">
        <input type="hidden" name="pinurl" class="form-control" value="{{url}}">
        <button type="submit" id="pinButton" class="btn btn-warning" >Pin it!</button>
      </form>
      %end
      
    </div>
  </div>
%end
