const textElements = document.getElementsByClassName('hover-text');

function displayText(index) {
    for (let i = 0; i < textElements.length; i++) {
        if (i === index) {
            textElements[i].style.display = 'block';
        } else {
            textElements[i].style.display = 'none';
        }
    }
}

function hideText() {
    for (let i = 0; i < textElements.length; i++) {
        textElements[i].style.display = 'none';
    }
}