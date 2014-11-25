%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<!DOCTYPE html>
<html>
<body>

<img src="http://img.wikinut.com/img/1mpdglbma_q7fudr/jpeg/724x5000/Ding.jpeg" alt="Ding" style="width:200px;height:100px">
<h1>Ding (Signed In Results)</h1>
%if user_email == '':
    <form name="signInForm" method="get" action="">
        <input type="submit" name="signInButton" value="signIn"/>
    </form>
%else:
    <h2> Hello {{user_email}} <h2>
%end
<form name="searchForm" action="" method="get">
  <input type="text" name="keywords"><br>
  <input value="Search It" id="searchButton" type="submit" />
</form>

<form name="signOutForm" method="get" action="">
    <input type="submit" name="signOutButton" value="signOut"/>
</form>

<h4>Results</h4>

<table border="1" id="results">
  <tr>
      <td>Word</td>
      <td>Count</td>
    </tr>
%if wordList is not None:
    %for key, value in wordList.iteritems():
        <tr>
            <td>{{key}} </td>
            <td>{{value}} </td>
        </tr>
    %end
%end
</table>

<h4>History</h4>

<table border="1" id="history">
  <tr>
      <td>Word</td>
    </tr>
%if popularWords is not None:
    %for key, value in enumerate(popularWords):
        <tr>
            <td>{{value}} </td>
        </tr>
    %end
%end
</table>

</body>
</html>