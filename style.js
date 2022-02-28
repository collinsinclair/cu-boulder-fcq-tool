function addBackGroundImage () {
    const head = document.querySelector("head")
    let backgroundStyleElement = document.createElement("style")
    backgroundStyleElement.innerHTML = `
body {
    background-image: url("images/cu-main-campus-aerial.jpg");
    background-repeat: no-repeat;
    background-size: cover;
    height: 100vh;
}
`
    head.append(backgroundStyleElement)
}

addBackGroundImage()