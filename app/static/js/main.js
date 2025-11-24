// Store token after login
function saveToken(token) {
    localStorage.setItem("jwt_token", token);
}

// Get token
function getToken() {
    return localStorage.getItem("jwt_token");
}

// Logout function
function logout() {
    localStorage.removeItem("jwt_token");
    window.location.href = "/login";
}
