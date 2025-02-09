// Signup form submission
document.getElementById('signup-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
  
    // Simple client-side validation
    if (password !== confirmPassword) {
      alert('Passwords do not match!');
      return;
    }
  
    // You can add AJAX call to send data to the server here.
    // For now, let's log the data to the console
    console.log('Signup Info:', { username, email, password });
  
    alert('Signup successful!');
  });
  
  // Login form submission
  document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
  
    // Simple client-side validation
    if (!email || !password) {
      alert('Please fill in both fields!');
      return;
    }
  
    // You can add AJAX call to validate login here.
    // For now, let's log the data to the console
    console.log('Login Info:', { email, password });
  
    alert('Login successful!');
  });
  