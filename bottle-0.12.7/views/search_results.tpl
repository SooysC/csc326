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
      %if user_email != '':
          <button type="submit" name="pinButton" class="btn btn-warning pin-btn" value="{{url}}">Pin It</button>
      %end
    </div>
  </div>
%end
