<?php
// Database connection
$servername = "localhost";
$username = "root";  // Your MySQL username
$password = "";      // Your MySQL password (leave blank if using XAMPP with no password set)
$dbname = "highway_ticketing";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Initialize error messages
$email_error = '';
$password_error = '';

// Check if form is submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Retrieve and sanitize form inputs
    $first_name = $conn->real_escape_string($_POST['first_name']);
    $last_name = $conn->real_escape_string($_POST['last_name']);
    $email = $conn->real_escape_string($_POST['email']);
    $mobile_no = $conn->real_escape_string($_POST['mobile_no']);
    $password = $conn->real_escape_string($_POST['password']);
    $confirm_password = $conn->real_escape_string($_POST['confirm_password']);
    $entrance_location = $conn->real_escape_string($_POST['entrance_location']);

    // Check if passwords match
    if ($password !== $confirm_password) {
        $password_error = "Passwords do not match!";
    }

    // Check if the email already exists in the database
    $check_email_query = "SELECT * FROM admin_signup WHERE email = '$email'";
    $result = $conn->query($check_email_query);

    if ($result->num_rows > 0) {
        $email_error = "This email is already registered. Please use another one!";
    } 

    // If no errors, proceed to insert the data
    if (empty($email_error) && empty($password_error)) {
        // Encrypt the password
        $hashed_password = password_hash($password, PASSWORD_BCRYPT);

        // Insert data into the database
        $sql = "INSERT INTO admin_signup (first_name, last_name, email, mobile_no, password, entrance_location) 
                VALUES ('$first_name', '$last_name', '$email', '$mobile_no', '$hashed_password', '$entrance_location')";

        if ($conn->query($sql) === TRUE) {
            // Redirect to the specified page upon successful signup
            header("Location: http://localhost/Number%20Plate%20System/signup_successful.html");
            exit(); // Make sure to exit after redirection
        } else {
            echo "Error: " . $sql . "<br>" . $conn->error;
        }
    } else {
        // Include the signup.html file to show errors
        include('signup.html');
    }
} else {
    // If the form is not submitted, include the signup.html
    include('signup.html');
}

// Close connection
$conn->close();
?>
