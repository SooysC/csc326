% include('header.tpl', title='PinBoard')

<div id='wrapper'>
  %for index, (url, title) in enumerate(pins):
    <div class="panel panel-info">

      <div class="panel-heading">
        <h3 class="panel-title">
          <a class="url-link" href="{{url}}" target="_blank">
            {{title}}
          </a>
        </h3>
      </div>
    </div>
  %end
</div>
