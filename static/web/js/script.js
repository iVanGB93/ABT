let navbar = document.querySelector('.header .flex .navbar');

document.querySelector('#menu-btn').onclick = () => {
    console.log("CLICK");
    navbar.classList.toggle('active');
}

window.onscroll = () => {
    navbar.classList.remove('active');
}

document.querySelectorAll('input[type="number"]').forEach(inputNumber => {
    inputNumber.oninput = () => {
        if(inputNumber.ariaValueMax.length > inputNumber.maxLength) inputNumber.ariaValueMax
        = inputNumber.ariaValueMax.slice(0, inputNumber.maxLength);
    };
});

AOS.init({
    duration: 400,
    delay:200,
});