// i added this function inside the browser and run it in setInterval then i download the log from the console
// but i have the account to log in


function scrape() {
  let cards = [...document.querySelectorAll("li.membership-list-content-center-list-item")];
  for (let card of cards) {
    let title = card.querySelector(".membership-list-font-bold");
    title = title && title.innerText;

    let country = card.querySelector(
      ".membership-list-content-center-list-item-left-top-content-location > span"
    );
    country = country && country.innerText;

    let name = card.querySelector(".membership-list-content-center-list-item-left-bottom-name");
    name = name && name.innerText;

    let phone = card.querySelector(".membership-list-content-center-list-item-left-bottom-phone");
    phone = phone && phone.innerText;

    let email = card.querySelector(".membership-list-content-center-list-item-left-bottom-email");
    email = email && email.innerText;

    let data = {
      title: title,
      country: country,
      name: name,
      phone: phone,
      email: email,
    };
    console.log(data);
  }
}

setInterval((_) => {
  scrape();
  document.querySelector(".btn-next").click();
}, 1000);
