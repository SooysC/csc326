%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<!DOCTYPE html>
<html>

<head>
<link rel="stylesheet" type="text/css" href="bootstrap.css"/>
</head>

<body>
<img src="http://img.wikinut.com/img/1mpdglbma_q7fudr/jpeg/724x5000/Ding.jpeg" alt="Ding">
<h1>Ding (Homepage)</h1>
<form name="searchForm" action="" method="get">
  <input type="text" name="keywords"><br>
  <button type="submit" id="searchButton" value="">Search</button>
  <!--input value="Search It" id="searchButton" type="submit" /-->
</form>
%if user_email == '':
  <form name="signInForm" method="get" action="">
    <!--input type="submit" name="signInButton" value="signIn"/-->
    <button type="submit" id="signInButton" name="signInButton" value="signIn">Sign in</button>
  </form>
%else:
  <h2> Hello {{user_email}} <h2>
  <form name="signOutForm" method="get" action="">
        <button type="submit" id="signOutButton" name="signOutButton" value="signOut">Sign Out</button>
    </form>
%end
</body>
</html>
