function addNavbar() {
    let body = document.querySelector("body")
    let navbarHTML = `
<div class="container-fluid">
    <a class="navbar-brand" href="./index.html">CU Boulder FCQ Tool</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
            aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">

            <li class="nav-item">
                <a class="nav-link active" aria-current="page" href="./index.html">Home</a>
            </li>

            <li class="nav-item">
                <a class="nav-link active" aria-current="page" href="./info.html">Stats</a>
            </li>

            <li class="nav-item">
                <a class="nav-link disabled" href="#">My Schedules</a>
            </li>

        </ul>
        <button class="d-flex btn btn-primary" type="button" id="log-in-sign-up">
            Log In | Sign Up
        </button>
    </div>
</div>
`
    const navbarElement = document.createElement("nav")
    navbarElement.classList.add("navbar", "navbar-expand-lg", "navbar-light", "bg-light")
    navbarElement.innerHTML = navbarHTML
    body.prepend(navbarElement)
}

addNavbar()