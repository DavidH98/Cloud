function showCard(cardName) {
    var loginCard = document.getElementById('login-card');
    var signupCard = document.getElementById('signup-card');
    var resetCard = document.getElementById('reset-card');

    if (cardName === 'login') {
        loginCard.hidden = false;
        signupCard.hidden = true;
        resetCard.hidden = true;
    }
    else if (cardName === 'signup') {
        loginCard.hidden = true;
        signupCard.hidden = false;
        resetCard.hidden = true;
    } else if (cardName === 'forgot') {
        loginCard.hidden = true;
        signupCard.hidden = true;
        resetCard.hidden = false;
    }
}

function togglePasswordVisibility() {
    var passwordInput = document.getElementById('password');
    var toggleButton = document.querySelector('.toggle-password');

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleButton.textContent = '';
        toggleButton.innerHTML = "<span class=\"mdi mdi-eye-outline\"></span>"
    } else {
        passwordInput.type = 'password';
        toggleButton.textContent = 'Show';
        toggleButton.innerHTML = "<span class=\"mdi mdi-eye-off-outline\"></span>"
    }
}