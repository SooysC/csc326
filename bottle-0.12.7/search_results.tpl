%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<!DOCTYPE html>
<html>
    
<body>

<h1>Ding</h1>

<h4>Search Results</h4>

<script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>

<table border="1" id="results">
%for index, url in enumerate(url_list):
    <tr>
        <td>{{url}} </td>
        <td><a href="{{url}}" target="_blank">Open Link in new tab</a></td>
    </tr>	
%end
</table>
% if page_num < num_pages:
<form name="" method="get" action="">
    <button type="submit" name="next" value="{{page_num + 1}}">Next</button> 
    <!--input type="submit" name="next" value=""/-->
</form>
%end

% if page_num > 1:
<form name="" method="get" action="">
    <button type="submit" name="prev" value="{{page_num - 1}}">Previous</button> 
    <!--input type="submit" name="prev" value="Prev"/-->
</form>
%end

<form name="" method="get" action="">
    <button type="submit" name="home" value="">Home</button> 
    <!--input type="submit" name="prev" value="Prev"/-->
</form>

</body>
</html>