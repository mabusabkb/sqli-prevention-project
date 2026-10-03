<?php

include 'connect.php';

?>


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" type="text/css" href="style3.css">
    <title>User's Data</title>
</head>
<body>
    <div class="heading">
        <p>User's Data</p>
    </div>
    <div class="table-div">
        <table class="table">
            <thead>
              <tr>
                <th scope="col">Id</th>
                <th scope="col">Username</th>
                <th scope="col">Email</th>
                <th scope="col">Gender</th>
                <th scope="col">Operation's</th>
              </tr>
            </thead>
            <tbody>

            <?php
            
             // Use prepared statement for consistency (no user input here, but good practice)
             $stmt = mysqli_prepare($conn, "SELECT id, username, email, gender FROM `users`");
             
             if ($stmt) {
                 mysqli_stmt_execute($stmt);
                 $result = mysqli_stmt_get_result($stmt);
                 
                 if($result) {
                   while($row = mysqli_fetch_assoc($result)) {
                     $id = $row['id'];
                     $uname = htmlspecialchars($row['username']);
                     $email = htmlspecialchars($row['email']);
                     $gender = htmlspecialchars($row['gender']);
                     echo '<tr>
                             <th scope="row">'.$id.'</th>
                             <td>'.$uname.'</td>
                             <td>'.$email.'</td>
                             <td>'.$gender.'</td>
                             <td>
                              <a href="update.php?updateid='.$id.'"><button class="btn-primary">Update</button></a>
                              <a href="delete.php?deleteid='.$id.'"><button class="btn-secondary">Delete</button></a>
                             </td>
                           </tr>';
                   }
                 } else {
                     error_log("Query execution error in show_users.php: " . mysqli_stmt_error($stmt));
                     echo '<tr><td colspan="5">An error occurred while loading users.</td></tr>';
                 }
                 
                 mysqli_stmt_close($stmt);
             } else {
                 error_log("Statement preparation error in show_users.php: " . mysqli_error($conn));
                 echo '<tr><td colspan="5">An error occurred while loading users.</td></tr>';
             }
             
             mysqli_close($conn);

            ?>
            
            </tbody>
          </table>
    </div>
    <center>
        <div class="back">
            <a href="admin_page.html" class="btn">Back</a>
        </div>
    </center>
</body>
</html>
