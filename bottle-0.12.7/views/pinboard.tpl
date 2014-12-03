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
      <div class="panel-body">
        %if user_email != '':
            <form name="unpinForm" class="navbar-form navbar-left" method="post" action="unpinurl">
              <button type="submit" id= "unpinButton "name="unpinButton" class="btn btn-warning" value="{{url}}">Unpin It</button>
            </form>
        %end
      </div>
    </div>
  %end
</div>
