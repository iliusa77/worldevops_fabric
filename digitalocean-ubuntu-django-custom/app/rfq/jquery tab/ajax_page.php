
<?php
	include('dbcon.php');
	
	$result = mysql_query("SELECT * FROM descriptions where page_type = ".$_REQUEST['id']." order by id desc");
	while ($row = mysql_fetch_array($result))
	{?>
	  <label><?php echo $row['heading'];?></label>
	  <br />
	  <p>
	   <img src="99.jpg" alt="" style="float:left; margin-right:10px;" />
	  <?php echo $row['text'];?>
	  </p>
	<?php
	}?>
