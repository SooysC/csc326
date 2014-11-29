% include('header.tpl', title='Page Title')

  <div id="wrapper">
    <p hidden id="curent_words"></p>
    <div class="left-column">
      <div hidden id="recommended-words-box" class="alert alert-warning" role="alert">
        Do you mean <button id="recommended-words-btn" type="button" class="btn btn-warning btn-xs"></button> ?
      </div>
      <div id="results">
      </div>
    </div>
    <div class="right-column">
      <div id="preview-box">
        <iframe src=""></iframe>
      </div>
    </div>
  </div>

% include('footer.tpl')
