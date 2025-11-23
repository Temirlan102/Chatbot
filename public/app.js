const tg = window.Telegram.WebApp;
tg.expand();

document.getElementById("loadSlots").onclick = async () => {
  const res = await fetch("http://localhost:3000/slots");
  const slots = await res.json();

  const list = document.getElementById("slotList");
  list.innerHTML = "";

  slots.forEach((slot) => {
    const li = document.createElement("li");
    li.textContent = `${slot.date} ${slot.time}`;

    li.onclick = async () => {
      await fetch("http://localhost:3000/book", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          slotId: slot.id,
          user: tg.initDataUnsafe.user.id,
        }),
      });

      tg.showAlert("Booked!");
    };

    list.appendChild(li);
  });
};
