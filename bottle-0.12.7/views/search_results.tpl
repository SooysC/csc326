<div hidden id="recommended-words">{{recommended_words}}</div>

%for index, url in enumerate(url_list):
  <div class="panel panel-info">

    <div class="panel-heading">
      <h3 class="panel-title">
        <a class="url-link" href="{{url}}" target="_blank">
          {{url[:65] + (url[65:] and '..')}}
        </a>
      </h3>
    </div>
    <div class="panel-body">
      body..
    </div>
  </div>
%end
