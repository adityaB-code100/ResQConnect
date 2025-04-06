

a="/service"
  const sentences = [
    { text: "Emergency assistance at your fingertips", href: a },
    { text: "Stay safe, we are here to help", href: a},
    { text: "Call 1091 for Women Helpline", href: a },
    { text: "In case of fire, dial 101 immediately", href: a },
    { text: "Help is just a call away", href: a }
  ];

  let index = 0;
  const container = document.getElementById("floatingSentence");

  function scrollSentence() {
    const { text, href } = sentences[index];
    container.innerHTML = `<a href="${href}" target="_blank">${text}</a>`;
    const link = container.querySelector("a");

    let leftPos = window.innerWidth;
    link.style.left = leftPos + "px";

    function animate() {
      leftPos -= 1;
      link.style.left = leftPos + "px";

      if (leftPos + link.offsetWidth > 0) {
        requestAnimationFrame(animate);
      } else {
        index = (index + 1) % sentences.length;
        setTimeout(scrollSentence, 500);
      }
    }

    animate();
  }

  scrollSentence();



  //card

  window.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".card");

    cards.forEach((card, index) => {
      setTimeout(() => {
        card.style.opacity = "1";
        card.style.transform = "translateY(0)";
      }, index * 1000); // Delay each card
    });
  });
