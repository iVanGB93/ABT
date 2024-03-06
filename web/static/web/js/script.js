let navbar = document.querySelector('.header .flex .navbar');
let navButton = document.querySelector('#menu-btn');

navButton.onclick = () => {
    navbar.classList.toggle('active');
}

window.onscroll = () => {
    navbar.classList.remove('active');

    if(window.scrollY > 0){
        document.querySelector('.header').classList.add('active');
    }else{
        document.querySelector('.header').classList.remove('active');
    }
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